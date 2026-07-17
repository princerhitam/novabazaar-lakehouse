# Databricks notebook source

# COMMAND ----------

# ============================================================================
# NOTEBOOK: 00_environment_setup
# ============================================================================
# Layer        : Setup / Bootstrap
# Domain       : Infrastructure
# Author       : Data Engineering Team
# Created Date : 2026-07-17
# Last Modified: 2026-07-17
# ============================================================================
#
# DESCRIPTION:
#   This notebook bootstraps the entire NovaBazaar Lakehouse environment.
#   It aligns with the modern Databricks Unity Catalog architecture.
#
#   Steps performed:
#     1. Verifies Unity Catalog and pre-existing schemas.
#     2. Creates custom schemas for operational monitoring (`audit`, `config`).
#     3. Provisions managed Delta tables for the audit and logging framework.
#     4. Performs end-to-end verification of files in UC Volumes.
#
# BUSINESS CONTEXT:
#   A repeatable, governed environment setup is essential for enterprise operations.
#   Instead of hardcoding legacy DBFS storage paths (which present security
#   vulnerabilities and lack row/column level permission checks), this setup
#   fully leverages Unity Catalog:
#     • Managed Catalogs structure datasets logically under catalogs and schemas.
#     • UC Volumes manage raw files securely (replacing public DBFS mounts).
#     • Managed Tables decouple physical path management from table metadata.
#
# DEPENDENCIES:
#   • Databricks Runtime 13.x+ with Unity Catalog enabled
#   • Target Catalog 'novamart' and Volume 'raw_files' pre-created
#
# CHANGE LOG:
#   2026-07-17 | Data Engineering Team | Aligned with Unity Catalog & Volumes
# ============================================================================

# COMMAND ----------

# ============================================================================
# STEP 1 — Verify Unity Catalog & Create Custom Schemas
# ============================================================================
# We use the catalog 'novabazaar' as our central container. We create schemas
# for 'audit' and 'config' to store operational and execution metadata.
# ============================================================================

# COMMAND ----------

CATALOG = "novabazaar"

# Create schemas
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.audit")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.config")

print("✅ Schemas verified/created under catalog 'novabazaar':")
print("  - novabazaar.bronze  (Core Bronze tables)")
print("  - novabazaar.silver  (Core Silver tables)")
print("  - novabazaar.gold    (Core Gold tables)")
print("  - novabazaar.audit   (Operational audit tables)")
print("  - novabazaar.config  (Metadata configs)")

# COMMAND ----------

# ============================================================================
# STEP 2 — Provision Managed Delta Audit Tables
# ============================================================================
# We create 5 audit tables under the 'novamart.audit' schema. Because these
# are Unity Catalog managed tables, we do not specify raw DBFS locations.
# Databricks automatically manages optimized cloud storage for these tables.
# ============================================================================

# COMMAND ----------

# 1. Pipeline Execution Log
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {CATALOG}.audit.log_pipeline_execution (
        log_id              STRING      COMMENT 'Unique identifier for the log entry (UUID)',
        pipeline_name       STRING      COMMENT 'Name of the pipeline (e.g. bronze_olist_orders)',
        pipeline_run_id     STRING      COMMENT 'Unique run identifier — groups all steps in one execution',
        step_name           STRING      COMMENT 'Step within the pipeline (e.g. read_source, validate, write)',
        step_sequence       INT         COMMENT 'Ordinal position of the step',
        log_level           STRING      COMMENT 'Severity: INFO | WARN | ERROR',
        message             STRING      COMMENT 'Human-readable log message',
        records_read        LONG        COMMENT 'Number of records read in this step',
        records_written     LONG        COMMENT 'Number of records successfully written',
        records_rejected    LONG        COMMENT 'Number of records rejected / quarantined',
        start_timestamp     TIMESTAMP   COMMENT 'Step start time (UTC)',
        end_timestamp       TIMESTAMP   COMMENT 'Step end time (UTC)',
        duration_seconds    DOUBLE      COMMENT 'Wall-clock duration of the step',
        status              STRING      COMMENT 'Step outcome: SUCCESS | FAILED | SKIPPED',
        error_message       STRING      COMMENT 'Error details when status = FAILED',
        notebook_path       STRING      COMMENT 'Full Databricks notebook path that executed this step',
        created_timestamp   TIMESTAMP   COMMENT 'Row creation timestamp (UTC)'
    )
    USING DELTA
    COMMENT 'Managed table tracking pipeline executions and run metrics'
