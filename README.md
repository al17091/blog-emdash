# Blog EmDash

A modern, dynamic web application and blog built with **Astro SSR** and **EmDash CMS**. Optimized for containerized environments and designed for a Pull-based GitOps deployment via **ArgoCD** on a **Kubernetes (K3s)** cluster using **Helm**.

---

## 🏗️ Architecture

```mermaid
graph TD
    Client[Browser / Client] -->|HTTPS| Traefik[Traefik IngressRoute]
    Traefik -->|Route| Astro[Astro SSR App]
    Astro -->|Read/Write| Postgres[(PostgreSQL DB)]
    Astro -->|Media Storage| PVC[Persistent Volume Claim /uploads]
    
    subgraph GitOps Workflow
        GitHub[GitHub Repo] -->|Push Tag| GHA[GitHub Actions]
        GHA -->|Build & Push| GHCR[GitHub Container Registry]
        ArgoCD[ArgoCD Cluster Operator] -->|Poll & Sync| GitHub
        ArgoCD -->|Deploy Helm Chart| Astro
    end
```

- **Frontend / Framework**: Astro (Server-Side Rendering / SSR)
- **CMS**: EmDash CMS (Integrated Admin Panel)
- **Database**: PostgreSQL (Migrated from SQLite for production grade reliability)
- **CI/CD**: GitHub Actions (Linting, trivy scans, OWASP ZAP DAST security scans, docker build)
- **Orchestration**: Helm Charts (Targeting K3s with Traefik IngressRoute)
- **Deployment**: GitOps via ArgoCD

---

## ✨ Features

- **Blazing Fast Performance**: Zero-JS by default rendering powered by Astro.
- **Embedded Editor**: Easy editing interface using the Portable Text editor inside EmDash admin interface (`/_emdash/admin`).
- **Flexible Styling**: Vanilla CSS architecture with custom themes support.
- **Content Organization**: Full support for Categories, Tags, and dynamic Theme customization.
- **Production-ready Operations**:
  - PostgreSQL adapter.
  - Multi-stage Docker builds.
  - Helm templates supporting HTTPS redirect via Traefik middlewares.
  - Automated security scans (Trivy + OWASP ZAP DAST).

---

## ⚙️ Environment Configuration

The application can be configured dynamically using the following environment variables:

| Variable | Description | Default | Required |
| :--- | :--- | :--- | :--- |
| `EMDASH_DB` | Database adapter type (`sqlite` or `postgres`/`pg`). | `sqlite` | No |
| `DATABASE_URL` | PostgreSQL connection string. | - | Yes (if `EMDASH_DB=postgres`) |
| `EMDASH_DATABASE_URL` | SQLite database file path. | `file:./data.db` | No (if `EMDASH_DB=sqlite`) |
| `PUBLIC_SHOW_ADMIN_LINK` | Toggle admin console link visibility on the public site layout. | `0` | No |
| `EMDASH_SITE_URL` | The public base URL of the site, used to restrict toolbar/admin access on public domains. | - | No |

---

## 🚀 Getting Started

### 1. Docker Compose (Quickstart)

You can run the development environment purely in Docker without installing Node.js or PostgreSQL on your host.

```bash
docker-compose up -d --build
```

This starts:
- **`app` container**: Hot-reloading dev server on port `4321` (mounts local workspace to `/app`).
- **`db` container**: PostgreSQL database (`emdash_db`) on port `5432`.

Access interfaces:
- **Public Site**: `http://localhost:4321`
- **Admin Portal**: `http://localhost:4321/_emdash/admin`

---

### 2. Local Setup (Manual Host Execution)

#### Prerequisites
- Node.js 18+
- pnpm (8+)
- Active PostgreSQL instance (or use local SQLite by defaulting `EMDASH_DB`)

#### Steps
1. **Install dependencies**:
   ```bash
   pnpm install
   ```
2. **Configure environment**:
   Create a local env or run the exports directly:
   ```bash
   export EMDASH_DB=postgres
   export DATABASE_URL="postgres://emdash:emdash_pass@localhost:5432/emdash_db"
   ```
3. **Seed the database**:
   Generates TypeScript types and runs initial database migrations / imports default seed content (`seed/seed.json`).
   ```bash
   pnpm bootstrap
   ```
4. **Run dev server**:
   ```bash
   pnpm dev
   ```
5. **Build for production**:
   ```bash
   pnpm build
   ```

---

## 🗄️ Database Operations

### Backing up & Restoring PostgreSQL

For managing data between different environments, utility scripts are provided in the `scripts/` directory:

- **Exporting Data (Dump)**:
  Generates a clean SQL dump omitting ownership definitions:
  ```bash
  DATABASE_URL="postgres://user:pass@host/db" ./scripts/pg-dump.sh > dump.sql
  ```
- **Importing Data (Restore)**:
  Restores an SQL dump to a target PostgreSQL database:
  ```bash
  DATABASE_URL="postgres://user:pass@host/new_db" ./scripts/pg-restore.sh < dump.sql
  ```
- **Seeding Database (`scripts/emdash-seed.mjs`)**:
  Custom runner for seeding PostgreSQL data. Essential during `pnpm bootstrap` as standard EmDash CLI seeding does not natively support Postgres setups out of the box.

---

## 📦 CI/CD & Production Deployment

### GitHub Actions Workflows

- **CI Pipeline (`ci.yml`)**:
  Runs on every PR/push to `develop`/`main`.
  - Type-checking, syntax formatting validation, and linting.
  - Filesystem security scans using **Trivy**.
  - Automated security assessment via **OWASP ZAP DAST** on a built preview server.
  - *Note: Ignores changes made solely to `helm/**` to optimize build minutes.*
- **CD Pipeline (`cd.yml`)**:
  Triggered by tags (e.g. `v1.0.0`).
  - Builds the production-ready Docker image.
  - Pushes to GitHub Container Registry (GHCR) under `ghcr.io/al17091/blog-emdash:vX.Y.Z` & `latest`.

### Kubernetes Setup via Helm & ArgoCD

Deployment configurations are packaged inside [helm/](file:///home/dapt/projects/blog-emdash/helm/).

- **ArgoCD Integration**:
  ArgoCD monitors this repository. Updating the tag parameter in your ArgoCD application definition triggers an automated GitOps deployment update.
- **Data Persistence**:
  A `PersistentVolumeClaim` (PVC) allocates 1Gi to preserve uploaded images under `/app/uploads`.
- **Traffic Routing**:
  Configures a Traefik `IngressRoute` and applies a redirect middleware to enforce SSL/HTTPS routing.
- **Seed Jobs**:
  Utilizes Kubernetes hook jobs to run the migration and seeding scripts automatically upon deployment.
