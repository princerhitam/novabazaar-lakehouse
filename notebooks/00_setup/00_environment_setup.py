# Databricks notebook source

# COMMAND ----------

# ============================================================================
# NOTEBOOK: 00_environment_setup
# ============================================================================
# Layer        : Setup
# Domain       : Infrastructure
# Author       : Data Engineering Team
# Created Date : 2026-07-16
# Last Modified: 2026-07-16
# ============================================================================
#
# DESCRIPTION:
#   This notebook provisions the complete NovaBazaar Lakehouse environment
#   from scratch.  It is designed to be idempotent – every operation uses
#   "IF NOT EXISTS" semantics so the notebook can be re-run safely without
#   side effects.
#
#   Steps performed:
#     1. Create the full DBFS folder hierarchy (landing → gold + audit/config)
#     2. Create medallion-layer Hive metastore databases
#     3. Provision audit / operational Delta tables
#     4. Verify the environment end-to-end
#
# BUSINESS CONTEXT:
#   Environment setup is the foundation of any production data platform.
#   Without a well-defined, repeatable provisioning process:
#     • Teams create ad-hoc paths, leading to data scattered across DBFS.
#     • Table ownership and lineage become untraceable.
#     • Disaster-recovery takes longer because the "known-good state" is
#       undocumented.
#     • Audit & compliance requirements (SOX, GDPR) cannot be met when
#       pipeline metadata is missing.
#
#   By codifying setup in a versioned notebook we get:
#     ✓ Reproducibility  – any team member can stand up the environment.
#     ✓ Auditability     – change-log is tracked via Git.
#     ✓ Idempotency      – safe to re-run after partial failures.
#     ✓ Documentation    – the notebook *is* the living specification.
#
# DEPENDENCIES:
#   • Databricks Runtime 13.x+ (Community Edition compatible)
#   • dbutils (pre-installed on Databricks)
#   • Delta Lake (bundled with Databricks Runtime)
#
# CHANGE LOG:
#   2026-07-16 | Data Engineering Team | Initial creation – Milestone 1
# ============================================================================

# COMMAND ----------

# ============================================================================
# STEP 1 — DBFS Folder Structure (Configuration)
# ============================================================================
# We define every path in data structures first, then loop to create them.
# This makes the notebook easy to extend when new sources arrive.
# ============================================================================

BASE_PATH = "/FileStore/novabazaar"

# ---- Landing Zone (15 raw-data sources) -----------------------------------
landing_sources = [
    "olist_orders",
    "olist_order_items",
    "olist_order_payments",
    "olist_order_reviews",
    "olist_customers",
    "olist_products",
    "olist_sellers",
    "olist_geolocation",
    "product_category_translation",
    "employees",
    "general_ledger",
    "inventory_snapshots",
    "marketing_campaigns",
    "promotions",
    "exchange_rates",
]

landing_folders = [
    f"{BASE_PATH}/landing/{src}/" for src in landing_sources
]

# ---- Bronze Layer (organised by domain) -----------------------------------
bronze_folders = [
    f"{BASE_PATH}/bronze/sales/olist_orders",
    f"{BASE_PATH}/bronze/sales/olist_order_items",
    f"{BASE_PATH}/bronze/sales/olist_order_payments",
    f"{BASE_PATH}/bronze/customer/olist_customers",
    f"{BASE_PATH}/bronze/customer/olist_order_reviews",
    f"{BASE_PATH}/bronze/product/olist_products",
    f"{BASE_PATH}/bronze/product/product_category_translation",
    f"{BASE_PATH}/bronze/seller/olist_sellers",
    f"{BASE_PATH}/bronze/reference/olist_geolocation",
    f"{BASE_PATH}/bronze/hr/employees",
    f"{BASE_PATH}/bronze/finance/general_ledger",
    f"{BASE_PATH}/bronze/finance/exchange_rates",
    f"{BASE_PATH}/bronze/inventory/inventory_snapshots",
    f"{BASE_PATH}/bronze/marketing/marketing_campaigns",
    f"{BASE_PATH}/bronze/marketing/promotions",
    f"{BASE_PATH}/bronze/_quarantine/",
]

