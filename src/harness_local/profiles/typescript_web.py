"""Perfil opt-in para una web TypeScript estática; sin ejecución al importar."""

from harness_local.core.engine.context import Command, JUnitDeclaration, ProjectProfile


def typescript_web_profile() -> ProjectProfile:
    return ProjectProfile(
        name="typescript-web",
        preparation=(
            Command(("node", "--version"), timeout_seconds=30),
            Command(("npm", "--version"), timeout_seconds=30),
            Command(("npm", "ci", "--offline", "--ignore-scripts", "--no-audit", "--no-fund"),
                    environment=(("npm_config_engine_strict", "true"),), timeout_seconds=120),
        ),
        validations=tuple(Command(("npm", "run", script), timeout_seconds=120)
                          for script in ("check", "test", "build")),
        allowed_command_prefixes=(("npm", "run", "check"), ("npm", "run", "test"),
                                  ("npm", "run", "build")),
        junit_reports=(JUnitDeclaration(Command(('npm', 'run', 'test'), timeout_seconds=120),
                                        '.local/junit.xml', 'Tests Node de tests/*.test.mjs; no cobertura de código'),),
        protected_paths=("docs/**", ".harness/**", ".codex/**", ".claude/**", "AGENTS.md", "CLAUDE.md",
                         "package.json", "package-lock.json", "tsconfig.json", "scripts/**", "tests/**", ".gitignore"),
        sensitive_paths=(".env", ".env.*", "**/.env", "**/.env.*", "*.pem", "*.key", "*.p12", "*.pfx", "id_rsa*"),
        sensitive_allowlist=(".env.example",),
        executor_instructions=(
            "Implement the static TypeScript web application within the frozen task paths. "
            "Use the existing npm run check, npm run test and npm run build scripts. "
            "Do not weaken tests, compiler settings, scripts or the dependency lock. "
            "Keep node_modules, .build, dist and the npm cache ignored. "
            "Preparation uses an already populated, explicitly configured npm cache offline; "
            "a cache miss stops the task. Dependency downloads, configuration changes and "
            "network access require separate authorization. Command prefixes do not grant "
            "agent tools or provide a sandbox."
        ),
    )
