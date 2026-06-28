# Blog EmDash

[![CI](https://github.com/al17091/blog-emdash/actions/workflows/ci.yml/badge.svg)](https://github.com/al17091/blog-emdash/actions/workflows/ci.yml)
[![CD](https://github.com/al17091/blog-emdash/actions/workflows/cd.yml/badge.svg)](https://github.com/al17091/blog-emdash/actions/workflows/cd.yml)

A modern, dynamic web application and blog built with Astro SSR and the EmDash CMS. Designed for a Pull-based GitOps deployment via ArgoCD on a Kubernetes (K3s) cluster using Helm.

## Architecture

- **Frontend / Framework**: Astro (SSR)
- **CMS**: EmDash
- **Database**: PostgreSQL
- **CI/CD**: GitHub Actions
- **Infrastructure**: Helm, ArgoCD, K3s, Traefik (Ingress)
- **Container Registry**: GitHub Container Registry (GHCR)

## 🚀 Local Development

### Prerequisites
- Docker & Docker Compose

### Standard Setup

You can run the development environment purely in Docker without installing Node.js or PostgreSQL on your host:

```bash
docker-compose up -d --build
```
This will mount your local directory and start:
1. `app` container: A hot-reloading dev server on port 4321.
2. `db` container: A local PostgreSQL database (`emdash_db`).

Access the application:
- Site: `http://localhost:4321`
- Admin UI: `http://localhost:4321/_emdash/admin`

## 📦 CI/CD & Deployment

This repository uses a fully automated CI/CD pipeline via GitHub Actions.

### Continuous Integration (`ci.yml`)
Runs on every push or pull request to the `main` and `develop` branches:
- **Typecheck/Lint**: Ensures code quality (`pnpm typecheck`).
- **Security Scan (Trivy)**: Scans the repository filesystem for vulnerabilities.

> **Note on `paths-ignore`**: 
> The CI workflow is configured to skip execution if changes are made exclusively to the `helm/**` directory. This is because changes to Kubernetes manifests or Helm values do not affect the application's source code. Skipping these checks saves GitHub Actions minutes and accelerates the infrastructure deployment process.

### Continuous Deployment (`cd.yml`)
Runs automatically when a new version tag (e.g., `v1.0.0`) is pushed:
- Builds the production Docker image using `Dockerfile`.
- Pushes the image to GHCR (`ghcr.io/al17091/blog-emdash`) tagged with both the version and `latest`.
- Also ignores changes to `helm/**` to avoid redundant builds when updating infrastructure configs.

### Kubernetes / ArgoCD (Helm)

The `helm/` directory contains a Helm chart for deploying the application to a K3s cluster via ArgoCD.

- **Values Management**: By modifying `helm/values.yaml` (or having ArgoCD inject values), parameters like `ingress.host`, `image.repository`, and `image.tag` can be dynamically updated without hardcoding environment details into the manifests.
- **Data Persistence**: A 1Gi PersistentVolumeClaim (`pvc.yaml`) is mounted to `/data` in the container for storing user-uploaded media (`uploads/`).
- **Ingress**: `ingressroute.yaml` and `middleware.yaml` configure Traefik to expose the service and force HTTPS redirection.

To deploy a new release:
1. Push a new Git tag (e.g., `v1.0.1`), triggering the GitHub Actions CD pipeline.
2. Update ArgoCD parameters (or `values.yaml`) to point the `image.tag` to the new version.
3. ArgoCD will sync the Helm chart and rollout the new version automatically.

## 🗄️ Database Operations (PostgreSQL)

This application has been migrated from SQLite to PostgreSQL. For ongoing data management between PostgreSQL instances (e.g., pulling production data to local, or migrating between environments), we provide helper scripts:

### Dump Data
Creates a clean, generic SQL dump (skipping ownership and privileges) suitable for restoring:
```bash
DATABASE_URL="postgres://user:pass@host/db" ./scripts/pg-dump.sh > dump.sql
```

### Restore Data
Restores a previously generated SQL dump into a target database:
```bash
DATABASE_URL="postgres://user:pass@host/new_db" ./scripts/pg-restore.sh < dump.sql
```

## 🛠️ Utility Scripts (`scripts/`)

The `scripts/` directory contains various Node.js and Bash scripts used for project management and maintenance:

- **`emdash-seed.mjs`**: A custom seeding script that replaces the default `emdash seed` CLI command. It has been specifically designed to support PostgreSQL (which the official CLI currently lacks), allowing `pnpm bootstrap` and `pnpm seed` to apply schema migrations and seed data directly to Postgres.
- **`pg-dump.sh`**: Helper bash script to export the Postgres database as a clean SQL file.
- **`pg-restore.sh`**: Helper bash script to import an SQL file into a Postgres database.

## 📝 Notes

- **Admin Links**: Admin UI links are hidden from the frontend by default. To show them locally, set `PUBLIC_SHOW_ADMIN_LINK=1` in your environment.
