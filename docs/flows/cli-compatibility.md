# Flow — automatic CLI discovery and compatibility

Implemented in P011-T012 (D174), following the [contract](../phase/P011-T011_CONTRATO_COMPATIBILIDAD_CLI.md)
and its HITL clarification. No version pin, candidate acceptance or operator evidence file is required in v7.

```mermaid
flowchart TD
    C["Parse local-config-7: explicit environment, provider, optional executable"] --> D["Data-only project composition: versions not yet observed"]
    D --> S["Service startup or effective project composition: resolve selected roles"]
    S --> P["Resolve command on explicit absolute PATH or optional path"]
    P --> V["Bounded version/help probes, closed stdin and temporary cwd"]
    V --> M{"Stable version at or above minimum and required interface present?"}
    M -- no --> X["Install/update/capability diagnostic; no model invocation or fallback"]
    M -- yes --> F["Freeze observed version, launch identity and packaged policy in job"]
    F --> B{"Current composition and launch identity match frozen job?"}
    B -- no --> Q["RECOVERY_REQUIRED; preserve original job and evidence"]
    B -- yes --> A["Fresh version/help observation for this attempt"]
    A --> G{"Capabilities and actual argv preserve required guards?"}
    G -- no --> R["Record refused intent without target launch; explicit resolution"]
    G -- yes --> I["Durable process intent and process identity; target waits at gate"]
    I --> H{"Launch identity still matches immediately before GO?"}
    H -- no --> K["Stop own gated group; record dead or uncertain state; no target GO"]
    H -- yes --> E["GO: fresh client session under existing controls"]
    E --> T{"One known terminal, valid payload and dead process group?"}
    T -- no --> O["Preserve original stream/failure; existing stop or recovery rules"]
    T -- yes --> N["Continue engine validation and review; every next attempt revalidates"]
```

Minimums are Codex 0.163.0 and Claude Code 2.1.304 for both roles. Historical configurations/evidence remain
readable; a below-minimum client cannot start new work. Only effective provider roles are detected during normal
operation; `check-config --preflight` explicitly diagnoses defaults and all preset roles. No auth/status/login,
test prompt, network lookup, installation or global configuration change is part of discovery.

Each mutation observes the client again and reuses that project resolution only inside the same request. Each
attempt also observes version/help again. Content-hash caching restats inode, size, mtime and ctime; it is not a
cached compatibility verdict. A fresh job can detect an updated client automatically; a queued job never adopts it. Source/profile hashes
bind the packaged policy, and symlink/script/interpreter hashes bind explicit local launch files. Hashing does not
certify transitive runtime dependencies or prevent adversarial concurrent replacement. Public reports expose hashes
and structured diagnostics, not raw help, environment values or executable paths.

HITL D174: later releases matching the known interface are admitted with **conditional compatibility**. The
packaged policy retains explicit sandbox, trust, memory and configuration controls; it does not claim observation
of undocumented startup persistence or effective permissions in every new release. Local missing/changed controls
block. No per-release approval/audit is transferred to the user. Provider-internal retries remain unknown; the
harness adds no fallback or retry. Read-only project/history views do not trigger discovery.
