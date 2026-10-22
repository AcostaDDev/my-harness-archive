"""Permission ledger, serialized with the managed queue and invocation intent."""
from dataclasses import replace
from datetime import datetime, timedelta
import json
import os
import pwd
from uuid import uuid4

from sqlalchemy import select

from harness_local.core.engine.contracts import freeze
from harness_local.core.engine.permissions import allowed, binding, digest
from harness_local.storage.managed import Conflict
from harness_local.storage.models import ManagedRunRow as Run, ManagedJobRow as Job, PermissionRequestRow as Permission


def actor():
    # Service identity, not authentication of the browser user (local session is pending).
    return {'uid': os.getuid(), 'user': pwd.getpwuid(os.getuid()).pw_name}


def view(row, now):
    data = {key: getattr(row, key) for key in ('id', 'run_id', 'version', 'status', 'request', 'fingerprint',
            'expires_at', 'decision', 'consumed_by', 'supersedes')}
    data['effective_status'] = 'EXPIRED' if row.expires_at <= now and row.status in ('PENDING', 'GRANTED', 'DENIED') else row.status
    return data


class PermissionRepository:
    def __init__(self, managed):
        self.managed = managed

    def _editable(self, session, run_id, expected):
        run = session.get(Run, run_id)
        if run is None:
            raise LookupError('Unknown managed run')
        if run.version != expected:
            raise Conflict('Run changed; reload before deciding permissions')
        if session.scalar(select(Job.id).join(Run, Job.run_id == Run.id).where(Run.root == run.root,
                Job.status.in_(('QUEUED', 'ACTIVE', 'RECOVERY_REQUIRED')))) is not None:
            raise Conflict('Permissions can only change at a stopped, unlocked boundary')
        if run.status not in ('STOPPED', 'BLOCKED', 'REVISION_LIMIT', 'INTERRUPTED'):
            raise Conflict('Permissions require a stopped task')
        return run

    def list(self, run_id):
        from sqlalchemy.orm import Session
        # Reads never expire or rewrite rows; historical decisions stay intact.
        with Session(self.managed.engine) as session:
            if session.scalar(select(Run.id).where(Run.id == run_id)) is None:  # sin cargar el historial (D142)
                raise LookupError('Unknown managed run')
            rows = session.scalars(select(Permission).where(Permission.run_id == run_id).order_by(Permission.created_at, Permission.id)).all()
            return [view(row, self.managed._now()) for row in rows]

    def create(self, run_id, expected, *, kind, target, operation, arguments, requested_by, source_attempt_id,
               reason, ttl_seconds, supersedes=None):
        from harness_local.core.engine.permissions import KINDS
        if kind not in KINDS or any(not isinstance(v, str) or not v.strip() for v in (target, operation, requested_by, reason)):
            raise ValueError('Explicit category, operation, target, requester and reason required')
        operations = {'files': 'write', 'tools': 'use', 'network': 'connect', 'product': 'decide', 'acceptance': 'accept'}
        if operation != operations[kind] or arguments:
            raise ValueError('Operation must match its category; scope is the exact target, without implicit arguments')
        if type(ttl_seconds) is not int or not 1 <= ttl_seconds <= 86400:
            raise ValueError('Validity must be between 1 second and 24 hours')
        if not isinstance(arguments, list) or not all(isinstance(v, str) for v in arguments):
            raise ValueError('Structured operation arguments required')
        with self.managed._write() as session:
            run = self._editable(session, run_id, expected)
            history = json.loads(run.history_json)['history']
            if history['task_json'] is None:
                raise Conflict('A frozen task contract is required')
            if source_attempt_id not in [a['request']['id'] for a in history['attempts']]:
                raise ValueError('Source attempt must belong to this run')
            now = self.managed._now()
            if session.scalar(select(Permission.id).where(Permission.run_id == run_id,
                    Permission.status.in_(('PENDING', 'GRANTED', 'DENIED')), Permission.expires_at > now,
                    Permission.id != (supersedes or ''),
                    Permission.request['kind'].as_string() == kind,
                    Permission.request['target'].as_string() == target)) is not None:
                raise Conflict('Replace the existing request explicitly before changing this scope')
            if supersedes:
                old = session.get(Permission, supersedes)
                if old is None or old.run_id != run_id or old.status not in ('PENDING', 'GRANTED', 'DENIED', 'CONSUMED', 'DENIED_CONSUMED'):
                    raise Conflict('Request cannot be replaced')
                old.status, old.version = 'SUPERSEDED', old.version + 1
            request = {'kind': kind, 'target': target, 'operation': operation, 'arguments': arguments,
                       'requested_by': requested_by, 'source_attempt_id': source_attempt_id, 'reason': reason,
                       'binding': binding(run), 'created_by': actor()}
            expires = (datetime.fromisoformat(now) + timedelta(seconds=ttl_seconds)).isoformat(timespec='microseconds')
            row = Permission(id=str(uuid4()), run_id=run_id, version=1, status='PENDING', request=request,
                             fingerprint=digest({'request': request, 'expires_at': expires}), expires_at=expires,
                             created_at=now, decision=None, consumed_by=None, supersedes=supersedes)
            session.add(row)
            self.managed._event(session, run, 'permission_requested', view(row, now))
            return view(row, now)

    def decide(self, run_id, permission_id, expected, *, expected_request_version, fingerprint, decision, scope, reason):
        if decision not in ('grant', 'deny') or scope not in ('once', 'task') or not reason.strip():
            raise ValueError('Explicit decision, validity scope and reason required')
        with self.managed._write() as session:
            run = self._editable(session, run_id, expected)
            row = session.get(Permission, permission_id)
            if row is None or row.run_id != run_id:
                raise LookupError('Unknown permission request')
            now = self.managed._now()
            if (row.version != expected_request_version or row.fingerprint != fingerprint or row.status != 'PENDING'
                    or row.expires_at <= now or row.request['binding'] != binding(run)
                    or row.fingerprint != digest({'request': row.request, 'expires_at': row.expires_at})):
                raise Conflict('Request expired, changed or already decided')
            if decision == 'grant' and not allowed(run, row.request['kind'], row.request['target']):
                raise Conflict('Grant exceeds the global/project/contract/provider authority')
            row.status, row.version = ('GRANTED' if decision == 'grant' else 'DENIED'), row.version + 1
            row.decision = {'actor': actor(), 'decision': decision, 'scope': scope, 'reason': reason,
                            'decided_at': now, 'expires_at': row.expires_at, 'fingerprint': row.fingerprint}
            self.managed._event(session, run, 'permission_decided', view(row, now))
            return view(row, now)


