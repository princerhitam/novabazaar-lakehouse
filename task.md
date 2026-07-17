# Project Task Board — NovaBazaar Lakehouse

## Medallion Data Platform Lifecycle

- [x] **Milestone 1: Foundation & Environment Setup**
  - [x] Create project workspace & folder structure
  - [x] Initialize Git repository & branch strategy
  - [x] Draft architecture blueprint & data dictionary
  - [x] Set up config-driven metadata rules (`source_config.json`)
  - [x] Write environment setup notebook (`00_environment_setup.py`)
  - [x] Push foundation code to `develop` branch

- [x] **Milestone 2: Synthetic Data Generation**
  - [x] Download Olist Core E-Commerce Dataset
  - [x] Generate synthetic exchange rates and campaigns
  - [x] Generate synthetic employees & promotions (Day 1 + Day 2)
  - [x] Generate synthetic general ledger linked to orders
  - [x] Generate synthetic inventory snapshot history
  - [x] Generate customer and product CDC snapshots
  - [x] Write DBFS upload guide notebook (`01_data_upload_guide.py`)

- [ ] **Milestone 3: Bronze Layer — Raw Ingestion**
  - [ ] Build metadata-driven generic ingestion pipeline
  - [ ] Implement incremental ingestion watermark tracking
  - [ ] Ingest Olist transaction tables (orders, items, payments)
  - [ ] Ingest reference, HR, finance, and marketing tables
  - [ ] Stage landing data on DBFS and load into Bronze Delta tables
  - [ ] Set up pipeline logging and error metrics integration

- [ ] **Milestone 4: Silver Layer — Cleansing & Conforming**
  - [ ] Implement reusable Data Quality (DQ) validation framework
  - [ ] Create bad-data quarantine routing system
  - [ ] Build SCD Type 1 lookup tables (stores, promotions, channels)
  - [ ] Build SCD Type 2 tracking for customers, products, and employees
  - [ ] Integrate CDC change-merge updates (inserts, updates, deletes)
  - [ ] Run cross-layer count & sum reconciliation audits

- [ ] **Milestone 5: Gold Layer — Business Models**
  - [ ] Create date & time conformed dimensions
  - [ ] Implement fact_sales (transaction grain)
  - [ ] Implement fact_inventory_snapshot (periodic snapshot)
  - [ ] Build fact_financial_transaction with accounting entries
  - [ ] Build customer_360 analytic serving table
  - [ ] Compute aggregated daily KPI summaries

- [ ] **Milestone 6: Advanced Analytics & SQL**
  - [ ] Build cohort and customer retention metrics
  - [ ] Implement RFM customer segmentation model
  - [ ] Run basket analysis queries for item associations
  - [ ] Validate financial balances vs payments reconciliation

- [ ] **Milestone 7: Enterprise Frameworks**
  - [ ] Set up parameterized orchestrator runner
  - [ ] Build operational pipeline execution health dashboard

- [ ] **Milestone 8: Performance Tuning & Optimization**
  - [ ] Profile explain plans for shuffle & join bottlenecks
  - [ ] Apply Z-Ordering, partitioning, and broadcast optimizations
  - [ ] Handle data skew with salting techniques

- [ ] **Milestone 9: Testing & Production Readiness**
  - [ ] Build PySpark unit tests for cleansing functions
  - [ ] Implement validation suite for tables and schemas
  - [ ] Finalize production runbook and repository documentations
