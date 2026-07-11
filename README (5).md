# ☁️ Cloud Data Engineering Platform | Microsoft Fabric

[![Microsoft Fabric](https://img.shields.io/badge/Microsoft_Fabric-0078D4?style=for-the-badge&logo=microsoft&logoColor=white)](https://fabric.microsoft.com)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Delta Lake](https://img.shields.io/badge/Delta_Lake-00ADD4?style=for-the-badge&logo=databricks&logoColor=white)](https://delta.io)
[![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)](https://powerbi.microsoft.com)
[![Azure DevOps](https://img.shields.io/badge/Azure_DevOps-0078D7?style=for-the-badge&logo=azure-devops&logoColor=white)](https://azure.microsoft.com/products/devops)
[![SQL](https://img.shields.io/badge/SQL-CC2927?style=for-the-badge&logo=microsoft-sql-server&logoColor=white)](https://learn.microsoft.com/en-us/fabric/data-warehouse/sql-analytics-endpoint)
[![OneLake](https://img.shields.io/badge/OneLake-0078D4?style=for-the-badge&logo=microsoft-azure&logoColor=white)](https://learn.microsoft.com/en-us/fabric/onelake/onelake-overview)

A production-shaped, end-to-end healthcare data engineering platform on **Microsoft Fabric**. A single **master pipeline** orchestrates the full run — metadata-driven ingestion, **Delta** transformation, and an automated **semantic model refresh** — across a Medallion Architecture, with everything **source-controlled in Azure DevOps** and promoted through a **Development → Test → Production** deployment pipeline.

The platform processes 552,545 rows across 9 clinical and financial datasets and delivers executive-ready Power BI analytics covering revenue at risk, denial management, department performance, clinical quality, and payer revenue.

---

## 📚 Table of Contents

- [📋 Overview](#-overview)
- [🏗️ Architecture](#️-architecture)
- [🎯 End-to-End Orchestration](#-end-to-end-orchestration)
- [🧩 Workspace Inventory](#-workspace-inventory)
- [🛠️ Tech Stack](#️-tech-stack)
- [📊 Datasets](#-datasets)
- [🥉 Bronze — Ingestion](#-bronze--ingestion)
- [🥈 Silver — Delta Transformation](#-silver--delta-transformation)
- [🥇 Gold — SQL Analytics-Endpoint Views](#-gold--sql-analytics-endpoint-views)
- [📈 Semantic Model & Dashboards](#-semantic-model--dashboards)
- [🔄 DevOps & CI/CD](#-devops--cicd)
- [🔧 Troubleshooting: SQL Endpoint Date Types](#-troubleshooting-sql-endpoint-date-types)
- [🏭 Production-Grade Practices](#-production-grade-practices)
- [🔮 Further Hardening](#-further-hardening)
- [👤 Author](#-author)

---

## 📋 Overview

- **One-click end-to-end run** via `Master_Pipeline`: ingestion → Silver transformation → Gold semantic-model refresh, chained on success
- **Microsoft Fabric Lakehouse** (`healthcare_lakehouse`, OneLake) as the unified storage and serving layer
- **Metadata-driven ingestion** in Fabric Data Factory (`Lookup` → `ForEach` → `Copy`) plus a dedicated **ADLS** source pipeline
- **Delta Lake** Silver tables written from a Fabric Notebook (pandas + `delta-rs`), queryable through the SQL analytics endpoint
- **Gold** exposed as reusable **SQL views**; a **Power BI semantic model** refreshed automatically inside the pipeline
- **Full CI/CD**: Azure DevOps Git integration + Fabric Deployment Pipelines across Development → Test → Production
- **Environment isolation**: dedicated staging Lakehouse and Warehouse for Dataflow Gen2 processing

### Project Highlights

- Single master orchestration pipeline covering the full Bronze → Silver → Gold → refresh lifecycle
- Metadata-driven, config-based ingestion rather than a hand-built activity per table
- Typed Delta tables that map cleanly to SQL analytics-endpoint types
- Gold business logic kept in version-controlled SQL views
- Automated Power BI semantic-model refresh as the final pipeline step
- Git-based source control with pull-request review and multi-environment promotion

### Business Value

Healthcare organizations lose revenue to denied claims, delayed reimbursements, and inconsistent payer processing. This platform centralizes clinical and financial data into a governed analytics environment to provide revenue and revenue-at-risk visibility by insurer and department, denial trends and appeal outcomes, department-level performance and clinical quality, and an executive summary for leadership.

---

## 🏗️ Architecture

![Medallion Architecture](docs/Fabric_medallion_Architecture.png)

```
ADLS + source files
        │
        ▼
┌──────────────────────────────── Master_Pipeline ────────────────────────────────┐
│                                                                                  │
│  Invoke: Bronze_ingestion ──▶ Notebook: Silver_Transformation ──▶ Gold Semantic  │
│        (Bronze_Pipeline)            (pandas → Delta)               model refresh  │
│              │                                                                    │
│   ┌──────────┴───────────┐                                                        │
│   ▼                      ▼                                                        │
│ Healthcare_ingestion   SylviePipeline_2 (ADLS)                                    │
│ (Lookup→ForEach→Copy)                                                             │
└──────────────────────────────────────────────────────────────────────────────────┘
        │                         │                              │
        ▼                         ▼                              ▼
  Files/Raw_data*          Tables/silver_*                dbo.gold_* SQL views
   (raw landing)              (Delta)                             │
                                                                  ▼
                                              Power BI semantic model → Dashboards
```

---

## 🎯 End-to-End Orchestration

`Master_Pipeline` is the single entry point for the platform. Three activities run in sequence, each gated by an **On Success** dependency:

| # | Activity                     | Type                  | What it does                                                       |
| - | ---------------------------- | --------------------- | ----------------------------------------------------------------- |
| 1 | **Bronze_ingestion**         | Invoke Pipeline       | Runs `Bronze_Pipeline` to ingest all sources into OneLake         |
| 2 | **Silver_Transformation**    | Notebook              | Runs the `Silver_layer` notebook (pandas → Delta tables)          |
| 3 | **Gold Semantic model refresh** | Semantic model refresh | Refreshes the Gold semantic model so dashboards are current       |

`Bronze_Pipeline` (step 1) itself invokes two child pipelines:

- **`Healthcare_ingestion`** — a metadata-driven `LookupData` → `ForEach (ForEach_healthcareFiles)` → `CopyData` pattern that lands each source into `Files/Raw_data{name}`
- **`SylviePipeline_2` (`ingestionADLS`)** — ingests source data from **Azure Data Lake Storage**

The result is a fully automated run: kick off `Master_Pipeline` (on a schedule or trigger) and the platform ingests, transforms, and refreshes analytics with no manual steps in between.

---

## 🧩 Workspace Inventory

All items live in the `Healthcare_Dev` Fabric workspace and are Git-synced to Azure DevOps (branch `healthcarebranch1`).

| Item                                 | Type                          | Role                                              |
| ------------------------------------ | ----------------------------- | ------------------------------------------------- |
| `Master_Pipeline`                    | Data pipeline                 | End-to-end orchestrator (ingest → Silver → refresh) |
| `Bronze_Pipeline`                    | Data pipeline                 | Ingestion orchestration (invokes the two below)   |
| `Healthcare_ingestion`               | Data pipeline                 | Metadata-driven copy (Lookup → ForEach → Copy)    |
| `SylviePipeline_2`                   | Data pipeline                 | ADLS source ingestion                             |
| `Silver_layer`                       | Notebook                      | Silver transformation (pandas → Delta)            |
| `healthcare_lakehouse`               | Lakehouse (+ SQL endpoint)    | Bronze / Silver / Gold storage and serving        |
| `healthcare_gold_model`              | Semantic model                | Star-schema model over the Gold views             |
| `Gold_layer`                         | Semantic model                | Gold semantic model                               |
| `StagingLakehouseForDataflows_2026`  | Lakehouse (+ SQL endpoint)    | Dataflow Gen2 staging                             |
| `StagingWarehouseForDataflows_2026`  | Warehouse                     | Dataflow Gen2 staging                             |

---

## 🛠️ Tech Stack

| Layer                   | Technology                                     | Purpose                                                 |
| ----------------------- | ---------------------------------------------- | ------------------------------------------------------- |
| Platform                | Microsoft Fabric                               | Unified lakehouse + compute + BI                        |
| Orchestration           | Fabric Data Factory (`Master_Pipeline`)        | End-to-end run with On Success dependencies             |
| Storage                 | OneLake Lakehouse                              | `Files/` raw landing + `Tables/` Delta (Silver)         |
| Ingestion               | Fabric Data Factory (Lookup, ForEach, Copy)    | Metadata-driven copy + ADLS source pipeline             |
| Staging                 | Dataflow Gen2 (staging Lakehouse + Warehouse)  | Isolated dataflow processing                            |
| Transformation Compute  | Fabric Notebook (Python / pandas)              | Silver cleaning and standardization                     |
| Table Format            | Delta Lake via `delta-rs` (`write_deltalake`)  | Typed, SQL-endpoint-queryable Silver tables             |
| Gold Serving            | SQL analytics endpoint views (`dbo`)           | Reusable business aggregations                          |
| Semantic Model          | Power BI (`healthcare_gold_model`, `Gold_layer`) | Star-schema models over the Gold views                |
| Visualization           | Power BI                                       | Executive dashboards                                    |
| Version Control & CI/CD | Azure DevOps + Fabric Deployment Pipelines     | Git integration, PR workflow, Dev → Test → Prod         |

> **Note on Spark:** Silver transformations run in **pandas** and write **Delta** tables via `delta-rs` (`write_deltalake`). Spark compute was throttled on the Fabric trial account (HTTP 430 errors), so the pipeline uses pandas rather than PySpark while still producing Delta output the SQL analytics endpoint queries natively. In production, PySpark would provide distributed scale for larger volumes.

---

## 📊 Datasets

Nine clinical and financial datasets land in `Files/Raw_data{name}` and become `silver_{name}` Delta tables.

| Dataset              | Rows        | Key Columns                                                  |
| -------------------- | ----------- | ----------------------------------------------------------- |
| patients             | 60,000      | demographics, city, state, insurance_type                   |
| encounters           | 70,000      | visit_date, visit_type, readmitted_flag, length_of_stay     |
| diagnoses            | 70,000      | diagnosis_code, chronic_flag, primary_flag                  |
| claims_and_billing   | 70,000      | billed_amount, paid_amount, claim_status                    |
| denials              | 5,998       | denial_reason_code, appeal_status, final_outcome            |
| procedures           | 126,021     | procedure_code, procedure_cost                              |
| medications          | 94,498      | drug_name, dosage, cost                                     |
| providers            | 1,491       | specialty, department, npi                                  |
| lab_tests            | 54,537      | test_name, test_result, status                             |
| **Total**            | **552,545** |                                                             |

---

## 🥉 Bronze — Ingestion

Raw source data is ingested into OneLake by **`Bronze_Pipeline`**, invoked as step 1 of `Master_Pipeline`. It runs two child pipelines:

1. **`Healthcare_ingestion`** — a metadata-driven copy pattern: a `LookupData` activity reads the list of source objects, a `ForEach (ForEach_healthcareFiles)` loops over them, and a `CopyData` activity lands each file into `Files/Raw_data{name}`.
2. **`SylviePipeline_2` (`ingestionADLS`)** — ingests source data from Azure Data Lake Storage.

Because ingestion is metadata-driven, new source files are picked up by configuration rather than by adding a new activity per table — the pattern production ingestion frameworks use.

---

## 🥈 Silver — Delta Transformation

**Notebook:** `Silver_layer` (Silver Transformation) — Python / pandas, writing Delta via `delta-rs`.
**Output:** `Tables/silver_{name}` (Delta)

Each raw dataset is read from Bronze, cleaned, and written as a typed Delta table with audit columns.

```python
def clean(df):
    # 1. trim stray spaces on text columns; turn blanks into nulls
    for c in df.columns:
        if df[c].dtype == "object":
            df[c] = df[c].str.strip()
    df = df.replace("", None)

    # 2. parse date text (e.g. "03-01-2025") and cast to DATE for the SQL endpoint
    for c in df.columns:
        if "date" in c.lower() or c.lower() == "dob":
            df[c] = pd.to_datetime(df[c], dayfirst=True, errors="coerce").dt.date

    # 3. drop exact-copy rows
    return df.drop_duplicates()

for name in DATASETS:                       # all 9 datasets
    df = clean(read_bronze(name))
    write_deltalake(
        f"{SILVER_PATH}/silver_{name}",
        df,
        mode="overwrite",
        storage_options={"allow_unsafe_rename": "true"},
    )
```

**Silver rules:** text trimming, blank-to-null normalization, `dayfirst` date parsing cast to `DATE`, exact-duplicate removal, and audit columns (`_source_file`, `_ingested_at` in tz-aware UTC).

> **Why Delta?** Writing Silver as Delta tables into `Tables/` makes them typed and directly queryable through the Fabric SQL analytics endpoint, which the Gold views and semantic model build on.

---

## 🥇 Gold — SQL Analytics-Endpoint Views

The Gold layer is a set of **SQL views** in the `dbo` schema on the Fabric SQL analytics endpoint, each modeling a business domain over the Silver Delta tables:

| Gold View                            | Business Use                                          |
| ------------------------------------ | ---------------------------------------------------- |
| `gold_executive_summary`             | Top-line KPIs for leadership reporting               |
| `gold_revenue_by_insurer`            | Revenue and collection performance per payer         |
| `gold_revenue_at_risk_by_department` | Unpaid / at-risk revenue by department               |
| `gold_denial_management`             | Denial reasons, rates, and appeal outcomes           |
| `gold_department_performance`        | Length of stay, readmissions, and cost by department |
| `gold_clinical_quality`              | Clinical quality and readmission indicators          |

Building Gold as views keeps business logic in version-controlled SQL, avoids duplicating data, and gives the semantic model and ad-hoc SQL a single governed layer.

---

## 📈 Semantic Model & Dashboards

The Gold views feed a Power BI **semantic model** (`healthcare_gold_model`), refreshed automatically as the final step of `Master_Pipeline` (the **Gold Semantic model refresh** activity) so dashboards are always current after a run. Dashboards built on the model:

### Executive Summary
![Executive Summary Dashboard](docs/dashboard_executive_summary.png)
Top-line KPIs across revenue, denials, and department performance for leadership.

### Revenue & Revenue at Risk
![Revenue Dashboard](docs/dashboard_revenue.png)
Revenue and collection rate by insurer, with at-risk (unpaid) revenue broken out by department.

### Denial Management
![Denial Management Dashboard](docs/dashboard_denials.png)
Denial rates by reason and payer with appeal outcomes — a direct process-improvement signal.

### Department Performance & Clinical Quality
![Department Performance Dashboard](docs/dashboard_department_performance.png)
Length of stay, readmission rates, cost by department, and clinical quality indicators.

> Screenshots live in `docs/`. Add each PNG using the filenames above.

---

## 🔄 DevOps & CI/CD

The entire Fabric workspace is source-controlled in **Azure DevOps** and promoted across three environments (**Development → Test → Production**) using **Fabric Deployment Pipelines**. Changes flow through a **branch → pull request → merge** workflow, so `main` always reflects reviewed, working code.

> **Plain-English version:** Fabric is wired to Azure DevOps the same way a Google Doc is wired to version history. Every pipeline, notebook, semantic model, and lakehouse becomes a file in the repo. I never edit the live copy directly: I branch, make my change, open a pull request, get it reviewed, and only then does it merge and get promoted to Production.

### 1. Source Control — Fabric Git Integration

The `Healthcare_Dev` workspace is connected to an Azure DevOps Git repo; every item is serialized and versioned automatically. The workspace view shows each item's **Git status** (Synced / Uncommitted), so uncommitted work is visible at a glance before promotion.

| Git Folder                          | Fabric Item Type | Role                                 |
| ----------------------------------- | ---------------- | ------------------------------------ |
| `Master_Pipeline.DataPipeline`      | Data pipeline    | End-to-end orchestrator              |
| `Bronze_Pipeline.DataPipeline`      | Data pipeline    | Ingestion orchestration              |
| `Healthcare_ingestion.DataPipeline` | Data pipeline    | Metadata-driven ingestion            |
| `Silver_layer.Notebook`             | Notebook         | Silver transformation logic          |
| `healthcare_lakehouse.Lakehouse`    | Lakehouse        | OneLake storage + SQL endpoint       |
| `healthcare_gold_model.SemanticModel` | Semantic model | Gold model                           |

### 2. Branching & Pull Request Workflow

`main` is never edited directly. Changes are made on a feature branch (`healthcarebranch1`) and merged through a pull request.

```
main
 └─▶ healthcarebranch1        # feature branch
        │  add UTC timezone   # commit: switch load timestamps to tz-aware UTC
        ▼
   Pull Request #1  review──▶  Merge into main   ✅
```

**Example — PR #1 `add UTC timezone`:** `_ingested_at` was switched to tz-aware UTC (`datetime.now(timezone.utc)`) on a feature branch, committed, reviewed, and merged.

### 3. CI/CD — Fabric Deployment Pipelines (Dev → Test → Prod)

A **Fabric Deployment Pipeline** promotes the workspace through three isolated environments; each stage is its own workspace, so untested work never lands in Production.

```
┌───────────────┐      ┌────────────────┐      ┌─────────────────────┐
│  DEVELOPMENT  │  ──▶ │      TEST      │  ──▶ │      PRODUCTION      │
│ Healthcare_Dev│      │ Healthcare_Test│      │Healthcare_production │
└───────────────┘      └────────────────┘      └─────────────────────┘
```

**Items promoted:** `Master_Pipeline`, `Bronze_Pipeline`, `Healthcare_ingestion`, `SylviePipeline_2`, `Silver_layer`, `healthcare_lakehouse` (+ SQL endpoint and Gold views), `healthcare_gold_model`, and `Gold_layer`. Before each deployment, Fabric compares the target stage against the source and shows exactly what changed.

---

## 🔧 Troubleshooting: SQL Endpoint Date Types

### Problem
After the first Silver build, date columns did not surface cleanly through the SQL analytics endpoint, and tz-naive ingestion timestamps (`datetime.utcnow()`) were not supported.

### Root Cause
`pd.to_datetime(...)` produced pandas `datetime64[ns]` values (with a time component), and `utcnow()` produced a tz-naive timestamp. The SQL analytics endpoint expects a clean `DATE` type for date fields and tz-aware timestamps.

### Fix
```python
# Cast parsed dates to Python date -> DATE type the SQL endpoint accepts
df[c] = pd.to_datetime(df[c], dayfirst=True, errors="coerce").dt.date

# Use a tz-aware UTC timestamp for the audit column
df["_ingested_at"] = dt.datetime.now(dt.timezone.utc)
```
Then **refresh the SQL analytics endpoint** so it picks up the new column types.

### Key Learnings
1. Delta column types must map to types the SQL analytics endpoint supports — `datetime64[ns]` with a time part is not the same as `DATE`.
2. Ingestion timestamps should be tz-aware (`datetime.now(timezone.utc)`), not `utcnow()`.
3. After any schema change, refresh the SQL analytics endpoint to re-read column metadata.

---

## 🏭 Production-Grade Practices

What makes this platform close to a real production environment:

- **Single orchestrated run** — `Master_Pipeline` chains ingestion, transformation, and semantic-model refresh with On Success gating, so a failure stops the run instead of publishing bad data.
- **Automated refresh** — the semantic model is refreshed inside the pipeline; dashboards reflect the latest run without a manual step.
- **Metadata-driven ingestion** — `Lookup` + `ForEach` + `Copy` scales to new sources by configuration, not code changes.
- **Typed, governed serving layer** — Delta Silver tables + SQL Gold views give consumers one clean, version-controlled interface.
- **Multi-environment CI/CD** — Git source control + Fabric Deployment Pipelines promote reviewed changes Dev → Test → Prod behind a pull-request gate.
- **Environment isolation** — dedicated staging Lakehouse and Warehouse keep Dataflow Gen2 processing separate from the serving layer.

---

## 🔮 Further Hardening

| Area                    | Next Step                                                        |
| ----------------------- | --------------------------------------------------------------- |
| Compute at scale        | PySpark for distributed Silver transformation on larger volumes  |
| Incremental processing  | Watermark on `_ingested_at` for incremental instead of full load |
| Security                | Row-level security in the semantic model by department / role    |
| Observability           | Data quality summary table + pipeline failure alerting           |
| Deployment rules        | Per-stage data-source rebinding so Prod reads Prod, not Dev      |
| Endpoint refresh        | Automated SQL-endpoint refresh step after Silver                 |

---

## 📁 Project Structure

```
Healthcare-Fabric-Medallion/
│
├── pipelines/
│   ├── Master_Pipeline/            # End-to-end orchestrator
│   ├── Bronze_Pipeline/            # Invokes the two ingestion pipelines
│   ├── Healthcare_ingestion/       # Metadata-driven Lookup → ForEach → Copy
│   └── SylviePipeline_2/           # ADLS source ingestion (ingestionADLS)
│
├── notebooks/
│   └── Silver_layer.py             # pandas cleaning -> Delta (write_deltalake)
│
├── gold_views/                     # SQL view definitions (dbo.gold_*)
│
├── semantic_models/                # healthcare_gold_model, Gold_layer
│
├── docs/
│   ├── Fabric_medallion_Architecture.png
│   ├── Fabric_Data_modeling.png
│   └── dashboard_*.png
│
└── README.md
```

---

## 👤 Author

**Sylvie Linda** — Data Engineer focused on building cloud-native data platforms using Microsoft Fabric, Azure, SQL, Python, and modern data engineering practices. I enjoy transforming complex operational data into reliable, business-ready datasets that drive decision-making.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/Linda-Sylvie-85087416a)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Lindasylvie6)

---

*Built with Microsoft Fabric · Python · pandas · Delta Lake · Power BI · Azure DevOps*
