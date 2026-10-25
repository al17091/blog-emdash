---
name: git-workflow
description: >-
  Git operations runbook and quality gate standards for lab-infra. Covers branch lifecycle (develop vs main),
  PR merge commit policy, pre-push CI verification inside the workspace container, and host signing key requirements.
---

# Git Workflow & Quality Gate Runbook

This skill defines the branching model, push policy, commit signing requirements, and local pre-push CI verification procedures for `lab-infra`.

---

## 1. Core Branch & Push Invariants

### 1.1 Strict Protection of `main` (No Direct Push)
> [!IMPORTANT]
> **NEVER execute `git push origin main` directly.**  
> The `main` branch represents stable production infrastructure. All updates to `main` must occur exclusively through **GitHub Pull Requests** from `develop` (or hotfix branches) using **merge commits** (`--no-ff`).
> 
> **Why merge commits are mandatory**:  
> Fast-forward merges into `main` destroy release boundary history, making it impossible to cleanly identify release milestones or revert entire feature sets if a production issue arises.

### 1.2 Pushing to Non-Main Branches (`develop`, feature branches)
- Pushing to working branches (such as `develop`, `feat/*`, `fix/*`) is **permitted and encouraged** once local work is completed and verified against local CI checks.
- Changes should be staged and committed incrementally with clean Conventional Commits messages.

### 1.3 Host-Side Commit Signing Rule
> [!CRITICAL]
> **Always execute `git commit` and `git push` on the host machine**, NOT inside the `workspace` container.  
> Commits executed inside the container will lack host-level SSH/GPG signing keys and fail signature verification.

---

## 2. Pre-Push Quality Gate (Local CI Checks)

Before pushing commits to `origin/develop` or opening a Pull Request to `main`, the AI agent must run the project's quality gate checks inside the `workspace` container to prevent CI pipeline failures:

### 2.1 Full Pre-Push Verification Suite
Run the following checks inside the container:

```bash
# 1. YAML Syntax & Formatting Check
docker compose exec workspace yamllint -c .yamllint.yml \
  ansible/playbooks/ \
  ansible/inventory/group_vars/all/common.yml \
  ansible/inventory/group_vars/all/samples/secret.yml

# 2. Shell Scripts Syntax
docker compose exec workspace bash -c 'find . -name "*.sh" -not -path "*/.git/*" -not -path "*/.venv/*" -exec bash -n {} +'

# 3. Python Compile Check
docker compose exec workspace python3 -m py_compile scripts/*.py

# 4. Ansible Playbook Sequence & Bootstrap Smoke Test
docker compose exec workspace python3 scripts/smoke_test_playbooks.py
```

### 2.2 Common CI Pitfalls & Prevention
| Check | Common Cause | Fix |
| :--- | :--- | :--- |
| `yamllint` [empty-lines] | More than 1 blank line at EOF or inside tasks | Ensure only 1 trailing newline at the end of YAML files. |
| `yamllint` [truthy] | Using unquoted `yes`/`no` or `on`/`off` | Use standard boolean `true` / `false`. |
| `smoke_test_playbooks.py` | Missing role dependencies or syntax error | Run `ansible-playbook --syntax-check` on modified playbooks. |

---

## 3. Pull Request & Release Flow (develop -> main)

### 3.1 Invariants & Policies
> [!CRITICAL]
> **1. CI Gate Invariant**: NEVER merge a PR before all GitHub Actions CI checks have completed successfully (100% green).  
> **2. PR Audit History Invariant**: Always merge PRs using a **merge commit** (`gh pr merge --merge`). NEVER squash or rebase when promoting from `develop` to `main`, in order to preserve release boundary history and rollback points.  
> **3. Signed Host Commits**: Always sign Git commits and tags with `-S` / `-s` on the host machine.

---

### 3.2 GitHub CLI (`gh`) Execution Environment
The GitHub CLI (`gh`) is authenticated with full repository and workflow scopes inside the workspace container (`lab-infra-workspace-1`). Always invoke it via:
```bash
docker exec lab-infra-workspace-1 gh <subcommand> --repo <owner/repo>
```

---

### 3.3 End-to-End Promotion & Release Procedure

#### Step 1: Push Local Work to `origin/develop`
Ensure local pre-push checks pass, then push the host-signed commits:
```bash
git push origin develop
```

