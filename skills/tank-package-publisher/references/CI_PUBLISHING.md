# CI/CD Publishing for Tank Skills

Guide for automating Tank skill publishing in continuous integration pipelines.

## Prerequisites

- Tank CLI installed in CI environment
- Authentication token available as secret
- `skills.json` with valid manifest

## Authentication in CI

### GitHub Actions

Store Tank token as a repository secret:

1. Go to Settings → Secrets and variables → Actions
2. Add secret: `TANK_TOKEN`
3. Use in workflow:

```yaml
- name: Configure Tank
  run: echo "$TANK_TOKEN" | tank login --token
  env:
    TANK_TOKEN: ${{ secrets.TANK_TOKEN }}
```

### GitLab CI

Add variable in Settings → CI/CD → Variables:

```yaml
configure_tank:
  script:
    - echo "$TANK_TOKEN" | tank login --token
  variables:
    TANK_TOKEN: $TANK_TOKEN
```

### CircleCI

Add context or project environment variable:

```yaml
- run:
    name: Configure Tank
    command: echo "$TANK_TOKEN" | tank login --token
```

## Basic Publish Workflow

```yaml
name: Publish Skill

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install Tank CLI
        run: npm install -g @tankpkg/cli
      
      - name: Configure Tank
        run: echo "$TANK_TOKEN" | tank login --token
        env:
          TANK_TOKEN: ${{ secrets.TANK_TOKEN }}
      
      - name: Validate manifest
        run: tank publish --dry-run
        working-directory: skills/my-skill
      
      - name: Publish
        run: tank publish
        working-directory: skills/my-skill
```

## Version Management

### Option 1: Tag-based Versioning

Extract version from git tag:

```yaml
- name: Update version from tag
  run: |
    VERSION=${GITHUB_REF#refs/tags/v}
    jq --arg v "$VERSION" '.version = $v' skills.json > skills.json.tmp
    mv skills.json.tmp skills.json
  working-directory: skills/my-skill
```

### Option 2: Conventional Commits

Use semantic-release or similar:

```yaml
- name: Semantic Release
  uses: cycjimmy/semantic-release-action@v4
  with:
    semantic_version: 22
    extra_plugins: |
      @semantic-release/exec
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

With `.releaserc`:

```json
{
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    ["@semantic-release/exec", {
      "publishCmd": "tank publish"
    }]
  ]
}
```

### Option 3: Manual Version Bump

Require manual version update before merge:

```yaml
- name: Check version changed
  run: |
    git fetch origin main
    if git diff origin/main -- skills/my-skill/skills.json | grep -q '"version"'; then
      echo "Version changed, proceeding"
    else
      echo "Error: Version not bumped"
      exit 1
    fi
```

## Monorepo Skills

For multiple skills in one repository:

```yaml
name: Publish Skills

on:
  push:
    tags:
      - 'skills/**/v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install Tank
        run: npm install -g @tankpkg/cli
      
      - name: Configure Tank
        run: echo "$TANK_TOKEN" | tank login --token
        env:
          TANK_TOKEN: ${{ secrets.TANK_TOKEN }}
      
      - name: Determine skill path
        id: skill
        run: |
          TAG=${GITHUB_REF#refs/tags/}
          SKILL_PATH=$(dirname "$TAG")
          echo "path=$SKILL_PATH" >> $GITHUB_OUTPUT
      
      - name: Validate
        run: tank publish --dry-run
        working-directory: ${{ steps.skill.outputs.path }}
      
      - name: Publish
        run: tank publish
        working-directory: ${{ steps.skill.outputs.path }}
```

Tagging: `git tag skills/playwright/v1.2.0`

## Pull Request Validation

Validate skill before merge:

```yaml
name: Validate Skill

on:
  pull_request:
    paths:
      - 'skills/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Tank
        run: npm install -g @tankpkg/cli
      
      - name: Validate manifests
        run: |
          for dir in skills/*/; do
            if [ -f "$dir/skills.json" ]; then
              echo "Validating $dir"
              tank publish --dry-run --directory "$dir" || exit 1
            fi
          done
      
      - name: Run skill tests
        run: |
          for dir in skills/*/; do
            if [ -f "$dir/scripts/test.sh" ]; then
              echo "Testing $dir"
              bash "$dir/scripts/test.sh" || exit 1
            fi
          done
```

## Security Best Practices

### Token Management

- Use repository secrets, never hardcode tokens
- Rotate tokens periodically
- Use organization-level secrets for shared access
- Limit token scope to minimum required

### Permission Scoping

```yaml
# Use fine-grained PAT or GitHub App
permissions:
  contents: read
  packages: write  # Only if publishing to GitHub Packages too
```

### Audit Trail

```yaml
- name: Log publish
  run: |
    echo "Published $(jq -r '.name' skills.json)@$(jq -r '.version' skills.json)" >> publish.log
    echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> publish.log
    echo "Actor: $GITHUB_ACTOR" >> publish.log
```

## Rollback Strategy

If publish succeeds but skill has issues:

```yaml
- name: Rollback on failure
  if: failure()
  run: |
    echo "::warning::Publish may have succeeded before failure"
    echo "Check package status: tank info $(jq -r '.name' skills.json)"
    echo "Consider unpublishing if broken"
```

Note: Tank may support deprecation or unpublish - check docs for available options.

## Caching

Speed up CI with caching:

```yaml
- name: Cache Tank config
  uses: actions/cache@v4
  with:
    path: ~/.config/tank
    key: tank-config-${{ runner.os }}
```

## Example: Complete Workflow

```yaml
name: CI/CD

on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install Tank
        run: npm install -g @tankpkg/cli
      
      - name: Validate skill
        run: tank publish --dry-run
        working-directory: skills/my-skill

  publish:
    needs: validate
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install Tank
        run: npm install -g @tankpkg/cli
      
      - name: Configure Tank
        run: echo "$TANK_TOKEN" | tank login --token
        env:
          TANK_TOKEN: ${{ secrets.TANK_TOKEN }}
      
      - name: Publish
        run: tank publish
        working-directory: skills/my-skill
      
      - name: Verify
        run: tank info $(jq -r '.name' skills.json)
        working-directory: skills/my-skill
```
