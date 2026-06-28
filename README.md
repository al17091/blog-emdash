# Blog EmDash

[![CI](https://github.com/al17091/blog-emdash/actions/workflows/ci.yml/badge.svg)](https://github.com/al17091/blog-emdash/actions/workflows/ci.yml)
[![CD](https://github.com/al17091/blog-emdash/actions/workflows/cd.yml/badge.svg)](https://github.com/al17091/blog-emdash/actions/workflows/cd.yml)

A modern, dynamic web application and blog built with Astro SSR and the EmDash CMS. Designed for a Pull-based GitOps deployment via ArgoCD on a K3s cluster.

## Architecture

- **Frontend / Framework**: Astro (SSR)
- **CMS**: EmDash
- **Database**: SQLite (Stored in a Persistent Volume)
- **CI/CD**: GitHub Actions
- **Infrastructure**: K3s, ArgoCD, Traefik (Ingress)
- **Container Registry**: GitHub Container Registry (GHCR)

## 🚀 Local Development

### Prerequisites
- Node.js 24+
- `pnpm` (v9+)
- Docker & Docker Compose (optional, for containerized dev)

### Standard Setup

1. **Install dependencies**
   ```bash
   pnpm install
   ```

2. **Initialize DB and seed (first time only)**
   ```bash
   pnpm bootstrap
   ```

3. **Start the dev server**
   ```bash
   pnpm dev
   ```

4. **Access the application**
   - Site: `http://localhost:4321`
   - Admin UI: `http://localhost:4321/_emdash/admin`

### Docker Compose (Devcontainer)

You can also run the development environment purely in Docker without installing Node.js on your host:

```bash
docker-compose up --build
```
This will mount your local directory and use `Dockerfile.dev` to provide a hot-reloading dev server on port 4321.

## 📦 CI/CD & Deployment

This repository uses a fully automated CI/CD pipeline via GitHub Actions.

### Continuous Integration (`ci.yml`)
Runs on every push or pull request to the `main` and `develop` branches:
- **Typecheck/Lint**: Ensures code quality (`pnpm typecheck`).
- **Security Scan (Trivy)**: Scans the repository filesystem for vulnerabilities.
- **DAST Scan (OWASP ZAP)**: Performs a baseline dynamic security scan against the built application.

### Continuous Deployment (`cd.yml`)
Runs automatically when a new version tag (e.g., `v1.0.0`) is pushed:
- Builds the production Docker image using `Dockerfile`.
- Pushes the image to GHCR (`ghcr.io/al17091/blog-emdash`) tagged with both the version and `latest`.

### Kubernetes / ArgoCD

The `k8s/` directory contains all necessary manifests for deploying the application to a K3s cluster via ArgoCD.

- **Data Persistence**: A 1Gi PersistentVolumeClaim (`pvc.yaml`) is mounted to `/data` in the container. `docker/entrypoint.sh` automatically symlinks the SQLite database (`data.db`) and uploaded media (`uploads/`) to this volume, ensuring data is not lost upon Pod restarts.
- **Ingress**: `ingressroute.yaml` and `middleware.yaml` configure Traefik to expose the service and force HTTPS redirection.

To deploy a new release via ArgoCD:
1. Update `k8s/kustomization.yaml` to point the `ghcr.io/al17091/blog-emdash` image to the new tag (e.g., `v1.0.1`) and commit the change.
2. Push a new Git tag (e.g., `v1.0.1`).
3. GitHub Actions will build and push the new image. ArgoCD will sync the updated manifests and deploy the new version.

## 🛠️ Notes

- **Admin Links**: Admin UI links are hidden from the frontend by default. To show them locally, start the server with:
  ```bash
  PUBLIC_SHOW_ADMIN_LINK=1 pnpm dev
  ```
- **Seeding in Production**: Updating `seed/seed.json` does not automatically overwrite a production database. To re-apply the seed locally, run `pnpm seed:update`.
