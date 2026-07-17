# NovaBazaar Data Platform Architecture Blueprint

This document outlines the architectural blueprint for the NovaBazaar Enterprise Data Platform, built using Databricks Community Edition, PySpark, Spark SQL, and Delta Lake.

## 1. Medallion Layer Specifications

The platform is designed around the **Medallion Architecture**, structured to build data maturity and clean state incrementally:

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     BRONZE      │       │     SILVER      │       │      GOLD       │
│  Raw / Landing  │ ───  │  Clean / Standard│ ───  │ Star Schema/KPI │
│  (Append-Only)  │       │   (SCD1 / SCD2) │       │   (Curated)     │
└─────────────────┘       └─────────────────┘       └─────────────────┘
```

### Bronze Layer (Raw Ingestion)
- **Role**: Raw append-only staging area.
- **Rules**: Keep source format schemas. No datatype conversions, value mapping, or filtering.
- **Enrichment**: Ingestion metadata added:
  - `_source_system`: Source identifier
  - `_ingestion_timestamp`: UTC Timestamp of process run
  - `_file_name`: Source file path
  - `_batch_id`: UUID of ingestion run
  - `_load_date`: Date partition column

### Silver Layer (Cleansed and Standardized)
- **Role**: Unified enterprise-wide Single Source of Truth (SSOT).
- **Cleansing**: Cast types, standardize strings (trim, uppercase, formatting), handle nulls, and deduplicate.
- **CDC and History**:
  - Apply Change Data Capture (CDC) events using `MERGE INTO`.
  - Slowly Changing Dimension (SCD) Type 1 for reference tables.
  - SCD Type 2 (history tracking) for core master entities (`customers`, `products`, `employees`).
- **Data Quality Gates**: Automated constraints applied. Fails on CRITICAL rules, routes failures to `_quarantine`.

### Gold Layer (Business Analytics and Serving)
- **Role**: Dimensional models optimized for high-performance business intelligence.
- **Design**: Star Schema design with conformed dimensions and facts.
- **Features**: Surrogate keys generated, role-playing date dimensions, and summary aggregation tables.

---

## 2. Data Flow & Integration Mapping

```
                                  LANDING ZONE (DBFS FileStore)
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
              [Olist CSV Data]                               [Synthetic Data]
           - Customers, Orders, Items,                     - HR Employees, GL entries,
             Payments, Reviews, Geoloc                     - Inventory, Promotions, FX
                      │                                               │
                      ▼                                               ▼
              [BRONZE LAYER]                                   [BRONZE LAYER]
             novabazaar_bronze                                novabazaar_bronze
                      │                                               │
                      ▼                                               ▼
              [SILVER LAYER]                                   [SILVER LAYER]
             novabazaar_silver                                novabazaar_silver
           Cleaned, Deduplicated,                           Cleaned, Standardized,
           SCD Type 1 & 2 History                           SCD Type 1 & 2 History
                      │                                               │
                      └───────────────────────┬───────────────────────┘
                                              │
                                              ▼
                                         [GOLD LAYER]
                                       novabazaar_gold
                                  Dimensions & Fact Tables
                                     Marts & BI Analytics
```

---

## 3. Storage and File Optimization
- **Table Format**: Delta Lake format exclusively for ACID transactions, version history (Time Travel), and fast queries.
- **Compaction**: `OPTIMIZE` commands compact small files into 1GB blocks.
- **Query Optimization**: `Z-ORDER BY` on high-cardinality join columns (e.g., `product_id`, `customer_id`).
- **Partitioning**:
  - Bronze: `_load_date`
  - Silver/Gold: Business dates (e.g. `order_date`) where tables exceed 50GB.
