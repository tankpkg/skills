# Deployment Workflows

Sources: Vercel CLI docs (2026), production GitHub repos (midday-ai, ChatGPTNextWeb, polarsource/polar)

Covers: CI/CD patterns, preview and production workflows, promote, rollback,
rolling releases, monorepo deployment, deploy hooks, and prebuilt deploys.

## The 3-Step Pattern

Every CI/CD pipeline follows the same core sequence:

```bash
vercel pull --yes --environment=production --token=$VERCEL_TOKEN
vercel build --prod --token=$VERCEL_TOKEN
vercel deploy --prod --prebuilt --archive=tgz --token=$VERCEL_TOKEN
```

**Step 1 (pull)**: Syncs environment variables and project settings to `.vercel/`.
**Step 2 (build)**: Builds using Vercel's pipeline. Output goes to `.vercel/output/`.
**Step 3 (deploy)**: Uploads pre-built artifacts. `--archive=tgz` compresses for speed.

For preview deployments, remove `--prod` from build and deploy, use
`--environment=preview` for pull.

## GitHub Actions

### Production Deployment

```yaml
name: Deploy Production
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    env:
      VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
      VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
    steps:
      - uses: actions/checkout@v4
      - name: Install Vercel CLI
        run: npm install -g vercel
      - name: Pull, Build, Deploy
        run: |
          vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}
          vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}
          vercel deploy --prod --prebuilt --archive=tgz --token=${{ secrets.VERCEL_TOKEN }}
```

### Preview Deployment

```yaml
name: Deploy Preview
on:
  pull_request:
jobs:
  deploy:
    runs-on: ubuntu-latest
    env:
      VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
      VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
    steps:
      - uses: actions/checkout@v4
      - name: Install Vercel CLI
        run: npm install -g vercel
      - name: Pull, Build, Deploy
        id: deploy
        run: |
          vercel pull --yes --environment=preview --token=${{ secrets.VERCEL_TOKEN }}
          vercel build --token=${{ secrets.VERCEL_TOKEN }}
          url=$(vercel deploy --prebuilt --archive=tgz --token=${{ secrets.VERCEL_TOKEN }})
          echo "url=$url" >> $GITHUB_OUTPUT
      - name: Comment PR
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: `Preview: ${{ steps.deploy.outputs.url }}`
            })
```

### Required Secrets

| Secret | Where to Find |
|--------|---------------|
| `VERCEL_TOKEN` | vercel.com/account/tokens |
| `VERCEL_ORG_ID` | `.vercel/project.json` after `vercel link` |
| `VERCEL_PROJECT_ID` | `.vercel/project.json` after `vercel link` |

## GitLab CI

```yaml
deploy_preview:
  stage: deploy
  except:
    - main
  script:
    - npm install -g vercel
    - vercel pull --yes --environment=preview --token=$VERCEL_TOKEN
    - vercel build --token=$VERCEL_TOKEN
    - vercel deploy --prebuilt --token=$VERCEL_TOKEN

deploy_production:
  stage: deploy
  only:
    - main
  script:
    - npm install -g vercel
    - vercel pull --yes --environment=production --token=$VERCEL_TOKEN
    - vercel build --prod --token=$VERCEL_TOKEN
    - vercel deploy --prod --prebuilt --token=$VERCEL_TOKEN
```

## Bitbucket Pipelines

```yaml
pipelines:
  branches:
    main:
      - step:
          script:
            - npm install -g vercel
            - vercel pull --yes --environment=production --token=$VERCEL_TOKEN
            - vercel build --prod --token=$VERCEL_TOKEN
            - vercel deploy --prod --prebuilt --token=$VERCEL_TOKEN
    feature/*:
      - step:
          script:
            - npm install -g vercel
            - vercel pull --yes --environment=preview --token=$VERCEL_TOKEN
            - vercel build --token=$VERCEL_TOKEN
            - vercel deploy --prebuilt --token=$VERCEL_TOKEN
```

## Staged Production Deployment

Deploy a production build without assigning it to the production domain.
Test first, then alias.

```bash
DEPLOYMENT_URL=$(vercel deploy --prod --skip-domain --token=$VERCEL_TOKEN)
# Run smoke tests against $DEPLOYMENT_URL...
vercel alias set $DEPLOYMENT_URL production-domain.com --token=$VERCEL_TOKEN
```

