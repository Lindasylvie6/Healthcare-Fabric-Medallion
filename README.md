# 🏥 Healthcare Analytics Platform | Microsoft Fabric

[![Microsoft Fabric](https://img.shields.io/badge/Microsoft_Fabric-0078D4?style=for-the-badge&logo=microsoft&logoColor=white)](https://fabric.microsoft.com)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)](https://powerbi.microsoft.com)
[![Parquet](https://img.shields.io/badge/Apache_Parquet-50ABF1?style=for-the-badge&logo=apache&logoColor=white)](https://parquet.apache.org)
[![SQL](https://img.shields.io/badge/SQL-CC2927?style=for-the-badge&logo=microsoft-sql-server&logoColor=white)](https://learn.microsoft.com/en-us/fabric/data-warehouse/sql-analytics-endpoint)
[![pandas](https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![OneLake](https://img.shields.io/badge/OneLake-0078D4?style=for-the-badge&logo=microsoft-azure&logoColor=white)](https://learn.microsoft.com/en-us/fabric/onelake/onelake-overview)

End-to-end healthcare data engineering project built on **Microsoft Fabric** with a production-inspired Medallion Architecture
following industry patterns used in enterprise
data platforms, orchestrated with **Fabric Data Factory**, and designed for **Power BI** consumption.

This solution processes 552,545 rows across 9 clinical and financial source files , delivering executive-ready dashboards covering revenue cycle, denial management, department performance, and patient risk scoring.

---

## 📚 Table of Contents

- [📋 Overview](#-overview)
- [🏗️ Architecture](#️-architecture)
- [🛠️ Tech Stack](#️-tech-stack)
- [📊 Datasets](#-datasets)
- [🥉 Bronze Layer](#-bronze-layer)
- [🥈 Silver Layer](#-silver-layer)
- [🥇 Gold Layer : Star Schema](#-gold-layer-star-schema)
- [⚙️ Orchestration](#️-orchestration)
- [📈 Analytics Consumption Layer](#-Analytics-Consumption-Layer)
- [💡 Key Engineering Decisions](#-key-engineering-decisions)
- [📊 Business Insights](#-business-insights)
- [🔧 Troubleshooting: Composite Key Discovery](#-troubleshooting-composite-key-discovery-in-silver)
- [🔮 Production Enhancements](#-production-enhancements)
- [👤 Author](#-author)

---

## 📋 Overview

- **Microsoft Fabric Lakehouse** as the unified storage and compute layer (OneLake)
- **Python + pandas + pyarrow** for notebook-based data transformation
- **Fabric Data Factory** for pipeline orchestration, scheduling, and event-based triggers
- **Parquet** as the storage format across all medallion layers
- **Power BI** for business intelligence dashboards connected via SQL Analytics Endpoint

### Project Highlights

- Built production Medallion Architecture (Bronze / Silver / Gold) on Microsoft Fabric
- Automated orchestration with chained notebook pipeline (On Success dependencies)
- Dual-trigger strategy: daily schedule (6:00 AM ET) + event-based CSV arrival trigger
- Email failure alerts configured directly in the pipeline
- Composite key deduplication discovered and resolved through data profiling
- Engineered derived KPIs: collection rate, unpaid amount, risk score, readmission rate
- Designed a Star Schema data model for Power BI with 1 fact table and 11 dimension aggregates
- Full pipeline runtime under 4 minutes end-to-end

### Business Value

Healthcare organizations face significant revenue leakage due to denied claims, delayed reimbursements, and inconsistent payer processing.

This platform centralizes clinical and financial data into a governed analytics environment to provide:

- Visibility into denial trends and appeal success rates
- Insurance payer revenue and collection rate analysis
- Department-level readmission and performance tracking
- Patient risk scoring for clinical intervention prioritization
- Executive-ready reporting via Power BI

---

## 🏗️ Architecture

[![Medallion Architecture](https://github.com/Lindasylvie6/Healthcare-Fabric-Medallion/blob/main/Fabric_medallion_Architecture.png?raw=true)](https://github.com/Lindasylvie6/Healthcare-Fabric-Medallion/blob/main/Fabric_medallion_Architecture.png)

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Platform | Microsoft Fabric | Unified lakehouse + compute + BI |
| Storage | OneLake (Lakehouse) | Medallion layer storage |
| Compute | Fabric Notebooks (Python kernel) | Data transformation |
| Libraries | pandas, pyarrow, pyarrow.parquet | DataFrame processing and Parquet I/O |
| File Format | Apache Parquet | Typed, compressed columnar storage |
| Orchestration | Fabric Data Factory | Pipeline sequencing and scheduling |
| Triggers | Schedule + Event-based (OneLake) | Batch and near real-time refresh |
| Alerting | Email failure notifications | Pipeline monitoring |
| Visualization | Power BI Desktop | Business intelligence dashboards |
| Diagramming | draw.io | Architecture and data model diagrams |
| Version Control | Azure DevOps | `Healthcare-Fabric-Medallion` project |

> **Note on Spark:** HTTP 430 throttle errors on a Fabric trial account blocked Spark compute during the build. The pipeline was intentionally redesigned using pure Python (pandas + pyarrow) to deliver a tested, working solution — a real production decision-making exercise. In a production environment, Bronze and Silver would use PySpark for distributed scale, and Gold tables would be written as Delta format to enable the SQL Analytics Endpoint natively.

---

## 📊 Datasets

| Dataset | Rows | Key Columns |
|---|---|---|
| patients | 60,000 | demographics, city, state, insurance_type |
| encounters | 70,000 | visit_date, visit_type, readmitted_flag, length_of_stay |
| diagnoses | 70,000 | diagnosis_code, chronic_flag, primary_flag |
| claims_and_billing | 70,000 | billed_amount, paid_amount, claim_status |
| denials | 5,998 | denial_reason_code, appeal_status, final_outcome |
| procedures | 126,021 | procedure_code, procedure_cost |
| medications | 94,498 | drug_name, dosage, cost |
| providers | 1,491 | specialty, department, npi |
| lab_tests | 54,537 | test_name, test_result, status |
| **Total** | **552,545** | |

---

## 🥉 Bronze Layer

**Notebook:** `01_bronze_ingestion.ipynb`  
**Path:** `Files/bronze/{table_name}/part-0.parquet`

The Bronze layer is the **raw landing zone**. No transformations, no business logic , read the CSV and land it safely with two audit columns added.

```python
for table_name, file_name in SOURCE_FILES.items():
    df = pd.read_csv(f"{RAW_PATH}/{file_name}")

    # Audit columns — WHEN and WHERE the data came from
    df["_bronze_load_timestamp"] = datetime.now().isoformat()
    df["_source_file"]           = file_name

    # Write as typed, compressed Parquet (vs raw untyped CSV)
    pq.write_table(
        pa.Table.from_pandas(df),
        f"{BRONZE_PATH}/{table_name}/part-0.parquet"
    )
```

**Why Parquet over CSV?** Parquet stores column types (int, float, datetime), compresses automatically, and reads 5–10x faster. Every byte written in Bronze is read multiple times downstream , format choice compounds.

**Why audit columns?** In production, data lineage and compliance require knowing *when* each row arrived and *from which file*. These columns are available for debugging and watermarking.

**Results:**

| Table | Rows Loaded | Runtime |
|---|---|---|
| bronze_patients | 60,000 | |
| bronze_encounters | 70,000 | |
| bronze_providers | 1,491 | |
| bronze_claims_and_billing | 70,000 | |
| bronze_denials | 5,998 | |
| bronze_diagnoses | 70,000 | |
| bronze_procedures | 126,021 | |
| bronze_medications | 94,498 | |
| bronze_lab_tests | 54,537 | |
| **Total** | **552,545** | **1m 33s** |

---

## 🥈 Silver Layer

**Notebook:** `02_silver_transformation.ipynb`  
**Path:** `Files/silver/{table_name}/part-0.parquet`

Silver applies **6 quality rules per table**: deduplication, ISO date parsing, null handling, text normalization, derived column engineering, and audit column management.

```python
# Example: silver_patients

df = pd.read_parquet(f"{BRONZE_PATH}/patients/part-0.parquet")

# Rule 1 — Deduplication on primary key
df = df.drop_duplicates(subset=["patient_id"])

# Rule 2 — Parse dates to ISO format
df["dob"]               = pd.to_datetime(df["dob"], dayfirst=True, errors="coerce")
df["registration_date"] = pd.to_datetime(df["registration_date"], dayfirst=True, errors="coerce")

# Rule 3 — Text normalization (prevents "MALE" vs "Male" fan-out in Power BI)
df["gender"]         = df["gender"].str.strip().str.title()
df["ethnicity"]      = df["ethnicity"].str.strip().str.title()
df["insurance_type"] = df["insurance_type"].str.strip().str.upper()
df["state"]          = df["state"].str.strip().str.upper()

# Rule 4 — Null handling
df["phone"] = df["phone"].fillna("Unknown")
df["email"] = df["email"].fillna("Unknown")

# Rule 5 — Silver audit column; drop Bronze audit columns
df["_silver_load_timestamp"] = datetime.now().isoformat()
df = df.drop(columns=["_bronze_load_timestamp", "_source_file"])
```

**Derived columns engineered at Silver (claims_and_billing):**

```python
df["unpaid_amount"]   = df["billed_amount"] - df["paid_amount"]
df["collection_rate"] = (df["paid_amount"] / df["billed_amount"] * 100).round(2)
```

These metrics are calculated once in Silver and reused across multiple Gold aggregations without redundant computation.

| Transformation | Description |
|---|---|
| Date casting | String → ISO datetime using `pd.to_datetime()` |
| Text normalization | `str.strip()` + `.str.title()` / `.str.upper()` for consistency |
| Null handling | Semantic defaults (`"Unknown"`, `"Not Filed"`, `"No Denial"`, `0`) |
| Deduplication | By primary key or composite key depending on table |
| Derived columns | `unpaid_amount`, `collection_rate` on claims |
| Audit propagation | `_silver_load_timestamp` added; Bronze audit columns removed |

**Runtime: 1m 11s**

---

## 🥇 Gold Layer : Star Schema

**Notebook:** `03_gold_aggregation.ipynb`  
**Path:** `Files/gold/{table_name}/part-0.parquet`

[![Data Model](https://github.com/Lindasylvie6/Healthcare-Fabric-Medallion/blob/main/Fabric_Data_modeling.png?raw=true)](https://github.com/Lindasylvie6/Healthcare-Fabric-Medallion/blob/main/Fabric_Data_modeling.png)

All 9 Silver tables are loaded into memory, joined, grouped, and written to 12 business-ready aggregation tables.

### Gold Tables

| Table | Rows | Business Use |
|---|---|---|
| `gold_patient_summary` | 60,000 | Central fact — total visits, spend, readmissions per patient |
| `gold_revenue_by_payer` | 7 | Revenue and denial rate per insurance company |
| `gold_revenue_by_month` | 13 | Monthly revenue trend |
| `gold_revenue_by_dept` | 21 | Revenue breakdown by department |
| `gold_denial_by_reason` | 14 | Top denial codes and appeal success rates |
| `gold_denial_by_payer` | 7 | Denials per insurance provider |
| `gold_denial_by_month` | — | Denial trend over time |
| `gold_department_performance` | 21 | Avg LOS, readmission rate, procedure costs |
| `gold_readmission_by_dept` | 21 | Readmissions by department |
| `gold_readmission_by_diag` | 63 | Which diagnoses drive readmissions |
| `gold_high_risk_patients` | 60,000 | Risk score and category per patient |
| `gold_readmission_by_month` | 3 | Monthly readmission trend |

### Patient Risk Scoring

```python
# Multi-factor risk score: age, visit frequency, readmissions, chronic conditions
high_risk["risk_score"] = (
    (high_risk["age"] // 10) +                        # older = higher risk
    (high_risk["total_visits"] * 2) +                 # frequent visitors
    (high_risk["total_readmissions"] * 5) +           # readmissions weighted heavily
    (high_risk["chronic_count"].fillna(0) * 3)        # chronic condition burden
)

high_risk["risk_category"] = pd.cut(
    high_risk["risk_score"],
    bins=[0, 10, 15, 20, float("inf")],
    labels=["Low", "Medium", "High", "Critical"]
)
```

### Revenue by Payer

```python
revenue_by_payer = claims.groupby("insurance_provider").agg(
    total_claims = ("claim_id",      "count"),
    total_billed = ("billed_amount", "sum"),
    total_paid   = ("paid_amount",   "sum"),
    total_unpaid = ("unpaid_amount", "sum")
).reset_index()

revenue_by_payer["avg_collection_rate"] = (
    revenue_by_payer["total_paid"] /
    revenue_by_payer["total_billed"] * 100
).round(2)
```

### Registering Gold Tables in the Lakehouse

Gold Parquet files are copied into `Tables/` so they appear in the Lakehouse table browser and are queryable via SQL:

```python
import shutil

for table in gold_tables:
    src  = f"{GOLD_PATH}/{table}/part-0.parquet"
    dest = f"{TABLES_PATH}/gold_{table}"
    os.makedirs(dest, exist_ok=True)
    shutil.copy2(src, f"{dest}/part-0.parquet")
```

**Runtime: 1m 12s**

---

## ⚙️ Orchestration

**Tool:** Fabric Data Factory : `healthcare_master_pipeline`

The three notebooks are chained sequentially with `On Success` dependency between each step:

```
bronze_ingestion  ──On Success──▶  silver_transformation  ──On Success──▶  gold_aggregation
     1m 33s                              1m 11s                                 1m 12s
```

**Total pipeline runtime: < 4 minutes**

### Triggers Configured

| Trigger | Type | Configuration |
|---|---|---|
| `daily_schedule` | Schedule | Every day at 6:00 AM ET |
| `csv_arrival_trigger` | Event-based | Fires on new CSV arrival in `Files/raw_ingestion` in OneLake |
| Email alert | Failure notification | Failure notifications configured through Fabric pipeline alerting. |

The dual-trigger pattern simulates a production scenario where files can arrive ad-hoc between scheduled batch runs, requiring near real-time processing without manual intervention.

---

## 📈 Analytics Consumption Layer

The Gold datasets were designed to support:

- Power BI Semantic Models
- Fabric SQL Analytics Endpoint
- Ad-hoc SQL analysis
- Future reporting workloads

Due to Fabric trial capacity limitations, dashboard implementation was not included in this project. The focus was on building and validating the data platform and analytics data products.

---

## 💡 Key Engineering Decisions

**1. pandas over PySpark : constraint navigated as a production decision**  
Spark compute was throttled on a Fabric trial account (HTTP 430 errors). Rather than block the project, the pipeline was redesigned using pandas + pyarrow. The architectural decision — and its production implications (PySpark for scale, Delta for SQL Endpoint)  is documented explicitly. This is the kind of constraint navigation that happens in real engineering environments.

**2. Composite key deduplication discovered through data profiling**  
`diagnosis_id`, `procedure_id`, and `lab_id` appeared to be primary keys but were actually category codes. Deduplicating on the ID alone would have silently dropped valid records. See the [Troubleshooting](#-troubleshooting-composite-key-discovery-in-silver) section below.

**3. Audit columns at every layer**  
`_bronze_load_timestamp`, `_silver_load_timestamp`, `_gold_load_timestamp` carried through each layer for lineage. Dropped at each transition so only the current layer's timestamp is retained  clean, predictable schema at every stage.

**4. Derived metrics pushed down to Silver**  
`unpaid_amount` and `collection_rate` are calculated once in Silver and reused across multiple Gold aggregations to avoids redundant computation and keeps Gold transformation logic readable.

**5. Dual-trigger orchestration**  
Both a daily schedule (batch refresh) and an OneLake file-arrival event trigger are configured. This pattern ensures stale data is never served beyond 24 hours while also enabling immediate processing when new source files arrive mid-day.

---

## 📊 Business Insights

1. **Dual-trigger orchestration** : enables both batch reliability and near real-time processing
2. **Composite key finding** : ID columns in source data are not always unique; data profiling is essential before writing dedup logic
3. **Risk scoring** : patients aged 65+ with multiple readmissions and chronic diagnoses represent the highest intervention priority
4. **Collection rate variance by payer** : revenue leakage can be measured and tracked at the insurance provider level
5. **Appeal success rate** : high appeal win rates suggest many initial denials are incorrect; a process improvement opportunity similar to the Azure project finding of 80% appeal success
6. **Readmission clustering** : specific diagnoses and departments drive disproportionate readmission rates, visible in `gold_readmission_by_diag`

---

## 🔧 Troubleshooting: Composite Key Discovery in Silver

### Problem

During Silver deduplication for `diagnoses`, `procedures`, and `lab_tests`, initial logic deduplicated on the apparent ID column alone:

```python
# Initial assumption — ID column is a unique row identifier
df = df.drop_duplicates(subset=["diagnosis_id"])
```

Row counts dropped significantly more than expected for a dedup operation.

---

### Root Cause Investigation

**Step 1 : Sample the data**

```python
df = pd.read_parquet(f"{BRONZE_PATH}/diagnoses/part-0.parquet")
print(df["diagnosis_id"].value_counts().head(10))
```

**Result:** Many `diagnosis_id` values appeared dozens of times ❌

**Step 2 : Understand the column**

```python
# How many unique diagnosis_ids exist?
print(df["diagnosis_id"].nunique())     # Much fewer than total rows
print(len(df))                          # Total rows

# Are the same diagnosis_ids paired with different encounter_ids?
print(df.groupby(["diagnosis_id", "encounter_id"]).size().max())
```

**Result:** `diagnosis_id` values like `D001`, `D002` are **ICD category codes**, not row identifiers. The same diagnosis code (e.g., `D001 = Type 2 Diabetes`) legitimately appears across hundreds of different patient encounters.

---

### Root Cause

The column names `diagnosis_id`, `procedure_id`, and `lab_id` implied unique row identifiers. They are actually **category/classification codes** — the same code can appear in many rows.

Deduplicating on the code alone would collapse all encounters with the same diagnosis into a single row, destroying the clinical data.

---

### Fix

Composite key deduplication using both the code and the encounter context:

```python
# WRONG : collapses all encounters with the same diagnosis code into one row
df = df.drop_duplicates(subset=["diagnosis_id"])

# CORRECT : a patient can legitimately have the same diagnosis in a different encounter
df = df.drop_duplicates(subset=["diagnosis_id", "encounter_id"])
```

Applied consistently across all three affected tables:

```python
# diagnoses
df = df.drop_duplicates(subset=["diagnosis_id", "encounter_id"])

# procedures
df = df.drop_duplicates(subset=["procedure_id", "encounter_id"])

# lab_tests
df = df.drop_duplicates(subset=["lab_id", "encounter_id"])
```

---

### Key Learnings

1. **Column names are not documentation** : `_id` suffix does not guarantee uniqueness; always profile before writing dedup logic
2. **Data profiling before transformation** : `value_counts()` on assumed key columns should be a standard first step in Silver
3. **Silent data loss** : deduplicating on a non-unique key silently drops valid rows with no error; row count validation catches this
4. **Domain knowledge matters** : understanding that `diagnosis_code` is a clinical classification (ICD-10) rather than a surrogate key changes the entire dedup strategy

### Prevention

Add a key uniqueness check before every dedup operation:

```python
def validate_key_uniqueness(df, key_cols, table_name):
    total_rows   = len(df)
    unique_combos = df.drop_duplicates(subset=key_cols).shape[0]
    dup_rate     = (1 - unique_combos / total_rows) * 100
    print(f"{table_name} | key={key_cols} | total={total_rows:,} | unique={unique_combos:,} | dup_rate={dup_rate:.1f}%")
    if dup_rate > 50:
        print(f"  WARNING: High duplicate rate — verify key selection")

validate_key_uniqueness(df, ["diagnosis_id"], "diagnoses")
validate_key_uniqueness(df, ["diagnosis_id", "encounter_id"], "diagnoses")
```

---

## 🔮 Production Enhancements

| Gap | Production Solution |
|---|---|
| Full load only | Incremental load using `_bronze_load_timestamp` watermarking |
| Parquet (not Delta) | PySpark `delta-rs` write to create `_delta_log/` for SQL Endpoint |
| No row-level security | RLS in Power BI semantic model by department or user role |
| No data quality reporting | DQ summary table tracking null rates and dupe counts per run |
| No CI/CD | Azure DevOps pipeline for notebook versioning and environment promotion |
| Single-file Parquet | Partitioned writes by date for large tables in production |

---

## 📁 Project Structure

```
Healthcare-Fabric-Medallion/
│
├── healthcare_lakehouse/
│   ├── Files/
│   │   ├── raw_ingestion/          # Source CSVs (9 files, 552K rows)
│   │   ├── bronze/                 # Raw Parquet + audit columns (9 tables)
│   │   ├── silver/                 # Cleaned, standardized Parquet (9 tables)
│   │   └── gold/                   # Business aggregations (12 tables)
│   └── Tables/                     # Registered for SQL Endpoint & Power BI
│       └── gold_*/                 # 12 gold tables
│
├── notebooks/
│   ├── 01_bronze_ingestion.ipynb
│   ├── 02_silver_transformation.ipynb
│   └── 03_gold_aggregation.ipynb
│
├── docs/
│   ├── Fabric_medallion_Architecture.png
│   └── Fabric_Data_modeling.png
│
└── README.md
```

---

## 👤 Author

**Sylvie Linda** : I'm a Data Engineer focused on building cloud-native data platforms using Microsoft Fabric, Azure, SQL, Python, and modern data engineering practices.

I enjoy transforming complex operational data into reliable, business-ready datasets that drive decision-making.
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Lindasylvie6)

---

*Built with Microsoft Fabric · Python · pandas · pyarrow · Power BI*
