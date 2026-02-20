---
name: tank-package-publisher
description: Package lifecycle specialist for Tank directory publishing. Use when users ask to publish a skill to Tank, run tank publish, fix publish failures, validate skills.json, bump versions, or verify releases. Handles dry-run-first workflow, manifest validation, and publish error remediation.
---

# Tank Package Publisher

Manage, validate, and publish skills to the Tank directory using the `tank` CLI with a dry-run-first workflow.

## Trigger Phrases

- "publish this skill to Tank"
- "run tank publish"
- "tank publish --dry-run"
- "version already exists"
- "fix tank publish error"
- "prepare this skill for release"
- "validate skills.json before publishing"
- "release checklist for tankpkg"

## Critical Workflow

Do not skip steps. Always run in order.

1. **Preflight**
   - Ensure `tank` is installed: `tank --version`
   - Ensure auth is valid: `tank whoami` (or run `tank login`)
   - Ensure target directory contains both required files:
     - `skills.json`
     - `SKILL.md`

2. **Manifest and Package Validation**
   - Validate `skills.json` parseability and required fields.
   - Confirm package name is valid (lowercase, optional `@org/name`, max length 214).
   - Confirm semver version format.
   - Ensure package stays within Tank packer limits:
     - max compressed package size: 50MB
     - max file count: 1000

3. **Dry Run First**
   - Run: `tank publish --dry-run`
   - Do not publish if dry-run fails.
   - Review dry-run output for name/version/size/file count.

4. **Publish**
   - Run: `tank publish`
   - If publish fails, classify error and apply the matching fix from the Failure Map.

5. **Post-Publish Verification**
   - Confirm package appears in directory:
     - `tank info <package-name>`
     - `tank search <keyword>`
   - Optionally run `tank verify` and `tank audit <package-name>`.

## Manifest Rules

Recommended `skills.json` baseline:

```json
{
  "name": "@tank/your-skill-name",
  "version": "1.0.0",
  "description": "One-sentence trigger-oriented description.",
  "permissions": {
    "network": { "outbound": [] },
    "filesystem": { "read": [], "write": [] },
    "subprocess": false
  },
  "repository": "https://github.com/tankpkg/skills"
}
```

Use least-privilege permissions unless the workflow requires broader access.

## Package Hygiene

- Keep release payload small and focused.
- Exclude unnecessary files with `.tankignore`.
- Tank automatically excludes `node_modules` and `.git`.
- Avoid symlinks and path tricks; Tank packer rejects unsafe paths.

## Failure Map

- **Not logged in** (`Not logged in. Run: tank login`)
  - Run `tank login`, then retry.
- **No skills.json found**
  - Run `tank init` in target directory, then populate metadata and retry.
- **Invalid skills.json / parse error**
  - Fix JSON syntax and schema shape, rerun dry-run.
- **401 Authentication failed**
  - Re-authenticate with `tank login`; verify token with `tank whoami`.
- **403 permission error**
  - Confirm org ownership or publish rights for package scope.
- **409 version already exists**
  - Bump `skills.json.version` to next semver and republish.
- **Upload/confirm failed**
  - Retry once, then inspect network/auth state and rerun dry-run.

## Safe Defaults

- Default to `tank publish --dry-run` before every real publish.
- Never mutate unrelated files during release prep.
- For bugfix releases, keep changes minimal and version bump explicit.
- Always report exact command outputs that matter (name/version, dry-run pass/fail, final publish status).

## Output Contract

When completing a publish task, return:

1. Package name and target version.
2. Preflight results (auth, required files, manifest validity).
3. Dry-run status and key metrics.
4. Publish result (success/failure) and exact remediation if failed.
5. Post-publish verification commands and their outcomes.

## Resources

Additional documentation and tools for Tank publishing:

### References

- [references/MANIFEST_SCHEMA.md](references/MANIFEST_SCHEMA.md) — Complete `skills.json` schema with field constraints and examples
- [references/ERROR_CODES.md](references/ERROR_CODES.md) — Full error catalog with remediation steps
- [references/CI_PUBLISHING.md](references/CI_PUBLISHING.md) — CI/CD automation workflows for GitHub Actions, GitLab CI

### Scripts

Executable helpers for common tasks:

- `scripts/preflight-check.sh <dir>` — Validate auth, required files, and package limits
- `scripts/validate-manifest.sh <dir>` — Check `skills.json` syntax and schema
- `scripts/version-bump.sh <dir> <major|minor|patch>` — Bump version in manifest and SKILL.md

### Assets

- [assets/skills.json.template](assets/skills.json.template) — Starter manifest with all fields
- [assets/.tankignore.template](assets/.tankignore.template) — Common ignore patterns
