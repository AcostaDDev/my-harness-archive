# Synthetic CLI capability fixtures

Independently authored flag lists, not copied CLI output. `test_cli_baseline.py` uses them for positive and
per-flag negative preflight checks. They prove harness behavior, not vendor semantics, authentication or inference.
The real help originals in `../cli_help/` remain private historical evidence and are not dependencies of public tests.
