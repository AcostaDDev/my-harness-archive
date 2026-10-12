"""Migración controlada H2.5 de un checkout legacy a modo gestionado.

Entrada de biblioteca explícita, sin API/CLI/UI ni autoarranque. Orden de la
activación: PREPARING en SQLite → inventario igual a la vista previa → copia
verificada en el directorio de la aplicación → inventario igual tras copiar →
publicación atómica → marcador → una transacción ACTIVE con índice y manifiesto.
Un fallo antes del marcador deja FAILED sin nada activo; una caída deja
PREPARING, que solo se reanuda o abandona explícitamente.
"""

import json
from pathlib import Path

from harness_local.adapters import migration as filesystem
from harness_local.adapters.legacy import LocalLegacyReader
from harness_local.core.migration import (
    MigrationError, build_manifest, build_preview, document_changes, inventory_blockers, inventory_fingerprint,
)
from harness_local.storage.migration import ModeConflict, ModeGuard, SQLiteMigrationRepository, live_conflict

EXPORT_NAME = "managed-state.json"


def _nonempty(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Explicit {name} required")


class MigrationService:
    def __init__(self, engine, *, migrations_dir=None, clock=None, probe=None, hook=None):
        """`migrations_dir` vive fuera de cualquier checkout; por defecto junto a la base SQLite.

        `hook(step, **info)` es un punto de observación/inyección de fallos para pruebas.
        """
        self.repository = SQLiteMigrationRepository(engine, clock=clock)
        self.probe = probe or filesystem.probe
        self.guard = ModeGuard(engine, self.probe)
        self.database = Path(engine.url.database).resolve()
        self.migrations_dir = Path(migrations_dir or self.database.parent / "migrations").resolve()
        self.hook = hook or (lambda step, **info: None)

    @staticmethod
    def _read(root: str):
        return LocalLegacyReader().read(root)

    def _related(self, facts) -> tuple[set[str], set[str]]:
        """Raíces con trabajo gestionado vivo en el mismo checkout o repositorio."""
        probed = self.repository.unfinished_roots()
        related = set()
        for root in probed:
            if root == facts.root:
                related.add(root)
                continue
            try:
                other = self.probe(root)
            except (OSError, ValueError):
                related.add(root)  # inverificable: se trata como relacionado (conservador)
                continue
            if facts.repository_key is not None and other.repository_key == facts.repository_key:
                related.add(root)
        return related, probed

    def _checkout_blockers(self, facts) -> list[dict]:
        blockers = []
        root = Path(facts.root)
        if not facts.legacy_state:
            blockers.append({"code": "no_legacy_state", "diagnostic": "Sin .harness/runs: el checkout puede "
                             "gestionarse sin migración."})
        if facts.marker is not None or facts.marker_error:
            blockers.append({"code": "marker_present", "diagnostic": "Ya existe un marcador de modo gestionado."})
        for path, name in ((self.migrations_dir, "directorio de migraciones"), (self.database, "base SQLite")):
            if path.is_relative_to(root) or root.is_relative_to(path):
                blockers.append({"code": "storage_inside_checkout",
                                 "diagnostic": f"El {name} debe estar fuera del checkout."})
        return blockers

    def preview(self, root) -> dict:
        """Solo lectura: no escribe en el checkout, en SQLite ni en el directorio de migraciones."""
        facts = self.probe(root)
        inventory = self._read(facts.root)
        related, probed = self._related(facts)
        blockers = self._checkout_blockers(facts) + self.repository.blockers(facts, related, probed)
        return build_preview(inventory, facts, blockers)

    def activate(self, root, *, preview_sha256: str, legacy_stopped: str):
        """`legacy_stopped`: confirmación explícita de que no queda ningún escritor legacy."""
        _nonempty(preview_sha256, "preview hash")
        _nonempty(legacy_stopped, "legacy writers stopped confirmation")
        facts = self.probe(root)
        live = self.repository.live(facts)
        if live is not None:
            if (conflict := live_conflict(live, facts.root, preview_sha256)) is not None:
                raise ModeConflict(conflict)
            return live
        # Comprobación previa sin efectos; se repite con autoridad tras PREPARING.
        inventory = self._read(facts.root)
        blockers = self._checkout_blockers(facts) + inventory_blockers(inventory)
        if blockers:
            raise MigrationError(f"{blockers[0]['diagnostic']} ({blockers[0]['code']})")
        if inventory_fingerprint(inventory) != preview_sha256:
            raise MigrationError("El estado legacy cambió desde la vista previa; generarla de nuevo.")
        related, probed = self._related(facts)
        record, created = self.repository.begin_activation(facts, preview_sha256, legacy_stopped,
                                                           self.migrations_dir, related, probed)
        if not created:
            return record
        self.hook("activation_prepared", activation_id=record.id)
        return self._complete(record)

    def resume_activation(self, activation_id: str, *, reason: str, expected_version: int | None = None):
        return self._complete(self.repository.take_over(activation_id, "PREPARING", reason,
                                                        expected_version=expected_version))

    def _complete(self, record):
        token = record.owner_token
        try:
            facts = self.probe(record.root)
            if (facts.root, facts.repository_key) != (record.root, record.repository_key):
                raise MigrationError("La identidad del checkout o de su repositorio cambió; nada se activa.")
            if facts.marker_error or (facts.marker is not None and facts.marker != record.marker):
                raise MigrationError("Existe un marcador ajeno a esta activación; no se sobrescribe.")
            inventory = self._read(record.root)
            if blockers := inventory_blockers(inventory):
                raise MigrationError(f"{blockers[0]['diagnostic']} ({blockers[0]['code']})")
            if inventory_fingerprint(inventory) != record.preview_sha256:
                raise MigrationError("El estado legacy cambió desde la vista previa; nada se activa.")
            self.hook("inventory_verified", activation_id=record.id)
            final = Path(record.snapshot_root)
            if not final.is_dir():
                final.parent.mkdir(parents=True, exist_ok=True)
                staging = final.parent / f"staging-{token}"
                filesystem.copy_snapshot(record.root, inventory, staging, hook=self.hook)
                self.hook("copy_complete", activation_id=record.id)
                mtimes = filesystem.origin_mtimes(record.root, inventory)
                if inventory_fingerprint(self._read(record.root)) != record.preview_sha256:
                    raise MigrationError("El estado legacy cambió durante la copia; nada se activa.")
                filesystem.publish(staging, final)
            else:
                mtimes = filesystem.origin_mtimes(record.root, inventory)
            self.hook("published", activation_id=record.id)
            snapshot = self._read(str(final))
            if snapshot.root != record.snapshot_root or inventory_fingerprint(snapshot) != record.preview_sha256:
                raise MigrationError("La copia publicada no reproduce el inventario verificado.")
            filesystem.write_marker(record.root, record.marker)
            self.hook("marker_written", activation_id=record.id)
        except Exception as exc:
            # El token decide quién falla: un proceso que perdió la transición no toca el marcador.
            try:
                self.repository.fail_activation(record.id, token, f"{type(exc).__name__}: {exc}")
            except Exception:
                raise exc
            try:
                filesystem.remove_marker(record.root, record.marker)
            except (OSError, MigrationError):
                pass
            raise
        manifest = build_manifest(record.id, facts, record.snapshot_root, inventory, mtimes)
        return self.repository.finalize_activation(record.id, token, manifest, snapshot)

    def abandon_activation(self, activation_id: str, *, reason: str, expected_version: int | None = None) -> None:
        """PREPARING → FAILED retirando el marcador propio; en FAILED solo retira un marcador residual."""
        record = self.repository.get(activation_id)
        if record.status == "FAILED":
            if expected_version is not None and record.version != expected_version:
                raise ModeConflict(f"La activación cambió (versión {record.version}); recargar antes de repetir.")
            filesystem.remove_marker(record.root, record.marker)
            return
        record = self.repository.take_over(activation_id, "PREPARING", reason, expected_version=expected_version)
        filesystem.remove_marker(record.root, record.marker)
        self.repository.abandon(record.id, record.owner_token, reason)

    def revert(self, activation_id: str, *, reason: str, expected_version: int | None = None):
        """Exporta y comprueba el estado gestionado, retira el marcador y devuelve el checkout a legacy."""
        record = self.repository.begin_revert(activation_id, reason, expected_version=expected_version)
        self.hook("revert_prepared", activation_id=record.id)
        return self._complete_revert(record)

    def resume_revert(self, activation_id: str, *, reason: str, expected_version: int | None = None):
        return self._complete_revert(self.repository.take_over(activation_id, "REVERTING", reason,
                                                               expected_version=expected_version))

    def _complete_revert(self, record):
        state = self.repository.export_state(record.id)
        directory = Path(record.snapshot_root).parent / "export"
        sha256 = filesystem.write_export(directory, EXPORT_NAME, state)
        if self.repository.export_state(record.id) != state:
            raise MigrationError("El estado gestionado cambió durante la exportación; no se revierte.")
        self.hook("exported", activation_id=record.id)
        filesystem.remove_marker(record.root, record.marker)
        self.hook("marker_removed", activation_id=record.id)
        return self.repository.finish_revert(record.id, record.owner_token, str(directory / EXPORT_NAME), sha256)

    def status(self, root) -> dict:
        """Modo, deriva legacy y propuestas de documentos; solo lectura."""
        assessment = self.guard.assess(root)
        activation = assessment.activation
        result = {"refusal": assessment.refusal, "activation": None, "drift": None, "documents": None}
        if activation is not None:
            result["activation"] = {"id": activation.id, "status": activation.status, "root": activation.root,
                                    "snapshot_root": activation.snapshot_root,
                                    "manifest_sha256": activation.manifest_sha256}
        if activation is not None and activation.manifest_json:
            manifest = json.loads(activation.manifest_json)
            result["drift"] = filesystem.legacy_drift(activation.root, manifest)
            current = filesystem.current_documents(activation.root, self._read(activation.root))
            result["documents"] = document_changes(manifest, current)
        return result
