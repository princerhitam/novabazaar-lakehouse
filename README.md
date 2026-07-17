# 🏬 NovaBazaar — Enterprise Lakehouse Data Engineering Platform

[![Databricks](https://img.shields.io/badge/Databricks-CE-FF3621?style=flat&logo=databricks&logoColor=white)](https://community.cloud.databricks.com/)
[![PySpark](https://img.shields.io/badge/PySpark-3.5-E25A1C?style=flat&logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![Delta Lake](https://img.shields.io/badge/Delta%20Lake-3.2-003366?style=flat&logo=delta&logoColor=white)](https://delta.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Enterprise-grade data platform built on Databricks Community Edition, powered by real-world Olist e-commerce data and synthetic augmentation — engineered to demonstrate production-caliber Lakehouse patterns from ingestion to analytics.**

---

## 📋 Overview

NovaBazaar is a comprehensive data engineering platform that implements the **Medallion Architecture** (Bronze → Silver → Gold) on Databricks Community Edition. It ingests, transforms, and serves data from **15 heterogeneous sources** spanning sales, customer, product, HR, finance, inventory, and marketing domains.

The platform is designed as a progressive learning and portfolio project — each milestone builds on the last, escalating from junior-level ingestion pipelines to architect-grade orchestration and observability.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        NovaBazaar Enterprise Lakehouse                              │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐  │
│   │   LANDING    │     │    BRONZE    │     │    SILVER    │     │     GOLD     │  │
│   │   (Raw)      │────▶│  (Ingested)  │────▶│  (Cleansed)  │────▶│  (Curated)   │  │
│   └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘  │
│         │                     │                     │                     │         │
│   • CSV / JSON         • Schema-on-Read      • Data Quality       • Star Schema   │
│   • 15 Sources         • Metadata Columns    • Deduplication      • Aggregations  │
│   • Olist + Synth      • Audit Tracking      • Type Casting       • KPIs / Marts  │
│   • DBFS FileStore     • Delta Format        • SCD Type 2         • Serving Layer │
│                                                                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   ┌──────────────────────────────────────────────────────────────────────────────┐  │
│   │                        CROSS-CUTTING CONCERNS                               │  │
│   ├──────────────────────────────────────────────────────────────────────────────┤  │
│   │  🔧 Config-Driven Ingestion  │  📊 Data Quality Framework                  │  │
│   │  🔄 CDC / SCD Type 2         │  📈 Observability & Logging                 │  │
│   │  🧪 Testing Framework        │  🔐 Access Control Patterns                 │  │
│   │  📦 Orchestration             │  📝 Data Lineage Tracking                  │  │
│   └──────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
                    ┌─────────────────────────────────────┐
                    │         SOURCE SYSTEMS               │
                    │                                       │
                    │  Olist (9 CSVs)  │  Synthetic (6)    │
                    └────────┬──────────┬──────────────────┘
                             │          │
                    ┌────────▼──────────▼──────────────────┐
                    │         LANDING ZONE                  │
                    │   /FileStore/novabazaar/landing/      │
                    │   Raw files • No transformations      │
                    └────────────────┬─────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │         BRONZE LAYER                  │
                    │   novabazaar_bronze database          │
                    │   Delta Tables • Audit columns        │
                    │   Load patterns: Full / Incr / CDC    │
                    └────────────────┬─────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │         SILVER LAYER                  │
                    │   novabazaar_silver database          │
                    │   Cleaned • Typed • Deduplicated      │
                    │   SCD2 • Validated • Standardized     │
                    └────────────────┬─────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │          GOLD LAYER                   │
                    │   novabazaar_gold database            │
                    │   Star Schema • Fact/Dim tables       │
                    │   Aggregated KPIs • Serving views     │
                    └──────────────────────────────────────┘
```

---

## ⚙️ Tech Stack

| Layer           | Technology                     | Purpose                                    |
|-----------------|--------------------------------|--------------------------------------------|
| **Compute**     | Databricks Community Edition   | Managed Spark clusters & notebooks         |
| **Processing**  | PySpark 3.5+                   | Distributed data processing                |
| **Query**       | Spark SQL                      | Declarative transformations & analytics    |
| **Storage**     | Delta Lake 3.2+                | ACID transactions, time travel, schema evo |
| **Data**        | Olist E-Commerce Dataset       | 9 real-world Brazilian e-commerce CSVs     |
| **Augmentation**| Synthetic Data (Faker/Custom)  | 6 additional enterprise data sources       |
| **Config**      | JSON (Metadata-Driven)         | Source configuration & pipeline control    |
| **Testing**     | PySpark + Custom Framework     | Data quality & pipeline validation         |
| **Language**    | Python 3.10+                   | Pipeline logic & orchestration             |

---

## 📁 Project Structure

```
novabazaar-lakehouse/
│
├── README.md                           # This file
├── .gitignore                          # Python/Databricks ignores
├── LICENSE                             # MIT License
│
├── config/
│   ├── source_config.json              # Metadata-driven config for 15 sources
│   ├── quality_rules.json              # Data quality rule definitions
│   └── pipeline_config.json            # Pipeline execution parameters
│
├── data/
│   ├── olist/                          # Raw Olist CSVs (gitignored)
│   │   ├── olist_orders_dataset.csv
│   │   ├── olist_order_items_dataset.csv
│   │   ├── olist_order_payments_dataset.csv
│   │   ├── olist_order_reviews_dataset.csv
│   │   ├── olist_customers_dataset.csv
│   │   ├── olist_products_dataset.csv
│   │   ├── olist_sellers_dataset.csv
│   │   ├── olist_geolocation_dataset.csv
│   │   └── product_category_name_translation.csv
│   ├── synthetic/                      # Generated synthetic data (gitignored)
│   │   ├── employees.csv
│   │   ├── general_ledger.csv
│   │   ├── inventory_snapshots.json
│   │   ├── marketing_campaigns.json
│   │   ├── promotions.csv
│   │   └── exchange_rates.csv
│   └── cdc/                            # CDC change feeds (gitignored)
│
├── notebooks/
│   ├── 00_setup/
│   │   ├── 00_environment_setup.py     # Cluster config & library installs
│   │   └── 01_dbfs_upload.py           # Upload local data to DBFS landing
│   ├── 01_bronze/
│   │   ├── bronze_ingestion_full.py    # Full-load ingestion pipeline
│   │   ├── bronze_ingestion_incr.py    # Incremental ingestion pipeline
│   │   ├── bronze_ingestion_cdc.py     # CDC ingestion pipeline
│   │   └── bronze_ingestion_snapshot.py # Snapshot ingestion pipeline
│   ├── 02_silver/
│   │   ├── silver_cleansing.py         # Data cleansing & standardization
│   │   ├── silver_dedup.py             # Deduplication logic
│   │   ├── silver_scd2.py              # SCD Type 2 implementation
│   │   └── silver_quality_checks.py    # Quality validation framework
│   ├── 03_gold/
│   │   ├── gold_dim_tables.py          # Dimension table builders
│   │   ├── gold_fact_tables.py         # Fact table builders
│   │   ├── gold_aggregations.py        # Pre-computed aggregations
│   │   └── gold_serving_views.py       # Materialized views for consumption
│   ├── 04_orchestration/
│   │   ├── pipeline_orchestrator.py    # End-to-end pipeline controller
│   │   └── dependency_graph.py         # DAG-based execution ordering
│   └── 05_analytics/
│       ├── sales_analytics.py          # Sales domain analysis
│       ├── customer_analytics.py       # Customer domain analysis
│       └── operational_kpis.py         # Cross-domain KPI dashboards
│
├── src/
│   ├── __init__.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── base_ingestor.py            # Abstract base ingestion class
│   │   ├── full_load.py                # Full load strategy
│   │   ├── incremental_load.py         # Incremental load strategy
│   │   ├── cdc_processor.py            # CDC processing strategy
│   │   └── snapshot_loader.py          # Snapshot load strategy
│   ├── transformations/
│   │   ├── __init__.py
│   │   ├── cleansing.py                # Data cleansing utilities
│   │   ├── deduplication.py            # Dedup logic
│   │   ├── scd.py                      # SCD implementations
│   │   └── type_casting.py            # Schema enforcement & casting
│   ├── quality/
│   │   ├── __init__.py
│   │   ├── rule_engine.py              # Quality rule evaluation engine
│   │   ├── validators.py               # Column-level validators
│   │   └── reporter.py                 # Quality report generator
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config_loader.py            # JSON config parser
│   │   ├── logging_utils.py            # Structured logging
│   │   ├── spark_utils.py              # Spark session & helpers
│   │   └── delta_utils.py              # Delta Lake operations
│   └── orchestration/
│       ├── __init__.py
│       ├── dag.py                      # Pipeline DAG definition
│       └── scheduler.py               # Execution scheduler
│
├── tests/
│   ├── __init__.py
│   ├── test_ingestion.py               # Ingestion unit tests
│   ├── test_transformations.py         # Transformation unit tests
│   ├── test_quality.py                 # Quality framework tests
│   └── test_utils.py                   # Utility function tests
│
├── generators/
│   ├── generate_employees.py           # Synthetic HR data generator
│   ├── generate_general_ledger.py      # Synthetic finance data generator
│   ├── generate_inventory.py           # Synthetic inventory snapshots
│   ├── generate_marketing.py           # Synthetic marketing campaigns
│   ├── generate_promotions.py          # Synthetic promotions data
│   ├── generate_exchange_rates.py      # Synthetic FX rates
│   └── generate_cdc_feeds.py           # CDC change event simulator
│
└── docs/
    ├── data_dictionary.md              # Column-level documentation
    ├── architecture.md                 # Detailed architecture deep-dive
    ├── runbook.md                      # Operational procedures
    └── milestones.md                   # Milestone tracking & progress
```

---

## 🎯 Milestones

The project is structured as a progressive learning path from **Junior Data Engineer** to **Data Architect**:

| Milestone | Title | Level | Description |
|-----------|-------|-------|-------------|
| **M1** | Foundation & Environment Setup | Junior | Set up Databricks CE workspace, upload Olist data to DBFS, create databases, validate Spark connectivity |
| **M2** | Bronze Layer — Full Load Ingestion | Junior | Build metadata-driven ingestion framework reading `source_config.json`, ingest all 15 sources as Delta tables with audit columns (`_ingestion_timestamp`, `_source_file`, `_batch_id`) |
| **M3** | Bronze Layer — Advanced Load Patterns | Mid | Implement incremental loads (watermark-based), CDC processing (merge operations), and snapshot loading with partition management |
| **M4** | Silver Layer — Cleansing & Standardization | Mid | Data type enforcement, null handling, string standardization, deduplication, and business rule application across all domains |
| **M5** | Silver Layer — SCD Type 2 & History | Mid-Senior | Implement Slowly Changing Dimensions Type 2 for customer, product, employee, and promotion tables using Delta Lake merge |
| **M6** | Data Quality Framework | Senior | Build a rule-based quality engine: completeness, uniqueness, referential integrity, range checks, anomaly detection — with quarantine tables and dashboards |
| **M7** | Gold Layer — Star Schema & Analytics | Senior | Design and build dimensional model: fact tables (orders, payments, reviews, GL entries), dimension tables (customer, product, seller, date, geography) |
| **M8** | Orchestration & Pipeline Management | Senior | DAG-based pipeline orchestration with dependency resolution, retry logic, checkpoint management, and end-to-end lineage tracking |
| **M9** | Observability, Testing & Production Patterns | Architect | Comprehensive test suite, structured logging, performance benchmarking, cost optimization analysis, and production deployment playbook |

---

## 🚀 Getting Started

### Prerequisites

- **Databricks Community Edition** account — [Sign up free](https://community.cloud.databricks.com/login.html)
- **Python 3.10+** (for local synthetic data generation)
- **Olist Dataset** — [Download from Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-username/novabazaar-lakehouse.git
cd novabazaar-lakehouse

# 2. Generate synthetic data (local)
pip install faker pandas
python generators/generate_employees.py
python generators/generate_general_ledger.py
python generators/generate_inventory.py
python generators/generate_marketing.py
python generators/generate_promotions.py
python generators/generate_exchange_rates.py

# 3. Upload to Databricks
#    - Import notebooks/ into your Databricks workspace
#    - Upload data/ contents to DBFS via Databricks UI or CLI
#    - Run 00_setup/00_environment_setup.py first

# 4. Execute pipelines
#    - Run bronze ingestion notebooks
#    - Run silver transformation notebooks
#    - Run gold layer builders
```

---

## 📊 Data Sources

| # | Source | Domain | Format | Load Pattern | Records (Est.) |
|---|--------|--------|--------|-------------|----------------|
| 1 | `olist_orders` | Sales | CSV | Full | ~100K |
| 2 | `olist_order_items` | Sales | CSV | Full | ~113K |
| 3 | `olist_order_payments` | Sales | CSV | Full | ~104K |
| 4 | `olist_order_reviews` | Customer | CSV | Full | ~100K |
| 5 | `olist_customers` | Customer | CSV | CDC | ~100K |
| 6 | `olist_products` | Product | CSV | CDC | ~33K |
| 7 | `olist_sellers` | Seller | CSV | Full | ~3K |
| 8 | `olist_geolocation` | Reference | CSV | Full | ~1M |
| 9 | `product_category_translation` | Reference | CSV | Full | ~71 |
| 10 | `employees` | HR | CSV | CDC | ~5K |
| 11 | `general_ledger` | Finance | CSV | Incremental | ~50K |
| 12 | `inventory_snapshots` | Inventory | JSON | Snapshot | ~20K |
| 13 | `marketing_campaigns` | Marketing | JSON | Full | ~10K |
| 14 | `promotions` | Marketing | CSV | CDC | ~2K |
| 15 | `exchange_rates` | Finance | CSV | Full | ~5K |

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Olist](https://olist.com/) for the open Brazilian e-commerce dataset
- [Databricks](https://databricks.com/) for Community Edition access
- [Delta Lake](https://delta.io/) for open-source lakehouse storage

---

<p align="center">
  <strong>NovaBazaar</strong> — Engineering data, one layer at a time. 🏗️
</p>