""")
print("✅ Table created/verified: novamart.audit.log_pipeline_execution")

# 2. Data Quality Results Log
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {CATALOG}.audit.log_dq_results (
        dq_run_id           STRING      COMMENT 'Unique DQ run identifier (UUID)',
        pipeline_run_id     STRING      COMMENT 'Links back to log_pipeline_execution',
        table_name          STRING      COMMENT 'Fully qualified table under test',
        rule_id             STRING      COMMENT 'Rule identifier (e.g. CHK_NOT_NULL_order_id)',
        rule_description    STRING      COMMENT 'Human-readable description of the check',
        total_records       LONG        COMMENT 'Total records evaluated',
        passed_records      LONG        COMMENT 'Records that passed the rule',
        failed_records      LONG        COMMENT 'Records that failed the rule',
        quality_score       DOUBLE      COMMENT 'Pass rate: passed / total (0.0 – 1.0)',
        severity            STRING      COMMENT 'Rule severity: CRITICAL | WARNING | INFO',
        status              STRING      COMMENT 'Overall result: PASS | FAIL | WARN',
        run_timestamp       TIMESTAMP   COMMENT 'When the DQ check was executed (UTC)'
    )
    USING DELTA
    COMMENT 'Managed table tracking automated data quality validations'
""")
print("✅ Table created/verified: novamart.audit.log_dq_results")

# 3. Source-to-Target Reconciliation Log
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {CATALOG}.audit.log_reconciliation (
        recon_id            STRING      COMMENT 'Unique reconciliation identifier (UUID)',
        pipeline_run_id     STRING      COMMENT 'Links back to log_pipeline_execution',
        source_table        STRING      COMMENT 'Fully qualified source table / path',
        target_table        STRING      COMMENT 'Fully qualified target table / path',
        source_count        LONG        COMMENT 'Row count in source',
        target_count        LONG        COMMENT 'Row count in target',
        count_match         BOOLEAN     COMMENT 'True when source_count == target_count',
        source_sum          DOUBLE      COMMENT 'Control total from source (e.g. SUM of amount)',
        target_sum          DOUBLE      COMMENT 'Control total from target',
        sum_match           BOOLEAN     COMMENT 'True when source_sum ≈ target_sum within tolerance',
        variance_pct        DOUBLE      COMMENT 'Percentage variance between source and target',
        status              STRING      COMMENT 'Reconciliation outcome: MATCH | MISMATCH',
        run_timestamp       TIMESTAMP   COMMENT 'When the reconciliation ran (UTC)'
    )
    USING DELTA
    COMMENT 'Managed table tracking financial and row-count reconciliation logs'
""")
print("✅ Table created/verified: novamart.audit.log_reconciliation")

# 4. CDC Statistics Log
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {CATALOG}.audit.log_cdc_tracking (
        tracking_id         STRING      COMMENT 'Unique tracking record identifier (UUID)',
        pipeline_run_id     STRING      COMMENT 'Links back to log_pipeline_execution',
        table_name          STRING      COMMENT 'Target table that received CDC changes',
        inserts_count       LONG        COMMENT 'New rows inserted',
        updates_count       LONG        COMMENT 'Existing rows updated',
        deletes_count       LONG        COMMENT 'Rows soft/hard deleted',
        unchanged_count     LONG        COMMENT 'Rows evaluated but unchanged',
        run_timestamp       TIMESTAMP   COMMENT 'When the CDC merge was executed (UTC)'
    )
    USING DELTA
    COMMENT 'Managed table tracking Change-Data-Capture statistics'
""")
print("✅ Table created/verified: novamart.audit.log_cdc_tracking")