#### Step 2: Open Pull Request via `gh`
Check for existing PRs, then create the PR from `develop` to `main`:
```bash
docker exec lab-infra-workspace-1 gh pr create \
  --repo al17091/<repo-name> \
  --base main \
  --head develop \
  --title "release: <brief description>" \
  --body "## Summary\n\n<details of changes and verification>"
```

#### Step 3: Monitor CI Execution
Watch the workflow run until completion (blocking until green):
```bash
# List latest runs to get the run ID
docker exec lab-infra-workspace-1 gh run list --repo al17091/<repo-name> --limit 3

# Watch run to completion
docker exec lab-infra-workspace-1 gh run watch <RUN_ID> --repo al17091/<repo-name> --exit-status

# Verify all PR status checks are green
docker exec lab-infra-workspace-1 gh pr checks <PR_NUMBER> --repo al17091/<repo-name>
```

#### Step 4: Merge PR Preserving Audit History
Once CI is 100% green, execute the merge with `--merge` (merge commit):
```bash
docker exec lab-infra-workspace-1 gh pr merge <PR_NUMBER> --merge --repo al17091/<repo-name>
```

#### Step 5: Tag Release (for CD Deployments)
If the project uses CD triggers on version tags (e.g., `v*.*.*`):
```bash
git checkout main
git pull origin main
git tag -s vX.Y.Z -m "Release vX.Y.Z: <summary>"
git push origin vX.Y.Z

# Monitor CD image build & push
docker exec lab-infra-workspace-1 gh run list --repo al17091/<repo-name> --limit 3
docker exec lab-infra-workspace-1 gh run watch <CD_RUN_ID> --repo al17091/<repo-name> --exit-status
```

#### Step 6: Reconcile Local Branches
```bash
git checkout develop
git pull origin develop
```

---

## 4. Semantic Versioning & Environment Lifecycle Policy

### 4.1 SemVer Specifications & Git Tag Distinction
- **Semantic Versioning (SemVer 2.0.0 Specification)**:  
  A Semantic Version MUST NOT contain a leading `v` prefix. Valid SemVer identifiers follow `MAJOR.MINOR.PATCH` with optional pre-release identifiers (e.g., `1.2.0`, `0.1.2-rc.1`, `0.1.2-preview`).
- **Git Release Tags**:  
  Git release tags prefix the SemVer string with `v` (e.g., `v1.2.0`, `v0.1.2-rc.1`) to establish standard release references in Git and GitHub Releases. CI/CD pipelines strip the leading `v` to resolve the underlying SemVer value (e.g., `v1.2.0` -> `1.2.0`).

### 4.2 Stability Hierarchy & Release Progression
Release progression strictly follows the standard stability hierarchy:
`Stability: Low ──> alpha ──> beta ──> rc (Release Candidate / preview) ──> Stable (GA)`

### 4.3 Environment Mapping Policy
| Git Tag Format | SemVer Form | Stability Stage | Target Environment | Target Branch | Role & Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `vX.Y.Z-rc.1` (`-preview`) | `X.Y.Z-rc.1` | Release Candidate | **STG (Staging)** | `develop` | Staging verification, integration validation, and cost/load profiling. NEVER deployed to PROD. |
| `vX.Y.Z` | `X.Y.Z` | Stable (GA) | **PROD (Production)** | `main` | Production deployment. Tagged ONLY after full verification and `--merge` into `main`. |

### 4.4 Tagging Rules & Invariants
> [!CRITICAL]
> **1. Strict Protection of Stable Release Tags (`vX.Y.Z`)**:  
> - NEVER tag a stable release (`vX.Y.Z` / SemVer `X.Y.Z`) directly on the `develop` branch.
> - Staging verification and preliminary testing on `develop` MUST strictly use pre-release tags (e.g., `vX.Y.Z-rc.1` or `vX.Y.Z-preview`).
>
> **2. Production Promotion Flow**:  
> - Only after staging validation (metrics, resource costs, operational behavior) is fully verified may a PR be opened from `develop` to `main`.
> - Once the PR is merged with a merge commit (`--merge`), the stable release tag `vX.Y.Z` MUST be created and pushed **exclusively on the `main` branch**.

