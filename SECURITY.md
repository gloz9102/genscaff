# Security Policy

## Reporting a vulnerability

Use the repository's private GitHub Security Advisory reporting flow for vulnerabilities in the validator, browser runner, command allowlist, path handling, or evidence-integrity checks.

Do not publish an unpatched exploit or bypass in a public issue. Include the affected version or commit, reproduction steps, expected impact, and a minimal proof of concept. Ordinary quality-gate false positives and feature requests belong in public issues.

No response-time or remediation-time guarantee is currently offered.

## Running Genscaff safely

The supported release line is 2.0.x. The 1.x standalone package receives security fixes only during the v2.0 compatibility window and is removed in v2.1.

Treat every repository command as arbitrary code. Genscaff does not re-run project commands unless
the repository is trusted and `--execute-approved-commands` is passed explicitly. Review the exact
commands and their package scripts before opting in.

Browser audits execute the target page's JavaScript and may issue network requests declared by that
page. Do not run active browser or command verification against an untrusted repository, and do not
expose credentials or secrets to the audited browser session.

Install plugin releases from this repository and verify release SHA-256 sidecars when using ZIP artifacts. Core `$genscaff` has no Node runtime dependency; npm dependencies belong only to `$genscaff-release-audit` and are installed from its committed lockfile with `npm ci --omit=dev`.