# ---- Silver Layer ---------------------------------------------------------
silver_folders = [
    f"{BASE_PATH}/silver/sales/transactions",
    f"{BASE_PATH}/silver/sales/order_items",
    f"{BASE_PATH}/silver/sales/payments",
    f"{BASE_PATH}/silver/customer/customers",
    f"{BASE_PATH}/silver/customer/reviews",
    f"{BASE_PATH}/silver/product/products",
    f"{BASE_PATH}/silver/product/categories",
    f"{BASE_PATH}/silver/seller/sellers",
    f"{BASE_PATH}/silver/reference/geolocation",
    f"{BASE_PATH}/silver/hr/employees",
    f"{BASE_PATH}/silver/finance/gl_entries",
    f"{BASE_PATH}/silver/finance/exchange_rates",
    f"{BASE_PATH}/silver/inventory/stock_levels",
    f"{BASE_PATH}/silver/marketing/campaigns",
    f"{BASE_PATH}/silver/marketing/promotions",
    f"{BASE_PATH}/silver/_quarantine/",
]

# ---- Gold Layer -----------------------------------------------------------
gold_folders = [
    # Dimensions
    f"{BASE_PATH}/gold/dimensions/dim_date",
    f"{BASE_PATH}/gold/dimensions/dim_customer",
    f"{BASE_PATH}/gold/dimensions/dim_product",
    f"{BASE_PATH}/gold/dimensions/dim_seller",
    f"{BASE_PATH}/gold/dimensions/dim_geography",
    f"{BASE_PATH}/gold/dimensions/dim_category",
    f"{BASE_PATH}/gold/dimensions/dim_employee",
    f"{BASE_PATH}/gold/dimensions/dim_payment_method",
    f"{BASE_PATH}/gold/dimensions/dim_promotion",
    f"{BASE_PATH}/gold/dimensions/dim_channel",
    # Facts
    f"{BASE_PATH}/gold/facts/fact_sales",
    f"{BASE_PATH}/gold/facts/fact_daily_sales_agg",
    f"{BASE_PATH}/gold/facts/fact_customer_activity",
    f"{BASE_PATH}/gold/facts/fact_inventory_snapshot",
    f"{BASE_PATH}/gold/facts/fact_review_analysis",
    f"{BASE_PATH}/gold/facts/fact_financial_transaction",
    # Analytics
    f"{BASE_PATH}/gold/analytics/customer_360",
    f"{BASE_PATH}/gold/analytics/customer_rfm",
    f"{BASE_PATH}/gold/analytics/seller_performance",
    # KPI
    f"{BASE_PATH}/gold/kpi/daily_kpi_summary",
    f"{BASE_PATH}/gold/kpi/monthly_kpi_summary",
]

# ---- Config / Audit / Reference ------------------------------------------
operational_folders = [
    f"{BASE_PATH}/config/",
    f"{BASE_PATH}/audit/pipeline_log",
    f"{BASE_PATH}/audit/dq_results",
    f"{BASE_PATH}/audit/reconciliation_log",
    f"{BASE_PATH}/audit/cdc_tracking",
    f"{BASE_PATH}/audit/watermark_tracking",
    f"{BASE_PATH}/reference/",
]

# Combine all folder lists
ALL_FOLDERS = (
    landing_folders
    + bronze_folders
    + silver_folders
    + gold_folders
    + operational_folders
)

print(f"📂 Total folders to create: {len(ALL_FOLDERS)}")

# COMMAND ----------

# ============================================================================
# STEP 1 (cont.) — Create every DBFS folder
# ============================================================================

created_count = 0
for folder_path in ALL_FOLDERS:
    dbutils.fs.mkdirs(folder_path)
    created_count += 1

