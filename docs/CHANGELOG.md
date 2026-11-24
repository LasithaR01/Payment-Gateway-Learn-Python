# Project changelog

Learning-repo notes for Payment Gateway (Bitcart study copy). Upstream Bitcart history stays in `api/CHANGELOG.md`.

## 2026-11-25

- Added root GitHub Actions CI (`.github/workflows/ci.yml`): API smoke install/import + repo layout checks.
- Merge policy: PR → CI green → merge; red CI blocks merge (Cursor rule updated).
- Added Cursor rule `.cursor/rules/github-achievements-commits.mdc` (same badge/PR workflow as the supermarket project).
- Documented that nested `api|admin|store/.github` workflows do not run in this monorepo.
- Local API run path: Windows Redis + `run_local.bat` / `scripts/run_local.py`, UTF-8 template load, Redis timeouts, onion middleware soft-fail, startup access banner.