## Promote from Preview

Promote a preview deployment to production without rebuilding.

```bash
vercel promote [deployment-url]
vercel promote status                    # Check progress
```

**Warning**: Promoted deployments use production environment variables, not
preview variables. If preview and production env vars differ, behavior may change.

## Rollback

Instantly revert production to a previous deployment. No rebuild required.

```bash
vercel rollback                          # Previous deployment (all plans)
vercel rollback [deployment-url]         # Specific deployment (Pro/Enterprise)
vercel rollback status                   # Check status
```

Undo a rollback with `vercel promote [deployment-url]`.

Hobby plan: can only roll back to the immediately previous deployment.
Pro/Enterprise: can roll back to any previous deployment.

## Rolling Releases

Gradually roll traffic to a new deployment in stages.

```bash
vercel rolling-release configure --cfg='{
  "enabled": true,
  "advancementType": "automatic",
  "stages": [
    {"targetPercentage": 10, "duration": 5},
    {"targetPercentage": 50, "duration": 10},
    {"targetPercentage": 100}
  ]
}'
```

Deploy triggers rolling release automatically:

```bash
vercel deploy --prod                     # Starts at 10%
vercel rolling-release fetch             # Monitor rollout
vercel rolling-release approve --dpl=... # Manual advancement (if manual mode)
```

## Redeploy

Rebuild an existing deployment with fresh dependencies and env vars.

```bash
vercel redeploy [deployment-url]
```

Use when: retrying failed builds, applying updated dependencies, refreshing env vars.

## Deploy Hooks

Trigger deployments via HTTP POST without pushing code.

Create hooks in Project Settings -> Git -> Deploy Hooks.
Each hook is tied to a specific branch.

```bash
curl -X POST https://api.vercel.com/v1/integrations/deploy/prj_xxx/yyy
```

Use cases: CMS content changes, scheduled deployments, external triggers.

## Webhooks

Listen to deployment events:

| Event | Description |
|-------|-------------|
| `deployment.created` | Deployment started |
| `deployment.succeeded` | Build and deploy completed |
| `deployment.failed` | Deployment failed |
| `deployment.ready` | Deployment is live |
| `deployment.canceled` | Deployment was canceled |

Configure in Project Settings -> Webhooks.

## Monorepo Deployment

### Turborepo + Vercel

```bash
export TURBO_TOKEN=$VERCEL_TOKEN
export TURBO_TEAM=$VERCEL_ORG_ID
turbo build --filter=web
vercel deploy --prebuilt --token=$VERCEL_TOKEN
```

Remote caching is automatic on Vercel. Achieves 80-95% cache hit rates.

### Per-App Configuration

Each app in a monorepo is a separate Vercel project:

```json
{
  "buildCommand": "pnpm --filter=web build",
  "installCommand": "pnpm install --frozen-lockfile",
  "outputDirectory": "apps/web/.next"
}
```

Link each app separately:

```bash
cd apps/web && vercel link --yes --project web-app
cd apps/api && vercel link --yes --project api-app
```

Or link the entire repo: `vercel link --repo`.

### Nx Monorepo

Add `runtimeCacheInputs` to prevent stale env var caching:

```json
{ "runtimeCacheInputs": ["echo $MY_VERCEL_ENV"] }
```

## Prebuilt Deployment

Build without sharing source code with Vercel.

```bash
vercel build --prod
vercel deploy --prod --prebuilt
```

**Limitations**:
- No Skew Protection (no deployment ID at build time)
- Missing system environment variables (VERCEL_URL, etc.) during build
- Git metadata not available

Prefer Git-based deployments when Skew Protection or system env vars are needed.

## Deployment Metadata

Tag deployments with custom metadata for tracking:

```bash
vercel deploy --meta commit=$GITHUB_SHA --meta author=$GITHUB_ACTOR
```

Query metadata via `vercel inspect` or the REST API.

## Zero-Downtime Deployment

All Vercel deployments are atomic:
1. New deployment builds in isolation.
2. Once ready, traffic switches instantly.
3. Old deployment remains available for rollback.

No configuration needed. Downtime is not possible during normal deployments.