print("=" * 70)
print(f"✅ DBFS Folder Structure Created Successfully!")
print(f"   Total folders provisioned : {created_count}")
print(f"   Landing zone sources      : {len(landing_folders)}")
print(f"   Bronze layer folders      : {len(bronze_folders)}")
print(f"   Silver layer folders      : {len(silver_folders)}")
print(f"   Gold layer folders        : {len(gold_folders)}")
print(f"   Operational folders       : {len(operational_folders)}")
print("=" * 70)

# COMMAND ----------

# ============================================================================
# STEP 2 — Create Databases (Hive Metastore)
# ============================================================================
# One database per medallion layer keeps ownership clear and simplifies
# access-control (GRANT / REVOKE at the database level).
# ============================================================================

databases = [
    ("novabazaar_bronze", "Raw ingested data — append-only, schema-on-read"),
    ("novabazaar_silver", "Cleansed, conformed, business-entity tables"),
    ("novabazaar_gold", "Star-schema dimensions, facts, aggregates & KPIs"),
    ("novabazaar_audit", "Pipeline execution logs, DQ results, reconciliation"),
    ("novabazaar_config", "Pipeline configuration and reference metadata"),
]

for db_name, comment in databases:
    spark.sql(f"""
        CREATE DATABASE IF NOT EXISTS {db_name}
        COMMENT '{comment}'
    """)
    print(f"✅ Database created (or already exists): {db_name}")

print("\n📋 Current databases in the metastore:")
display(spark.sql("SHOW DATABASES"))

# COMMAND ----------

# ============================================================================
# STEP 3 — Audit Table 1: log_pipeline_execution
# ============================================================================
# Captures every step of every pipeline run.  This is the single source of
# truth for debugging failures and measuring SLA adherence.
# ============================================================================

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS novabazaar_audit.log_pipeline_execution (
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
    LOCATION '{BASE_PATH}/audit/pipeline_log'
    COMMENT 'Append-only log of every pipeline step execution'
""")

print("✅ Table created: novabazaar_audit.log_pipeline_execution")

# COMMAND ----------

# ============================================================================
# STEP 3 — Audit Table 2: log_dq_results
# ============================================================================
# Stores the outcome of every data-quality rule execution so we can trend
# quality scores over time and trigger alerts on degradation.
# ============================================================================

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS novabazaar_audit.log_dq_results (
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
    LOCATION '{BASE_PATH}/audit/dq_results'
    COMMENT 'Data-quality rule execution results'
""")

print("✅ Table created: novabazaar_audit.log_dq_results")

# COMMAND ----------

# ============================================================================
# STEP 3 — Audit Table 3: log_reconciliation
# ============================================================================
# Source-to-target reconciliation proves data completeness after each
# pipeline run.  Required for SOX / financial audit evidence.
# ============================================================================

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS novabazaar_audit.log_reconciliation (
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
    LOCATION '{BASE_PATH}/audit/reconciliation_log'
    COMMENT 'Source-to-target reconciliation results'
""")

print("✅ Table created: novabazaar_audit.log_reconciliation")

# COMMAND ----------

# ============================================================================
# STEP 3 — Audit Table 4: log_cdc_tracking
# ============================================================================
# Tracks Change-Data-Capture statistics per table per run so we can
# monitor mutation patterns and detect anomalies (e.g. unexpected deletes).
# ============================================================================

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS novabazaar_audit.log_cdc_tracking (
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
    LOCATION '{BASE_PATH}/audit/cdc_tracking'
    COMMENT 'CDC merge statistics per table per run'
""")

print("✅ Table created: novabazaar_audit.log_cdc_tracking")

# COMMAND ----------

