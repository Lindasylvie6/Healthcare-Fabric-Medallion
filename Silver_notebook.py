#!/usr/bin/env python
# coding: utf-8

# ## Silver_layer
# 
# New notebook

# # **<mark>Silver Transformation</mark>**

# In[4]:


# ══════════════════════════════════════════════
# CELL 1 — Complete setup (run this FIRST, always)
# ══════════════════════════════════════════════
import pandas as pd, glob, os, datetime as dt
from deltalake import write_deltalake

BRONZE_PATH = "/lakehouse/default/Files"
SILVER_PATH = "/lakehouse/default/Tables"

DATASETS = [
    "patients", "encounters", "providers", "diagnoses", "procedures",
    "medications", "lab_tests", "claims_and_billing", "denials",
]

def read_bronze(name):
    folder = f"{BRONZE_PATH}/Raw_data{name}"
    files = [f for f in glob.glob(f"{folder}/**/*", recursive=True) if os.path.isfile(f)]
    if not files:
        raise FileNotFoundError(f"Nothing in {folder} — is healthcare_lakehouse the default?")
    df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)
    df["_source_file"] = name
    df["_ingested_at"] = dt.datetime.utcnow()
    return df

print("Setup ready. DATASETS:", len(DATASETS), "tables")




# In[6]:


# ══════════════════════════════════════════════
# CELL 2 — Turn ALL 9 raw folders into Silver Delta tables
# ══════════════════════════════════════════════

def clean(df):
    # 1. trim stray spaces on text columns, turn blanks into nulls
    for c in df.columns:
        if df[c].dtype == "object":
            df[c] = df[c].str.strip()
    df = df.replace("", None)

    # 2. turn date TEXT (like "03-01-2025") into real dates
    for c in df.columns:
        if "date" in c.lower() or c.lower() == "dob":
            df[c] = pd.to_datetime(df[c], dayfirst=True, errors="coerce")

    # 3. drop only exact-copy rows
    return df.drop_duplicates()

for name in DATASETS:                       # loop over all 9
    df = clean(read_bronze(name))
    write_deltalake(
        f"{SILVER_PATH}/silver_{name}",
        df,
        mode="overwrite",
        storage_options={"allow_unsafe_rename": "true"},
    )
    print(f" silver_{name}: {len(df):,} rows")

print("All 9 Silver tables built.")


# # <mark>Troubleshoot</mark>

# In[7]:


# ===== SILVER REBUILD — SQL-endpoint-safe date types. Run this ONE cell. =====
import pandas as pd, glob, os, datetime as dt
from deltalake import write_deltalake

BRONZE_PATH = "/lakehouse/default/Files"
SILVER_PATH = "/lakehouse/default/Tables"
DATASETS = ["patients","encounters","providers","diagnoses","procedures",
            "medications","lab_tests","claims_and_billing","denials"]

def read_bronze(name):
    folder = f"{BRONZE_PATH}/Raw_data{name}"
    files = [f for f in glob.glob(f"{folder}/**/*", recursive=True) if os.path.isfile(f)]
    if not files:
        raise FileNotFoundError(f"Nothing in {folder}")
    df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)
    df["_source_file"] = name
    df["_ingested_at"] = dt.datetime.now(dt.timezone.utc)   # tz-aware = supported
    return df

def clean(df):
    for c in df.columns:
        if df[c].dtype == "object":
            df[c] = df[c].str.strip()
    df = df.replace("", None)
    for c in df.columns:
        if "date" in c.lower() or c.lower() == "dob":
            # parse, then drop the time part -> DATE type the SQL endpoint accepts
            df[c] = pd.to_datetime(df[c], dayfirst=True, errors="coerce").dt.date
    return df.drop_duplicates()

for name in DATASETS:
    df = clean(read_bronze(name))
    write_deltalake(f"{SILVER_PATH}/silver_{name}", df, mode="overwrite",
                    storage_options={"allow_unsafe_rename": "true"})
    print(f"silver_{name}: {len(df):,} rows, {len(df.columns)} cols")

print("\nDone. Now REFRESH the SQL endpoint to pick up the new column types.")



