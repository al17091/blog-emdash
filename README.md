# web-s (EmDash)

This repository is an EmDash-based blog (Astro SSR + EmDash).

- Local dev: SQLite + local media storage
- k3s (production): Postgres (e.g. CNPG) + persistent uploads

## Local Development

1. Install dependencies

```bash
pnpm install
```

2. Initialize DB and seed (first time only)

```bash
pnpm bootstrap
```

3. Start the dev server

```bash
pnpm dev
```

4. Open in your browser

- Site: `http://localhost:4321`
- Admin UI: `http://localhost:4321/_emdash/admin`

Note: if `pnpm dev` prints a different port, use the URL shown in the terminal.

## Commands

```bash
# Build
pnpm build

# Start production server (after build)
pnpm start
```

## Production Seeding (Important)

Updating `seed/seed.json` does not automatically update your production database. If you use EmDash + DB in production, you must apply the seed after deploying.

- Local (SQLite): `pnpm bootstrap` (migrations + seed)
- Local (SQLite, after changing `seed/seed.json`): `pnpm seed:update` (re-apply seed and update existing schema/fields)
- Production (Postgres): run `node ./scripts/emdash-seed.mjs --on-conflict update` with `DATABASE_URL` set (the Helm chart can do this automatically)

If you want posts/users/settings/uploads to persist in production, make sure `data.db` and `uploads/` are stored on persistent storage (some platforms recreate containers and wipe the filesystem).

## Deploy (k3s + Helm)

This repo includes:

- Production `Dockerfile` (Astro server)
- Helm chart at `charts/lab-laboratory/`

### 1) Build & push the image

Build the container and push it to your registry (example uses GHCR):

```bash
docker build -t ghcr.io/al17091/web-s:$(git rev-parse --short HEAD) .
docker push ghcr.io/al17091/web-s:$(git rev-parse --short HEAD)
```

### 2) Install/upgrade with Helm

Create a small values file (example):

```yaml
# values.prod.yaml
image:
  repository: ghcr.io/al17091/web-s
  tag: "<git-sha>"

database:
  engine: postgres
  urlFromSecret:
    name: "<cnpg-app-secret>"
    key: uri

env:
  # Recommended for passkeys / public URL generation behind TLS proxy
  EMDASH_SITE_URL: "https://engineerlab.jp"

ingress:
  enabled: true
  className: traefik
  hosts:
    - host: engineerlab.jp
      paths:
        - path: /
          pathType: Prefix

persistence:
  enabled: true
  size: 2Gi
```

Then deploy:

```bash
helm upgrade --install lab charts/lab-laboratory -n lab --create-namespace -f values.prod.yaml
```

Notes:

- The chart expects Postgres in production (e.g. CNPG). Set `database.urlFromSecret` (or `database.url`) to provide `DATABASE_URL`.
- The chart mounts a volume at `/data` and the container persists uploads there (`uploads/` is symlinked to `/data/uploads`).
- A Helm hook Job runs `node ./scripts/emdash-seed.mjs` (post-install/upgrade) by default. You can disable it via `seedJob.enabled=false`.

## Notes

- SQLite DB: `data.db`
- Media uploads: `uploads/`
- Both are ignored by `.gitignore`

## Showing Admin Links

Admin links are hidden by default. To show them in the UI, set:

```bash
PUBLIC_SHOW_ADMIN_LINK=1 pnpm dev
```