# ============================================================================
# STEP 3 — Audit Table 5: watermark_tracking
# ============================================================================
# High-water-mark table for incremental ingestion.  Each source table has
# a row that records the last successfully processed value (timestamp,
# ID, offset) so subsequent runs only pull new / changed data.
# ============================================================================

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS novabazaar_audit.watermark_tracking (
        source_system       STRING      COMMENT 'Origin system name (e.g. olist, sap)',
        table_name          STRING      COMMENT 'Source table name',
        watermark_column    STRING      COMMENT 'Column used as the watermark (e.g. updated_at)',
        last_watermark_value STRING     COMMENT 'Last successfully processed watermark value',
        watermark_type      STRING      COMMENT 'Data type hint: TIMESTAMP | INTEGER | STRING',
        last_updated        TIMESTAMP   COMMENT 'When this watermark was last refreshed (UTC)',
        updated_by          STRING      COMMENT 'Pipeline / notebook that performed the update'
    )
    USING DELTA
    LOCATION '{BASE_PATH}/audit/watermark_tracking'
    COMMENT 'Incremental ingestion high-water-mark tracking'
""")

print("✅ Table created: novabazaar_audit.watermark_tracking")

# COMMAND ----------

# ============================================================================
# STEP 4 — End-to-End Verification
# ============================================================================

print("=" * 70)
print("🔍 VERIFICATION — DBFS Folder Structure")
print("=" * 70)

for layer in ["landing", "bronze", "silver", "gold", "config", "audit", "reference"]:
    try:
        contents = dbutils.fs.ls(f"{BASE_PATH}/{layer}/")
        print(f"\n📁 {layer.upper()} ({len(contents)} items):")
        for item in contents:
            print(f"   {'📂' if item.isDir() else '📄'} {item.name}")
    except Exception as e:
        print(f"\n⚠️  {layer.upper()}: {e}")

print("\n" + "=" * 70)
print("🔍 VERIFICATION — Databases")
print("=" * 70)
db_df = spark.sql("SHOW DATABASES LIKE 'novabazaar_*'")
display(db_df)

print("\n" + "=" * 70)
print("🔍 VERIFICATION — Audit Tables")
print("=" * 70)

audit_tables = [
    "novabazaar_audit.log_pipeline_execution",
    "novabazaar_audit.log_dq_results",
    "novabazaar_audit.log_reconciliation",
    "novabazaar_audit.log_cdc_tracking",
    "novabazaar_audit.watermark_tracking",
]

for table in audit_tables:
    try:
        cols = spark.sql(f"DESCRIBE TABLE {table}").count()
        print(f"   ✅ {table} — {cols} columns")
    except Exception as e:
        print(f"   ❌ {table} — {e}")

print("\n" + "=" * 70)
print("🎉  ENVIRONMENT SETUP COMPLETE — NovaBazaar Lakehouse")
print("=" * 70)
print(f"""
   DBFS folders created       : {len(ALL_FOLDERS)}
   Databases created          : {len(databases)}
   Audit tables provisioned   : {len(audit_tables)}

   All resources are idempotent — this notebook can be re-run at any time.