# 5. Incremental Watermark Tracking
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {CATALOG}.audit.watermark_tracking (
        source_system       STRING      COMMENT 'Origin system name (e.g. olist, sap)',
        table_name          STRING      COMMENT 'Source table name',
        watermark_column    STRING      COMMENT 'Column used as the watermark (e.g. updated_at)',
        last_watermark_value STRING     COMMENT 'Last successfully processed watermark value',
        watermark_type      STRING      COMMENT 'Data type hint: TIMESTAMP | INTEGER | STRING',
        last_updated        TIMESTAMP   COMMENT 'When this watermark was last refreshed (UTC)',
        updated_by          STRING      COMMENT 'Pipeline / notebook that performed the update'
    )
    USING DELTA
    COMMENT 'Managed table tracking watermark indexes for incremental loading'
""")
print("✅ Table created/verified: novamart.audit.watermark_tracking")

# COMMAND ----------

# ============================================================================
# STEP 3 — Verification: Check UC Volume Landing Zone Files
# ============================================================================
# We check if the raw source files are correctly placed in the Unity Catalog
# Volume. This ensures our ingestion pipeline can find them.
# ============================================================================

# COMMAND ----------

VOLUME_PATH = "/Volumes/novabazaar/landing/raw_files"

print("=" * 80)
print(f"🔍 VERIFYING LANDING VOLUME: {VOLUME_PATH}")
print("=" * 80)

try:
    volume_contents = dbutils.fs.ls(VOLUME_PATH)
    print(f"\n📂 Volume Contents ({len(volume_contents)} subdirectories/files):")
    for item in volume_contents:
        print(f"   {'📂' if item.isDir() else '📄'} {item.name}")
except Exception as e:
    print(f"❌ Error accessing volume path: {e}")

# COMMAND ----------

# ============================================================================
# STEP 4 — End-to-End Metastore Schema Verification
# ============================================================================

# COMMAND ----------

print("=" * 80)
print("🔍 VERIFYING SCHEMAS & TABLES")
print("=" * 80)

# Check schemas
print("\n📋 Schemas in catalog 'novabazaar':")
display(spark.sql(f"SHOW SCHEMAS IN {CATALOG}"))

# Check tables in audit schema
print("\n📋 Tables in 'novabazaar.audit':")
display(spark.sql(f"SHOW TABLES IN {CATALOG}.audit"))

print("\n🎉 ENVIRONMENT SETUP COMPLETED SUCCESSFULLY!")

# COMMAND ----------

# ============================================================================
# STEP 5 — Interview Focus: Unity Catalog & Managed Architecture
# ============================================================================
#
# Q1. What is the difference between DBFS and Unity Catalog Volumes?
#     DBFS is legacy mount points pointing to a global S3/ADLS bucket, lacking
#     fine-grained permission controls. Volumes are managed or external directory
#     containers fully integrated with Unity Catalog, allowing securable, Auditable,
#     and managed file assets directly accessible via SQL and standard APIs.
#
# Q2. What is the difference between Managed Tables and External Tables in UC?
#     - Managed tables: Databricks manages the metadata AND the physical data in
#       the catalog's storage root. Deleting the table drops the data AND metadata.
#     - External tables: You manage the S3/ADLS physical path yourself. Deleting the
#       table drops the metadata in UC, but the physical files in S3 are preserved.
#
# Q3. Why use Statement Execution API over DBFS REST API for environment setup?
#     Statement Execution API runs queries directly in Databricks Serverless SQL
#     warehouses, obeying all catalog security constraints, role-based access control,
#     and catalog audit logs. DBFS API lacks standard table ACL integration.
# ============================================================================
