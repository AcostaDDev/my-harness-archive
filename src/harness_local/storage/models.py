from sqlalchemy import Boolean, Index, JSON, ForeignKey, ForeignKeyConstraint, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SimulationRow(Base):
    __tablename__ = "simulations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    # ISO 8601 conserva UTC; SQLite DateTime no conserva zona horaria.
    created_at: Mapped[str] = mapped_column(String(40))
    events: Mapped[list[str]] = mapped_column(JSON)


class LegacySourceRow(Base):
    __tablename__ = "legacy_sources"

    root: Mapped[str] = mapped_column(String, primary_key=True)
    observed_at: Mapped[str] = mapped_column(String(40))
    watch_enabled: Mapped[bool] = mapped_column(Boolean, server_default="0")
    diagnostic: Mapped[str | None] = mapped_column(Text, nullable=True)


class LegacyRunRow(Base):
    __tablename__ = "legacy_runs"

    root: Mapped[str] = mapped_column(ForeignKey("legacy_sources.root", ondelete="CASCADE"), primary_key=True)
    path: Mapped[str] = mapped_column(String, primary_key=True)
    identity: Mapped[str] = mapped_column(String)


class LegacyArtifactRow(Base):
    __tablename__ = "legacy_artifacts"
    __table_args__ = (
        ForeignKeyConstraint(["root", "run_path"], ["legacy_runs.root", "legacy_runs.path"]),
    )

    root: Mapped[str] = mapped_column(ForeignKey("legacy_sources.root", ondelete="CASCADE"), primary_key=True)
    path: Mapped[str] = mapped_column(String, primary_key=True)
    run_path: Mapped[str | None] = mapped_column(String, nullable=True)
    kind: Mapped[str] = mapped_column(String(40))
    format: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(20))
    sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    payload: Mapped[object] = mapped_column(JSON(none_as_null=True), nullable=True)
    diagnostic: Mapped[str | None] = mapped_column(Text, nullable=True)


class LegacyEventRow(Base):
    __tablename__ = "legacy_events"
    __table_args__ = {"sqlite_autoincrement": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    root: Mapped[str] = mapped_column(ForeignKey("legacy_sources.root", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(40))
    observed_at: Mapped[str] = mapped_column(String(40))
    payload: Mapped[dict] = mapped_column(JSON)


class ManagedRunRow(Base):
    __tablename__ = "managed_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    root: Mapped[str] = mapped_column(String)
    task_id: Mapped[str] = mapped_column(String)
    phase_id: Mapped[str] = mapped_column(String)
    context_json: Mapped[str] = mapped_column(Text)
    versions_json: Mapped[str] = mapped_column(Text)
    history_json: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40))
    stage: Mapped[str] = mapped_column(String(40))
    revisions: Mapped[int] = mapped_column(Integer)
    revision_limit: Mapped[int] = mapped_column(Integer)
    version: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[str] = mapped_column(String(40))
    updated_at: Mapped[str] = mapped_column(String(40))


_LIVE_ACTIVATION = text("status IN ('PREPARING', 'ACTIVE', 'REVERTING')")


class ManagedActivationRow(Base):
    """Modo gestionado de un checkout legacy H2.5: autoridad del modo y procedencia del histórico."""

    __tablename__ = "managed_activations"
    __table_args__ = (
        Index("uq_managed_activations_live_root", "root", unique=True, sqlite_where=_LIVE_ACTIVATION),
        Index("uq_managed_activations_live_repository", "repository_key", unique=True,
              sqlite_where=_LIVE_ACTIVATION),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    root: Mapped[str] = mapped_column(String)
    repository_key: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String(20))
    preview_sha256: Mapped[str] = mapped_column(String(64))
    legacy_stopped: Mapped[str] = mapped_column(Text)
    rules_json: Mapped[str] = mapped_column(Text)
    marker: Mapped[str] = mapped_column(Text)
    marker_sha256: Mapped[str] = mapped_column(String(64))
    snapshot_root: Mapped[str] = mapped_column(String)
    manifest_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    manifest_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    owner_token: Mapped[str | None] = mapped_column(String(36), nullable=True)
    version: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[str] = mapped_column(String(40))
    activated_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    finished_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    diagnostic: Mapped[str | None] = mapped_column(Text, nullable=True)
    revert_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    export_path: Mapped[str | None] = mapped_column(String, nullable=True)
    export_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)


class ManagedJobRow(Base):
    __tablename__ = "managed_jobs"
    __table_args__ = {"sqlite_autoincrement": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    idempotency_key: Mapped[str] = mapped_column(String(200), unique=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("managed_runs.id"))
    request_json: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40))
    owner_token: Mapped[str | None] = mapped_column(String(36), nullable=True)
    heartbeat_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    lease_until: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[str] = mapped_column(String(40))
    finished_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    diagnostic: Mapped[str | None] = mapped_column(Text, nullable=True)
    process_owner: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    owner_closed: Mapped[bool] = mapped_column(Boolean, server_default="0")
    # Activación H2.5 bajo la que se admitió el job; null en checkouts sin estado legacy.
    activation_id: Mapped[str | None] = mapped_column(ForeignKey("managed_activations.id"), nullable=True)


class CheckoutLockRow(Base):
    __tablename__ = "checkout_locks"

    root: Mapped[str] = mapped_column(String, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("managed_jobs.id"), unique=True)


class ManagedAttemptRow(Base):
    __tablename__ = "managed_attempts"
    __table_args__ = (UniqueConstraint("run_id", "number"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("managed_runs.id"))
    number: Mapped[int] = mapped_column(Integer)
    request_json: Mapped[str] = mapped_column(Text)
    versions_json: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40))
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[str] = mapped_column(String(40))
    finished_at: Mapped[str | None] = mapped_column(String(40), nullable=True)


class ManagedEventRow(Base):
    __tablename__ = "managed_events"
    __table_args__ = (UniqueConstraint("run_id", "sequence"), {"sqlite_autoincrement": True})

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("managed_runs.id"))
    sequence: Mapped[int] = mapped_column(Integer)
    kind: Mapped[str] = mapped_column(String(40))
    recorded_at: Mapped[str] = mapped_column(String(40))
    payload: Mapped[dict] = mapped_column(JSON)


class ManagedProcessRow(Base):
    __tablename__ = "managed_processes"

    attempt_id: Mapped[str] = mapped_column(ForeignKey("managed_attempts.id"), primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("managed_jobs.id"))
    spec: Mapped[dict] = mapped_column(JSON)
    identity: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(40))
    capture: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class ManagedCommitRow(Base):
    """Intención y resultado del commit aceptado; fuente de la conciliación H2.4."""

    __tablename__ = "managed_commits"
    __table_args__ = (Index("uq_managed_commits_live", "run_id", unique=True,
                            sqlite_where=text("status IN ('INTENT', 'COMMITTED')")),)

    operation_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("managed_runs.id"))
    job_id: Mapped[int] = mapped_column(ForeignKey("managed_jobs.id"))
    status: Mapped[str] = mapped_column(String(40))
    base_revision: Mapped[str] = mapped_column(String(64))
    reviewed_fingerprint: Mapped[str] = mapped_column(String(64))
    expected_tree: Mapped[str] = mapped_column(String(64))
    expected_commit: Mapped[str] = mapped_column(String(64))
    intent_json: Mapped[str] = mapped_column(Text)
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    commit_sha: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[str] = mapped_column(String(40))
    finished_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
