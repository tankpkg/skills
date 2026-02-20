# Tank Publish Error Codes

Complete reference for `tank publish` errors and their remediation.

## Authentication Errors

### Not logged in

```
Not logged in. Run: tank login
```

**Cause:** No valid authentication token in CLI config.

**Remediation:**
1. Run `tank login`
2. Complete browser authentication
3. Verify with `tank whoami`
4. Retry publish

### 401 Authentication failed

```
Authentication failed. Run: tank login
```

**Cause:** Token expired, revoked, or invalid.

**Remediation:**
1. Run `tank logout`
2. Run `tank login` for fresh token
3. Verify with `tank whoami`
4. Retry publish

## Authorization Errors

### 403 Permission denied

```
You don't have permission to publish to this organization
```

**Cause:** User is not a member of the organization, or lacks publish rights.

**Remediation:**
1. Verify org membership with org admin
2. Confirm your account has `publish` role
3. If using personal scope, remove `@org/` prefix
4. Contact org owner for access

### 403 Package name reserved

**Cause:** Package name is reserved or protected.

**Remediation:**
1. Choose a different package name
2. If you own the name, contact support

## Version Errors

### 409 Version already exists

```
Version already exists. Bump the version in skills.json
```

**Cause:** The version in `skills.json` is already published.

**Remediation:**
1. Update `version` in `skills.json`:
   - Patch: `1.0.0` → `1.0.1` (bug fixes)
   - Minor: `1.0.0` → `1.1.0` (new features)
   - Major: `1.0.0` → `2.0.0` (breaking changes)
2. Run `tank publish --dry-run`
3. Run `tank publish`

## Manifest Errors

### No skills.json found

```
No skills.json found in <directory>. Run: tank init
```

**Cause:** Missing manifest file in target directory.

**Remediation:**
1. Navigate to skill directory
2. Run `tank init`
3. Edit generated `skills.json`
4. Retry publish

### Failed to read or parse skills.json

```
Failed to read or parse skills.json
```

**Cause:** JSON syntax error or file not readable.

**Remediation:**
1. Validate JSON syntax: `cat skills.json | jq .`
2. Fix any syntax errors (trailing commas, missing quotes)
3. Ensure file is readable
4. Retry dry-run

### Invalid skills.json schema

```
Invalid skills.json: <path> <message>
```

**Cause:** Manifest doesn't conform to schema.

**Common schema errors:**

| Error | Fix |
|-------|-----|
| `name: does not match pattern` | Use lowercase, hyphens, optional @scope/ |
| `name: max length exceeded` | Keep name under 214 chars |
| `version: does not match pattern` | Use semver X.Y.Z format |
| `permissions: additional properties` | Use only network/filesystem/subprocess |
| `description: max length exceeded` | Keep under 500 chars |

## Package Errors

### Missing SKILL.md

```
SKILL.md not found in package
```

**Cause:** Required `SKILL.md` file is missing.

**Remediation:**
1. Create `SKILL.md` in skill directory
2. Add YAML frontmatter with `name` and `description`
3. Add skill instructions in Markdown body
4. Retry publish

### Package too large

```
Package exceeds maximum size (50MB compressed)
```

**Cause:** Compressed tarball exceeds 50MB limit.

**Remediation:**
1. Create `.tankignore` file
2. Exclude large files:
   ```
   node_modules
   .git
   *.mp4
   *.zip
   dist/
   build/
   coverage/
   ```
3. Run `tank publish --dry-run` to check size
4. Retry publish

### Too many files

```
Package exceeds maximum file count (1000 files)
```

**Cause:** Package contains more than 1000 files.

**Remediation:**
1. Create `.tankignore` file
2. Exclude unnecessary files:
   ```
   node_modules
   .git
   **/*.test.ts
   **/*.spec.ts
   coverage/
   .next/
   ```
3. Run `tank publish --dry-run` to check file count
4. Retry publish

### Unsafe path detected

```
Unsafe path detected: <path>
```

**Cause:** Package contains symlinks, absolute paths, or path traversal.

**Remediation:**
1. Remove symlinks from skill directory
2. Ensure no absolute paths in file references
3. Remove any `..` path components
4. Retry publish

## Network Errors

### Upload failed

```
Failed to upload tarball: <status> <statusText>
```

**Cause:** Network error during tarball upload.

**Remediation:**
1. Check network connectivity
2. Retry once
3. If persists, check `tankpkg.dev` status
4. Try again after short wait

### Confirm failed

```
Failed to confirm publish: <error>
```

**Cause:** Server error during publish confirmation.

**Remediation:**
1. Check error message for specifics
2. Verify package wasn't partially published: `tank info <name>`
3. If not published, retry from dry-run
4. Contact support if error persists

## Security Errors

### Security scan failed

```
Security scan failed: <reason>
```

**Cause:** Package failed security validation.

**Remediation:**
1. Review scan failure reason
2. Remove or fix flagged content
3. Re-run `tank audit ./skill-dir`
4. Fix identified issues
5. Retry publish

## Timeout Errors

### Login timeout

```
Login timed out after 5 minutes
```

**Cause:** Browser auth not completed within timeout.

**Remediation:**
1. Run `tank login` again
2. Complete browser auth within 5 minutes
3. If browser doesn't open, manually visit printed URL

### API timeout

**Cause:** API request timed out.

**Remediation:**
1. Retry the operation
2. Check network stability
3. Try during off-peak hours

## Error Resolution Flowchart

```
Error occurred
    │
    ├─► Auth error (401/Not logged in)
    │       └─► tank login → retry
    │
    ├─► Permission error (403)
    │       └─► Check org membership → contact admin
    │
    ├─► Version error (409)
    │       └─► Bump version → dry-run → publish
    │
    ├─► Manifest error
    │       └─► Fix JSON/schema → dry-run → publish
    │
    ├─► Package error
    │       └─► Add files/fix limits → dry-run → publish
    │
    └─► Network/timeout
            └─► Retry → check network → contact support
```
