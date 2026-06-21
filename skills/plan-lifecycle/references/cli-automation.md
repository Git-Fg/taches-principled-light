# CLI and API Automation Reference

## Sections
- [Deployment Platforms](#deployment-platforms)
- [Payment & Billing](#payment--billing)
- [Databases & Backend](#databases--backend)
- [Version Control & CI/CD](#version-control--cicd)
- [Build Tools & Testing](#build-tools--testing)
- [Environment Configuration](#environment-configuration)
- [When Claude Must Ask for Help](#when-claude-must-ask-for-help)
- [Quick Reference](#quick-reference)
- [Decision Tree](#decision-tree)
- [Summary](#summary)

---

**Core principle:** If it has a CLI or API, Claude does it. Never ask the human to perform manual steps that Claude can automate.

---

## Deployment Platforms

### Vercel ⚠️ Verify current syntax
**CLI:** `vercel`

**What Claude automates:**
- Create and deploy projects: `vercel --yes`
- Set environment variables: `vercel env add KEY production`
- Link to git repo: `vercel link`
- Trigger deployments: `vercel --prod`
- Get deployment URLs: `vercel ls`
- Manage domains: `vercel domains add example.com`

**Never ask human to:**
- Visit vercel.com/new to create project
- Click through dashboard to add env vars
- Manually link repository

### Railway
**CLI:** `railway`

**What Claude automates:**
- Create and deploy projects: `railway init` and `railway up`
- Set environment variables: `railway variables set KEY=VALUE`
- Link to existing projects: `railway link`
- Run local code in Railway environment: `railway run`
- Manage plugins (Redis, Postgres, etc.): `railway add`

**Never ask human to:**
- Visit railway.app to create project
- Click through dashboard to add env vars
- Manually provision databases

### Fly.io
**CLI:** `fly`

**What Claude automates:**
- Launch app: `fly launch --no-deploy`
- Deploy: `fly deploy`
- Set secrets: `fly secrets set KEY=value`
- Scale: `fly scale count 2`

### Cloudflare
**CLI:** `wrangler` (Workers, R2, Pages, D1)
**Can automate:**
- Deploy Workers via `wrangler deploy`
- Create D1 databases via `wrangler d1 create`
- Manage R2 buckets via `wrangler r2`
- Pages deployments via `wrangler pages deploy`

**Cannot automate:** Domain registrar operations (use web dashboard)

### AWS
**CLI:** `aws` (via AWS CLI v2)
**Can automate:**
- S3 operations via `aws s3`
- Lambda deployments via `aws lambda`
- ECS tasks via `aws ecs`
- CloudFormation stacks

**Cannot automate:** IAM role creation (requires human approval for security), billing operations

### GCP
**CLI:** `gcloud`
**Can automate:**
- GCS operations via `gsutil`
- Cloud Functions deployments via `gcloud functions deploy`
- Cloud Run via `gcloud run deploy`

**Cannot automate:** Project creation (requires web console), billing

---

## Payment & Billing

### Stripe
**CLI:** `stripe`

**What Claude automates:**
- Create webhook endpoints: `stripe listen --forward-to localhost:3000/api/webhooks`
- Trigger test events: `stripe trigger payment_intent.succeeded`
- Create products/prices: Stripe API via curl/fetch
- Manage customers: Stripe API via curl/fetch
- Check webhook logs: `stripe webhooks list`

**Never ask human to:**
- Visit dashboard.stripe.com to create webhook
- Click through UI to create products
- Manually copy webhook signing secret

---

## Databases & Backend

### Supabase
**CLI:** `supabase`

**What Claude automates:**
- Initialize project: `supabase init`
- Link to remote: `supabase link --project-ref {ref}`
- Create migrations: `supabase migration new {name}`
- Push migrations: `supabase db push`
- Generate types: `supabase gen types typescript`
- Deploy functions: `supabase functions deploy {name}`

**Never ask human to:**
- Visit supabase.com to create project manually
- Click through dashboard to run migrations
- Copy/paste connection strings

**Note:** Initial project creation may require web dashboard, but all subsequent work is CLI-automated.

### Upstash (Redis/Kafka)
**CLI:** `upstash`

**What Claude automates:**
- Create Redis database: `upstash redis create {name} --region {region}`
- Get connection details: `upstash redis get {id}`

### PlanetScale
**CLI:** `pscale`

**What Claude automates:**
- Create database: `pscale database create {name} --region {region}`
- Create branch: `pscale branch create {db} {branch}`
- Deploy request: `pscale deploy-request create {db} {branch}`
- Connection string: `pscale connect {db} {branch}`

---

## Version Control & CI/CD

### GitHub
**CLI:** `gh`

**What Claude automates:**
- Create repo: `gh repo create {name} --public/--private`
- Create issues: `gh issue create --title "{title}" --body "{body}"`
- Create PR: `gh pr create --title "{title}" --body "{body}"`
- Manage secrets: `gh secret set {KEY}`
- Trigger workflows: `gh workflow run {name}`
- Check status: `gh run list`

---

## Build Tools & Testing

### Node/npm/pnpm/bun

**What Claude automates:**
- Install dependencies: `npm install`, `pnpm install`, `bun install`
- Run builds: `npm run build`
- Run tests: `npm test`, `npm run test:e2e`
- Type checking: `tsc --noEmit`

### Bun
**CLI:** `bun`
**Can automate:**
- Install via `bun install`
- Run scripts via `bun run`
- Build via `bun build`
- Test via `bun test`

**Note:** Bun is a modern JavaScript runtime and package manager, drop-in replacement for npm/yarn.

### Xcode (macOS/iOS)
**CLI:** `xcodebuild`

**What Claude automates:**
- Build project: `xcodebuild -project App.xcodeproj -scheme App build`
- Run tests: `xcodebuild test -project App.xcodeproj -scheme App`
- Archive: `xcodebuild archive -project App.xcodeproj -scheme App`

---

## Environment Configuration

### .env Files

**What Claude automates:**
- Create .env files: write directly
- Append variables: edit in place
- Read current values: read file contents

**Pattern:**
```markdown
### Task: Configure environment variables
Files: .env
Action: Write .env file with: DATABASE_URL, STRIPE_KEY, JWT_SECRET (generate secure values)
Verify: Read .env confirms all variables present
Done: .env exists with all required variables
```

---

## When Claude Must Ask for Help

**Truly rare cases where no CLI/API exists:**

1. **Email verification links** — Account signup requires clicking verification email
2. **SMS verification codes** — 2FA requiring phone
3. **Manual account approvals** — Platform requires human review before API access
4. **Domain DNS records at registrar** — Some registrars have no API
5. **Credit card input** — Payment methods requiring 3D Secure web flow
6. **OAuth app approval** — Some platforms require web-based app approval

For these cases: Present clearly what Claude needs and why.

---

## Quick Reference

| Action | CLI/API? | Claude does it? |
|--------|----------|-----------------|
| Deploy to Vercel | ✅ `vercel` | YES |
| Create Stripe webhook | ✅ Stripe API | YES |
| Run xcodebuild | ✅ `xcodebuild` | YES |
| Write .env file | ✅ write directly | YES |
| Create Upstash DB | ✅ `upstash` CLI | YES |
| Install npm packages | ✅ `npm` | YES |
| Create GitHub repo | ✅ `gh` | YES |
| Run tests | ✅ `npm test` | YES |
| Create Supabase project | ⚠️ Web dashboard | NO (then CLI for everything else) |
| Click email verification link | ❌ No API | NO |
| Enter credit card with 3DS | ❌ No API | NO |

**Default answer: YES.** Unless explicitly in the "NO" category, Claude automates it.

---

## Decision Tree

```
Task requires external resource?
    │
    ▼
Does it have CLI/API?
    │
   YES          NO
    │            │
    ▼            ▼
Claude does    Rare: email links,
it via CLI     2FA, manual approvals
```

---

## Summary

**The rule:** If Claude CAN do it, Claude MUST do it.

Verification (checking work looks/behaves correctly) is done via:
- Automated tests (`npm test`)
- Build verification (`npm run build`)
- API checks (`curl` commands)
- File existence checks

Only verify things that genuinely require human judgment (visual appearance, UX feel).