""")

# COMMAND ----------

# ============================================================================
# STEP 5 — Interview Questions & Exercises
# ============================================================================
#
# ---------------------------------------------------------------------------
# 📝 INTERVIEW QUESTIONS
# ---------------------------------------------------------------------------
#
# Q1. What is DBFS (Databricks File System)?
#     DBFS is an abstraction layer on top of scalable object storage
#     (e.g. AWS S3, Azure ADLS Gen2, GCS).  It provides a familiar
#     POSIX-like file-system interface (/FileStore/…) that lets notebooks
#     and jobs read/write data without managing cloud-specific SDKs.
#     Key points:
#       - /FileStore/ is accessible via the Databricks web UI.
#       - DBFS paths map to cloud storage under the hood.
#       - dbutils.fs provides programmatic access (ls, cp, mv, mkdirs, rm).
#
# Q2. What is the difference between Managed and External tables in
#     Databricks?
#     • Managed table: Databricks controls BOTH the metadata (Hive
#       metastore) AND the data files.  Dropping the table deletes the
#       data.
#     • External table: Databricks manages metadata only; data lives at
#       a user-specified LOCATION.  Dropping the table removes metadata
#       but the data files remain.  In production, external tables are
#       preferred because they decouple storage lifecycle from metastore
#       operations — critical for disaster recovery and multi-tool access.
#
# Q3. Why do we create separate databases for each medallion layer?
#     Separation provides:
#       a) Access control — GRANT SELECT on novabazaar_gold to analysts
#          without exposing raw bronze data.
#       b) Namespace clarity — table names stay short and unambiguous.
#       c) Lifecycle management — bronze tables may have different
#          retention / vacuum policies than gold.
#       d) Lineage — it is immediately clear which layer a table belongs
#          to from its fully qualified name.
#
# Q4. What is Delta Lake and how does it differ from plain Parquet?
#     Delta Lake is an open-source storage layer that adds ACID
#     transactions, schema enforcement, time-travel (versioning), and
#     efficient upserts (MERGE) on top of Parquet.
#     Key differences:
#       - Parquet is a columnar file format; Delta adds a transaction log
#         (_delta_log/) that tracks every change.
#       - Delta supports UPDATE, DELETE, MERGE — Parquet is append-only.
#       - Delta enables time-travel queries (SELECT … VERSION AS OF / 
#         TIMESTAMP AS OF).
#       - Delta integrates with Spark's structured streaming for exactly-
#         once processing.
#
# Q5. Explain the purpose of audit tables in a production data platform.
#     Audit tables provide:
#       a) Observability — pipeline_execution logs let on-call engineers
#          pinpoint which step failed and how many records were affected.
#       b) Data quality tracking — dq_results trends reveal gradual
#          source degradation before it causes downstream errors.
#       c) Compliance evidence — reconciliation logs prove that data
#          was transferred completely (SOX, GDPR Article 5 accuracy).
#       d) Incremental processing — watermark_tracking enables efficient
#          "process only what's new" patterns instead of full reloads.
#       e) Change auditing — cdc_tracking records mutation volumes so
#          anomalies (e.g. mass deletes) can be detected automatically.
#
# ---------------------------------------------------------------------------
# 📚 HOMEWORK EXERCISES
# ---------------------------------------------------------------------------
#
# Exercise 1: Add a new landing source
#   A new data source called "website_clickstream" needs to be ingested.
#   - Add its landing folder.
#   - Add a bronze folder under a suitable domain.
#   - Add a silver folder with a cleansed table name.
#   - Re-run the notebook and verify the new folders appear.
#
# Exercise 2: Create a config table
#   Create a Delta table novabazaar_config.pipeline_parameters with
#   columns: pipeline_name STRING, parameter_name STRING,
#   parameter_value STRING, is_active BOOLEAN, updated_timestamp TIMESTAMP.
#   Store it at /FileStore/novabazaar/config/pipeline_parameters.
#   Insert 3 sample rows using spark.sql("INSERT INTO …").
#
# Exercise 3: Write a helper function
#   Write a reusable Python function `log_pipeline_step(...)` that inserts
#   a row into novabazaar_audit.log_pipeline_execution.  It should:
#     - Auto-generate log_id using uuid.uuid4().
#     - Auto-set created_timestamp to current_timestamp().
#     - Accept all other fields as parameters with sensible defaults.
#   Test it by calling the function and then querying the table.
#
# ---------------------------------------------------------------------------
# 🚀 STRETCH GOALS
# ---------------------------------------------------------------------------
#
# Stretch 1: Implement table-level access controls
#   Use Databricks SQL to GRANT SELECT on novabazaar_gold to a group
#   called "analysts" and DENY access to novabazaar_bronze for the same
#   group.  Document the commands even if you cannot run them on Community
#   Edition (it requires Unity Catalog or Table ACLs to be enabled).
#
# Stretch 2: Build an automated environment health-check notebook
#   Create a separate notebook (00_health_check) that:
#     - Verifies all DBFS folders exist (re-creates missing ones).
#     - Verifies all databases and tables exist.
#     - Checks that audit tables are not empty (warns if no data after
#       pipelines should have run).
#     - Outputs a single PASS / FAIL status with details.
#   Schedule it to run daily via Databricks Jobs (or document how to).
#
# ============================================================================

print("📝 Interview questions and exercises are in the comments above.")
print("   Scroll up or view the raw notebook source to read them.")
