# 🏥 Healthcare Analytics | Microsoft Fabric Medallion Architecture

## Project Overview
End-to-end data engineering project built on Microsoft Fabric using 
the Medallion Architecture (Bronze → Silver → Gold) with a Power BI dashboard.

## Dataset
9 CSV files covering a fictional healthcare system:
patients, encounters, providers, diagnoses, procedures,
medications, lab_tests, claims_and_billing, denials

## Tech Stack
| Tool | Purpose |
|------|---------|
| Microsoft Fabric | Unified analytics platform |
| OneLake | Central data lake storage |
| Lakehouse | Bronze, Silver, Gold layers |
| SQL (T-SQL) | Transformations across all layers |
| Python / PySpark | Data validation and notebooks |
| Power Query | Data prep in Power BI |
| Power BI | Final dashboard |
| GitHub | Version control |

## Architecture
