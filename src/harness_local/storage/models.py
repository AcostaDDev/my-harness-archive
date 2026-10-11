from sqlalchemy import Boolean, JSON, ForeignKey, ForeignKeyConstraint, Integer, String, Text, UniqueConstraint
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