def authorize(session, managed, run, request):
    """Only the next executor intent can consume grants, atomically with its row."""
    if request.permission_snapshot_json is not None:
        raise Conflict('Callers cannot inject permission snapshots')
    grants, denials = [], []
    if request.role == 'executor':
        now = managed._now()
        rows = session.scalars(select(Permission).where(Permission.run_id == run.id,
                            Permission.status.in_(('GRANTED', 'DENIED'))).order_by(Permission.created_at, Permission.id)).all()
        for row in rows:
            # Product and acceptance decisions remain a distinct audit; never unlock an executor or commit.
            if row.request['kind'] not in ('files', 'tools', 'network'):
                continue
            if row.expires_at <= now or row.request['binding'] != binding(run):
                continue
            if row.fingerprint != digest({'request': row.request, 'expires_at': row.expires_at}):
                raise Conflict('Permission request fingerprint changed')
            if row.status == 'DENIED':
                denials.append(view(row, now))
                if row.decision['scope'] == 'once':
                    row.status, row.version, row.consumed_by = 'DENIED_CONSUMED', row.version + 1, request.id
                managed._event(session, run, 'permission_denial_applied', {'permission_id': row.id, 'attempt_id': request.id})
                continue
            if not allowed(run, row.request['kind'], row.request['target']):
                raise Conflict('Frozen permission authority no longer allows the request')
            grants.append(view(row, now))
            if row.decision['scope'] == 'once':
                row.status, row.version, row.consumed_by = 'CONSUMED', row.version + 1, request.id
            managed._event(session, run, 'permission_applied', {'permission_id': row.id, 'attempt_id': request.id,
                                                               'fingerprint': row.fingerprint})
    payload = {'attempt_id': request.id, 'context_json': request.context_json, 'task_json': request.task_json,
               'grants': grants, 'denials': denials}
    return replace(request, permission_snapshot_json=freeze({'payload': payload, 'sha256': digest(payload)}))
