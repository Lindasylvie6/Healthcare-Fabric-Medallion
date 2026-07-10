## 🔄 DevOps, Pull Requests & CI/CD

[#-devops-pull-requests--cicd](#-devops-pull-requests--cicd)

The entire Fabric workspace is source-controlled in **Azure DevOps** and promoted across
three environments (**Development → Test → Production**) using **Fabric Deployment Pipelines**.
Changes flow through a **branch → pull request → merge** workflow, so `main` always reflects
reviewed, working code.

> **Plain-English version:** Fabric is wired to Azure DevOps the same way a Google Doc is wired
> to version history. Every pipeline, notebook, and lakehouse becomes a file in the repo. I never
> edit the live copy directly: I branch, make my change, open a pull request, get it reviewed,
> and only then does it merge and get promoted to Production.

---

### 1. Source Control — Fabric Git Integration

[#1-source-control--fabric-git-integration](#1-source-control--fabric-git-integration)

The Fabric workspace is connected to an Azure DevOps Git repository. Every workspace item is
serialized to a folder and versioned automatically:

| Git Folder                     | Fabric Item Type | Role in Pipeline               |
| ------------------------------ | ---------------- | ------------------------------ |
| `Bronze_Pipeline.DataPipeline` | Data pipeline    | Raw ingestion orchestration    |
| `Healthcare_ingestion.DataPipeline` | Data pipeline | Metadata-driven ingestion   |
| `DataflowGen2.Dataflow`        | Dataflow Gen2    | No-code Silver transformations |
| `Silver_layer.Notebook`        | Notebook         | Silver transformation logic    |
| `Notebook_1.Notebook`          | Notebook         | Supporting transformation      |
| `healthcare_lakehouse.Lakehouse` | Lakehouse      | OneLake storage (Bronze/Silver/Gold) |

When a notebook is changed in Fabric and committed, Git stores the source as `notebook-content.py`
(visible in the commit history). This means notebook logic is diffable and reviewable like any
other code, not locked inside a binary.

> **Why it matters:** Serializing Fabric items to Git gives full **version history, rollback, and
> code review** on data pipelines and notebooks, the same discipline software teams apply to
> application code.

---

### 2. Branching & Pull Request Workflow

[#2-branching--pull-request-workflow](#2-branching--pull-request-workflow)

`main` is never edited directly. Every change is made on a feature branch and merged through a
pull request.

```
main
 └─▶ healthcarebranch1        # feature branch created for a change
        │  add UTC timezone   # commit: switch load timestamps from local time to UTC
        ▼
   Pull Request #1  review──▶  Merge into main   ✅
```

**Example : Pull Request #1: `add UTC timezone`**
Audit timestamps (`_bronze_load_timestamp`, `_silver_load_timestamp`) were originally written in
local time. They were switched to **UTC** on a feature branch, because storing timestamps in UTC
removes ambiguity across regions and daylight-saving changes, a data engineering best practice.
The change was committed, opened as PR #1, reviewed, and merged into `main`.

> **Why it matters:** The pull request is a safety gate. A broken change stays on the branch and
> never touches the production version until it is reviewed and approved.

---

### 3. CI/CD : Fabric Deployment Pipelines (Dev → Test → Prod)

[#3-cicd--fabric-deployment-pipelines-dev--test--prod](#3-cicd--fabric-deployment-pipelines-dev--test--prod)

A **Fabric Deployment Pipeline** promotes the workspace through three isolated environments. Each
stage is its own workspace, so untested work never lands in Production.

```
┌───────────────┐      ┌───────────────┐      ┌────────────────────┐
│  DEVELOPMENT  │  ──▶ │     TEST      │  ──▶ │     PRODUCTION      │
│ Healthcare_Dev│      │ Healthcare_Test│     │Healthcare_production│
│  (build here) │      │ (validate)    │      │   (live workload)   │
└───────────────┘      └───────────────┘      └────────────────────┘
```

| Stage       | Workspace              | Status                 |
| ----------- | ---------------------- | ---------------------- |
| Development | `Healthcare_Dev`       | Source / build         |
| Test        | `Healthcare_Test`      | ✅ Successful deployment |
| Production  | `Healthcare_production`| ✅ Successful deployment |

**Items promoted through the pipeline:** `Bronze_Pipeline`, `Healthcare_ingestion`,
`Master_Pipeline`, `healthcare_lakehouse` (+ its SQL analytics endpoint), `Gold_layer` and
`healthcare_gold_model` (semantic models). Before each deployment, Fabric **compares** the target
stage against the source and shows exactly what changed, so nothing is promoted blindly.

> **Why it matters:** This is the CI/CD backbone. Code is built in Dev, validated in Test, and
> promoted to Prod with a controlled, comparable, one-click deployment — the standard enterprise
> release pattern.

---

### Production Maturity Notes

[#production-maturity-notes](#production-maturity-notes)

This project demonstrates the full source-control and promotion workflow. A fully hardened
enterprise setup would additionally layer on:

| Capability            | What it adds                                                        |
| --------------------- | ------------------------------------------------------------------- |
| Deployment rules      | Rebind lakehouse/data-source connections per stage (Prod reads Prod, not Dev) |
| Branch policies       | Require a reviewer + successful build validation before a PR can merge |
| Automated validation  | A pipeline that lints notebooks / checks schema on every pull request |
| Release approval gate  | Manual sign-off before promotion to the Production stage           |

---
