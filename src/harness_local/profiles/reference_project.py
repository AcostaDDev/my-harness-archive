"""Reglas de stack extraídas de config.yaml/helpers legacy; sin rutas globales."""

from harness_local.core.engine.context import Command, ProjectProfile


def reference_project_profile() -> ProjectProfile:
    compose = ("docker", "compose", "--env-file", ".env.example")
    web = (*compose, "exec", "-T", "web", "python")
    settings = "--settings=config.settings.test"
    return ProjectProfile(
        name="reference_project",
        preparation=(
            Command(("python3", ".harness/scripts/dev_tools.py", "sync-python"), timeout_seconds=600),
            Command(("docker", "info", "--format", "{{.ServerVersion}}"), timeout_seconds=600),
        ),
        validations=(
            Command(("python", "-m", "ruff", "check", "src")),
            Command(("python", "-m", "ruff", "format", "--check", "src")),
            Command((*compose, "config", "--quiet")),
            Command((*compose, "up", "--build", "--detach", "--wait", "--wait-timeout", "240")),
            Command((*web, "manage.py", "check", settings)),
            Command((*web, "manage.py", "makemigrations", "--check", "--dry-run", "--noinput", settings)),
            Command((*web, "manage.py", "test", "--noinput", settings)),
            Command((*web, "-m", "config.celery_smoke", "--timeout", "30")),
        ),
        allowed_command_prefixes=tuple((name,) for name in ("python", "python3", "pytest", "ruff", "mypy", "uv", "poetry", "docker-compose")) + (("docker", "compose"),),
        protected_paths=("docs/**", ".harness/**", ".codex/**", ".claude/**", "AGENTS.md", "CLAUDE.md"),
        sensitive_paths=(".env", ".env.*", "*.pem", "*.key", "*.p12", "*.pfx", "id_rsa*"),
        sensitive_allowlist=(".env.example",),
        formatter_argv=("python", "-m", "ruff", "format", "--"),
        formatter_paths=("src/**/*.py", "src/*.py"),
        executor_instructions=(
            "For focused Django tests use python3 .harness/scripts/dev_tools.py test <app.TestCase.test_method>. "
            "Use current source on PostgreSQL via Docker; do not substitute SQLite or temporary settings. "
            "Dependency installation and asset downloads require separate tool/network authorization."
        ),
    )
