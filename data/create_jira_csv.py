#!/usr/bin/env python3
import csv
import os

print("🚀 Generating Jira Import CSV...")

desktop_path = "/Users/rhitambhaduri/Desktop"
csv_file = f"{desktop_path}/NovaBazaar_Jira_Import.csv"

# Define columns
fieldnames = [
    "Issue Type",
    "Summary",
    "Description",
    "Priority",
    "Epic Link",
    "Story Points",
    "Labels",
    "Acceptance Criteria"
]

# Tickets data
tickets = [
    # --- EPICS ---
    {
        "Issue Type": "Epic",
        "Summary": "EPIC: Platform Foundations & Data Staging",
        "Description": "Establish the governed workspace environment and stage all e-commerce and synthetic source datasets.",
        "Priority": "High",
        "Epic Link": "",
        "Story Points": "",
        "Labels": "foundation",
        "Acceptance Criteria": "1. All DBFS landing folders and Hive databases created.\n2. Delta audit logging tables provisioned.\n3. Olist and synthetic datasets loaded to UC Volume."
    },
    {
        "Issue Type": "Epic",
        "Summary": "EPIC: Bronze Layer Config-Driven Ingestion",
        "Description": "Build a reusable, metadata-driven ingestion framework to load raw source files into Bronze Delta tables incrementally.",
        "Priority": "High",
        "Epic Link": "",
        "Story Points": "",
        "Labels": "bronze",
        "Acceptance Criteria": "1. Pipeline reads source configs dynamically.\n2. Ingestion metadata columns added.\n3. Incremental watermarking logs successfully."
    },
    {
        "Issue Type": "Epic",
        "Summary": "EPIC: Silver Layer Cleansing & Quality Control",
        "Description": "Cleanse, conform, deduplicate, and validate ingested data using an automated Data Quality rule engine and Quarantine router.",
        "Priority": "High",
        "Epic Link": "",
        "Story Points": "",
        "Labels": "silver",
        "Acceptance Criteria": "1. Data Quality scores logged for every run.\n2. Failed records routed to quarantine table.\n3. SCD Type 1 and Type 2 histories merged correctly."
    },
    {
        "Issue Type": "Epic",
        "Summary": "EPIC: Gold Layer Business Star Schema",
        "Description": "Transform cleansed Silver tables into conformed dimension and fact serving tables optimized for analytical reporting.",
        "Priority": "High",
        "Epic Link": "",
        "Story Points": "",
        "Labels": "gold",
        "Acceptance Criteria": "1. Surrogate keys generated for dimensions.\n2. Sales transaction fact and inventory snapshot facts implemented.\n3. Customer 360 table aggregated."
    },
    {
        "Issue Type": "Epic",
        "Summary": "EPIC: Platform Performance, Orchestration & Testing",
        "Description": "Verify pipeline correctness with unit tests, optimize queries, and orchestrate the full end-to-end execution flow.",
        "Priority": "Medium",
        "Epic Link": "",
        "Story Points": "",
        "Labels": "production",
        "Acceptance Criteria": "1. Explain plans show no shuffle skew or cartesian joins.\n2. Automated tests execute without errors.\n3. Parameterized notebook runs consecutively."
    },

    # --- SPRINT 1 TICKETS (M1 & M2) ---
    {
        "Issue Type": "Story",
        "Summary": "NB-101: Provision Metastore Databases and Folders",
        "Description": "As a Data Engineer, I want to initialize the workspace directory structures and create logical medallion databases to separate data life cycles.",
        "Priority": "High",
        "Epic Link": "EPIC: Platform Foundations & Data Staging",
        "Story Points": "3",
        "Labels": "m1,setup",
        "Acceptance Criteria": "- Databases novamart.bronze, silver, and gold exist.\n- Audit schema created under Unity Catalog."
    },
    {
        "Issue Type": "Story",
        "Summary": "NB-102: Build Observability Delta Logging Tables",
        "Description": "As a Platform Lead, I want to create dedicated, managed Delta tables for pipeline logs, quality metrics, and watermarks to support dashboard monitoring.",
        "Priority": "High",
        "Epic Link": "EPIC: Platform Foundations & Data Staging",
        "Story Points": "5",
        "Labels": "m1,monitoring",
        "Acceptance Criteria": "- Tables log_pipeline_execution, log_dq_results, and watermark_tracking are fully queryable.\n- Every column contains functional metadata comments."
    },
    {
        "Issue Type": "Story",
        "Summary": "NB-103: Stage Raw CSV and JSON Datasets to UC Volume",
        "Description": "As a Data Engineer, I want to load the Olist transaction records and synthetic ledger tables into a secure Unity Catalog Volume to enable ingestion processing.",
        "Priority": "High",
        "Epic Link": "EPIC: Platform Foundations & Data Staging",
        "Story Points": "3",
        "Labels": "m2,data",
        "Acceptance Criteria": "- All 15 files successfully placed inside /Volumes/novamart/landing/raw_files/.\n- Preview queries read files from volume paths successfully."
    },

    # --- SPRINT 2 TICKETS (M3) ---
    {
        "Issue Type": "Story",
        "Summary": "NB-201: Develop Config-Driven Ingestion Engine",
        "Description": "As a Data Engineer, I want to build a parameterized PySpark ingestion notebook that dynamically reads source specifications from source_config.json to load files.",
        "Priority": "High",
        "Epic Link": "EPIC: Bronze Layer Config-Driven Ingestion",
        "Story Points": "8",
        "Labels": "m3,ingestion",
        "Acceptance Criteria": "- Single notebook handles CSV, JSON, and Parquet files.\n- Adds metadata columns _source_system, _ingestion_timestamp, _batch_id, and _file_name."
    },
    {
        "Issue Type": "Story",
        "Summary": "NB-202: Implement Incremental Watermarking Ingestion",
        "Description": "As a Data Engineer, I want to integrate high-water-mark checks in the ingestion loop to query only new records since the last run timestamp.",
        "Priority": "High",
        "Epic Link": "EPIC: Bronze Layer Config-Driven Ingestion",
        "Story Points": "5",
        "Labels": "m3,incremental",
        "Acceptance Criteria": "- watermark_tracking table updated on completion.\n- Subsequent runs process zero records if no new files land."
    },

    # --- SPRINT 3 TICKETS (M4) ---
    {
        "Issue Type": "Story",
        "Summary": "NB-301: Build Data Quality Gate and Quarantine Router",
        "Description": "As a CDO, I want to validate column values against pre-configured check rules and route failed rows to quarantine so they do not corrupt downstream tables.",
        "Priority": "High",
        "Epic Link": "EPIC: Silver Layer Cleansing & Quality Control",
        "Story Points": "8",
        "Labels": "m4,quality",
        "Acceptance Criteria": "- Rows with null primary keys or invalid formats routed to quarantine table.\n- Runs log metrics to log_dq_results."
    },
    {
        "Issue Type": "Story",
        "Summary": "NB-302: Implement SCD Type 1 for Seller Dimensions",
        "Description": "As a Data Analyst, I want to overwrite seller details in the Silver layer upon modification so we always hold current seller location records.",
        "Priority": "Medium",
        "Epic Link": "EPIC: Silver Layer Cleansing & Quality Control",
        "Story Points": "3",
        "Labels": "m4,scd1",
        "Acceptance Criteria": "- Updates applied via PySpark MERGE INTO statement.\n- Old values overwritten with zero duplicate records."
    },
    {
        "Issue Type": "Story",
        "Summary": "NB-303: Implement SCD Type 2 for Customer History",
        "Description": "As a CMO, I want to version customer address changes so we can run accurate regional sales analyses based on historical locations.",
        "Priority": "High",
        "Epic Link": "EPIC: Silver Layer Cleansing & Quality Control",
        "Story Points": "8",
        "Labels": "m4,scd2",
        "Acceptance Criteria": "- Updates close the active record (current=false, end_date=now) and insert the new row.\n- Surrogate keys map historical ranges."
    },

    # --- SPRINT 4 TICKETS (M5) ---
    {
        "Issue Type": "Story",
        "Summary": "NB-401: Model Conformed Dimensions with Surrogate Keys",
        "Description": "As an Enterprise Architect, I want to build conformed dimension tables (dim_customer, dim_product, dim_date) using monotonically increasing keys.",
        "Priority": "High",
        "Epic Link": "EPIC: Gold Layer Business Star Schema",
        "Story Points": "5",
        "Labels": "m5,modeling",
        "Acceptance Criteria": "- Dim tables created in novamart.gold schema.\n- Includes a static, role-playing date dimension from 2016-2030."
    },
    {
        "Issue Type": "Story",
        "Summary": "NB-402: Build Sales Transaction Fact Table",
        "Description": "As a Sales Lead, I want a central fact_sales table containing order quantities, prices, freight amounts, and cost center values mapped to keys.",
        "Priority": "High",
        "Epic Link": "EPIC: Gold Layer Business Star Schema",
        "Story Points": "8",
        "Labels": "m5,fact",
        "Acceptance Criteria": "- central fact_sales table populated from order items, payments, and dimensions.\n- Query times return in < 30 seconds."
    },
    {
        "Issue Type": "Story",
        "Summary": "NB-403: Aggregate Customer 360 Analytics Serving Table",
        "Description": "As a Marketing Analyst, I want a customer_360 table aggregating total orders, lifetime value (LTV), review scores, and segment labels.",
        "Priority": "Medium",
        "Epic Link": "EPIC: Gold Layer Business Star Schema",
        "Story Points": "5",
        "Labels": "m5,serving",
        "Acceptance Criteria": "- Table populated from facts and dimensions.\n- Ready for BI dashboard connections."
    },

    # --- SPRINT 5 TICKETS (M6 & M7) ---
    {
        "Issue Type": "Story",
        "Summary": "NB-501: Perform Customer RFM Cohort Segmentation",
        "Description": "As a CMO, I want to calculate customer Recency, Frequency, and Monetary scores using Spark SQL window functions to target campaigns.",
        "Priority": "Medium",
        "Epic Link": "EPIC: Platform Performance, Orchestration & Testing",
        "Story Points": "5",
        "Labels": "m6,analytics",
        "Acceptance Criteria": "- Calculations use NTILE and ROW_NUMBER window functions.\n- Groups customers into loyal, champion, and churn segments."
    },
    {
        "Issue Type": "Story",
        "Summary": "NB-502: Design Parameterized Pipeline Orchestrator",
        "Description": "As an Ops Lead, I want an orchestration notebook that triggers setup, ingestion, cleaning, and modeling tasks consecutively with error logging.",
        "Priority": "High",
        "Epic Link": "EPIC: Platform Performance, Orchestration & Testing",
        "Story Points": "8",
        "Labels": "m7,orchestration",
        "Acceptance Criteria": "- Notebook uses dbutils.notebook.run().\n- Automatically catches failures and writes to log_pipeline_execution."
    },

    # --- SPRINT 6 TICKETS (M8 & M9) ---
    {
        "Issue Type": "Story",
        "Summary": "NB-601: Optimize Star Schema Join Performance",
        "Description": "As a Lead Engineer, I want to profile the execution plan and apply broadcast joins and Z-Ordering to eliminate shufflings.",
        "Priority": "Medium",
        "Epic Link": "EPIC: Platform Performance, Orchestration & Testing",
        "Story Points": "5",
        "Labels": "m8,performance",
        "Acceptance Criteria": "- Broadcast joins applied on dimensions < 100MB.\n- Delta tables Z-Ordered by join keys."
    },
    {
        "Issue Type": "Story",
        "Summary": "NB-602: Implement PySpark Automated Test Suite",
        "Description": "As a QA Engineer, I want unit and integration tests executing schema checks and validation counts to prevent pipeline regressions.",
        "Priority": "High",
        "Epic Link": "EPIC: Platform Performance, Orchestration & Testing",
        "Story Points": "5",
        "Labels": "m9,testing",
        "Acceptance Criteria": "- Tests run on mock dataframes.\n- Execution prints a clear PASSED/FAILED suite report."
    }
]

# Write to CSV
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(tickets)

print(f"🎉 Jira import CSV created successfully on your Desktop: {csv_file}")
