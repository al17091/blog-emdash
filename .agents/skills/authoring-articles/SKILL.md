---
name: authoring-articles
description: Standard operating procedure for researching, authoring, converting to Portable Text, optimizing SEO metadata, validating schemas, and synchronizing blog articles to staging on EmDash.
---

# Content Authoring Runbook for EmDash

This skill defines the end-to-end standard operating procedure (SOP) for drafting, formatting, SEO-optimizing, validating, and publishing technical and travel articles on an EmDash site.

---

## 1. Editorial Principles & Language Policy

- **Tech Articles (English)**:
  - **Title Length**: Strictly **50 characters or less** (2-3 lines max, punchy & direct).
  - **Audience**: Global engineering community, SREs, security architects.
  - **Depth**: A4 report class / engineering whitepaper. Must include incident timelines, kernel/network root causes, ASCII flow diagrams, concrete YAML/CLI configurations, and benchmark metrics.
- **Travel & Hiking Articles (Japanese)**:
  - **Title Length**: Strictly **50 characters or less** (e.g. 25-35 chars).
  - **Audience**: Domestic hikers, outdoor enthusiasts, hot-spring seekers.
  - **Depth**: Comprehensive trail guides. Must include course statistics (CT, distance, elevation), transit logistics, stage-by-stage trail conditions, photo placeholders (`[📷 写真: ...]`), post-hike onsen/gourmet details, and seasonal gear advice.
- **Anonymization & Masking Policy (CRITICAL)**:
  - **Domains**: NEVER use actual production or internal domains in article text, code blocks, or curl commands.
    - Public domains: `*.engineerlab.jp` ➔ `*.example.com`
    - Internal domains: `*.lab.internal`, `*.lab.local` ➔ `*.example.internal`, `*.example.local`
  - **Identities & IDs**: NEVER expose real CloudFront distribution IDs (`EDMTMX...`), AWS account IDs (`195275...`), IAM user/role ARNs, internal secret values, or specific host IP addresses.
    - CloudFront / AWS IDs ➔ `<DISTRIBUTION_ID>`, `<ACCOUNT_ID>`, `E1234567890ABC`
    - Example IPs ➔ Use RFC 5737 documentation ranges (`192.0.2.x`, `198.51.100.x`, `203.0.113.x`) or generic private subnets.
- **Status Policy**:
  - Always draft new content with `status: "draft"` in `seed/seed.json` to allow author review and photo attachment before publishing.

---

## 2. EmDash Content Schema & Data Invariants

All articles reside in `seed/seed.json` under `content.posts[]`.

### Post Entry Structure
```json
{
  "id": "posts:<kebab-case-slug>",
  "slug": "<kebab-case-slug>",
  "status": "draft",
  "taxonomies": {
    "theme": ["engineering"],
    "category": ["infrastructure"],
    "tag": ["kubernetes", "storage"]
  },
  "data": {
    "title": "Clear, High-Intent Title",
    "excerpt": "SEO-optimized description (140-160 chars EN, 100-120 chars JA)",
    "content": [
      {
        "_type": "block",
        "style": "normal",
        "_key": "b_a1b2c3d4",
        "children": [
          {
            "_type": "span",
            "_key": "s_e5f6g7h8",
            "text": "Paragraph content or code block string."
          }
        ]
      }
    ]
  }
}
```

### Critical Rules:
1. **Taxonomy Names**: Must match the singular name defined in the seed's `taxonomies[]` exactly (e.g., `"category"` not `"categories"`, `"theme"` not `"themes"`, `"tag"` not `"tags"`).
2. **Portable Text Blocks**: Every block and span MUST have a unique `_key` string.
3. **Styles**: Supported styles are `"normal"`, `"h2"`, `"h3"`, and `"blockquote"`.

---

## 3. SEO & Meta Description Standards

EmDash automatically binds article metadata to public `<head>` tags via `getSeoMeta()` and Schema.org JSON-LD:
- `data.title` ➔ `<title>{title} | {siteTitle}</title>`, `og:title`, `twitter:title`
- `data.excerpt` ➔ `<meta name="description">`, `og:description`, `twitter:description`, JSON-LD `description`
- `slug` ➔ `<link rel="canonical" href=".../posts/{slug}">`

### Character Count Guidelines for SERP Click-Through:
- **Japanese (Travel)**: **100〜122 characters**. Focus on search intent: `コースタイム`, `アクセス`, `日帰り温泉`, `難易度`, `名物グルメ`.
- **English (Tech)**: **140〜155 characters**. Focus on high-intent technical terms: `Root cause`, `Post-mortem`, `Architecture`, `Kubernetes`, `Benchmark`, `Troubleshooting`.

### Admin UI SEO Sidebar Synchronization (`_emdash_seo` Table):
The Admin UI's right-hand SEO sidebar reads directly from the `_emdash_seo` table (keyed by `collection` and `content_id`).
When applying seeds, always ensure `scripts/emdash-seed.mjs` runs its post-seed SQL sync to populate:
- `seo_title` = `title`
- `seo_description` = `excerpt`
- `seo_canonical` = `https://blog-stg.lab.internal/posts/{slug}`

---

## 4. Multi-File Generation Architecture

To author articles without managing massive single-file JSONs, use the modular generator scripts in `scripts/`:

| File | Purpose |
| :--- | :--- |
| `scripts/articles_travel.py` | Python dictionary holding Japanese mountain/hiking articles |
| `scripts/articles_tech_infra.py` | Python dictionary holding Infrastructure, Storage, & Networking articles |
| `scripts/articles_tech_sec_ai.py` | Python dictionary holding Security, Telemetry, & AI integration articles |
| `scripts/apply_all_articles.py` | Master parser converting Markdown to Portable Text blocks and updating `seed/seed.json` |
| `scripts/emdash-seed.mjs` | Database seed applier with automated `_emdash_seo` synchronization |

### Running the Generator:
```bash
# 1. Update the content/markdown in scripts/articles_*.py
# 2. Run master updater to populate seed/seed.json
python3 scripts/apply_all_articles.py
```

---

## 5. Local Quality Gates (Pre-Commit Invariants)

Always run all validation checks before committing:

```bash
# 1. Verify no sensitive production/internal domains or IDs are leaked in seed.json
python3 -c "
import json, sys
d = json.load(open('seed/seed.json'))
leaks = []
for post in d['content']['posts']:
    text = json.dumps(post)
    for term in ['engineerlab.jp', 'lab.internal', 'EDMTMX', '195275637149']:
        if term in text:
            leaks.append((post.get('slug'), term))
if leaks:
    print('SECURITY ALERT: Sensitive terms found in posts:', leaks)
    sys.exit(1)
print('✔ Anonymization check passed: Zero sensitive domains or IDs detected.')
"

# 2. Validate seed JSON schema against EmDash CLI
npx emdash seed seed/seed.json --validate

# 3. Test server build with Astro
pnpm build
```

---

## 6. Deployment & Staging Synchronization

### Git Workflow:
```bash
git add seed/seed.json scripts/
git commit -S -m "content: add <topic> article in draft mode"
git push origin develop
```

### Staging Cluster Deployment (`blog-stg`):
```bash
# 1. Locate staging pod
POD=$(kubectl get pod -n blog-stg -l app=blog-emdash -o jsonpath='{.items[0].metadata.name}')

# 2. Copy updated seed file to pod
kubectl cp seed/seed.json blog-stg/$POD:/app/seed/seed.json

# 3. Apply seed and trigger SEO metadata sync
kubectl exec -n blog-stg $POD -- node scripts/emdash-seed.mjs --on-conflict update

# 4. (Optional) Verify primary database records
PRIMARY=$(kubectl get pod -n blog-stg -l cnpg.io/instanceRole=primary -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n blog-stg $PRIMARY -c postgres -- psql -U postgres -d app -c "
  SELECT s.content_id, p.slug, left(s.seo_title, 35) as title, length(s.seo_description) as desc_len
  FROM _emdash_seo s JOIN ec_posts p ON s.content_id = p.id;
"
```

---

## 7. Review & Publishing Checklist

1. Navigate to the Admin UI: `https://blog-stg.lab.internal/_emdash/admin`.
2. Open **Posts** ➔ **Drafts**.
3. Review the article:
   - Check layout and markdown formatting.
   - For travel posts, upload and drag photos into `[📷 写真: ...]` placeholders.
   - Verify the right-hand **SEO** panel contains the Title, Meta Description, and Canonical URL.
4. When ready, click **Publish** (公開).
   - Once published, EmDash automatically exposes the article on `https://blog-stg.lab.internal/posts/{slug}` and registers it in `https://blog-stg.lab.internal/sitemap-posts.xml`.

---

## 8. Production Promotion & GitHub Workflow

When promoting verified articles or feature updates from staging/develop to production:

### 8.1 Invariants
- **Host-Signed Commits**: Always execute `git commit -S` and `git tag -s` on the host machine.
- **CI Gate**: Strictly wait for `CI (Test & Scan)` to complete successfully before merging.
- **PR Audit History**: Always merge via GitHub PR using a **merge commit** (`--merge`). Never squash or rebase when promoting to `main`.
- **Anonymization Invariant**: Verify all internal domains and AWS resource IDs are sanitized before publishing.

### 8.2 GitHub Release Runbook via `gh` CLI:
```bash
# 1. Commit and push changes on develop
git add seed/seed.json src/
git commit -S -m "chore(content): publish verified articles"
git push origin develop

# 2. Create Pull Request using gh CLI
docker exec lab-infra-workspace-1 gh pr create \
  --repo al17091/blog-emdash \
  --base main \
  --head develop \
  --title "release: <brief title>" \
  --body "## Summary\n\n<details>"

# 3. Wait for CI to pass
docker exec lab-infra-workspace-1 gh run list --repo al17091/blog-emdash --limit 3
docker exec lab-infra-workspace-1 gh run watch <RUN_ID> --repo al17091/blog-emdash --exit-status
docker exec lab-infra-workspace-1 gh pr checks <PR_NUM> --repo al17091/blog-emdash

# 4. Merge via merge commit (preserving PR audit trail)
docker exec lab-infra-workspace-1 gh pr merge <PR_NUM> --merge --repo al17091/blog-emdash

# 5. Tag release for CD build & push
git checkout main
git pull origin main
git tag -s vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z

# 6. Apply seed update to production database
POD=$(kubectl get pod -n blog -l app=blog-emdash -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n blog $POD -- node scripts/emdash-seed.mjs --on-conflict update

# 7. Reconcile develop branch
git checkout develop
git pull origin develop
```


