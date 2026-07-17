# Databricks notebook source

# COMMAND ----------

# ============================================================================
# NOTEBOOK: 03_bronze_ingestion_framework
# ============================================================================
# Layer        : Bronze (Raw Ingestion)
# Domain       : Core / Ingestion Framework
# Author       : Data Engineering Team
# Created Date : 2026-07-17
# Last Modified: 2026-07-17
# ============================================================================
#
# DESCRIPTION:
#   This is the core Metadata-Driven Ingestion Engine for NovaBazaar.
#   It dynamically reads configurations from `config/source_config.json`
#   and loads raw files from the landing volume into Bronze Delta tables.
#
# BUSINESS CONTEXT:
#   Ingestion is the entry point of the Lakehouse. Hardcoding individual scripts
#   for each source is an anti-pattern. This generic framework handles all formats,
#   adds audit logging, registers Delta tables, and enables metadata configuration.
#
# DEPENDENCIES:
#   • Schemas and audit tables created in 00_environment_setup
#   • Raw files staged in /Volumes/novabazaar/landing/raw_files
# ============================================================================

# COMMAND ----------

# ============================================================================
# STEP 1 — Imports & Parameters
# ============================================================================
import os
import json
import uuid
from datetime import datetime
from pyspark.sql.functions import lit, current_timestamp, input_file_name

# Define base paths
CATALOG = "novabazaar"
REPO_PATH = f"/Workspace/Repos/rhitambhaduri7@gmail.com/novabazaar-lakehouse"
CONFIG_FILE_PATH = f"{REPO_PATH}/config/source_config.json"

print(f"✅ Config file target: {CONFIG_FILE_PATH}")

# COMMAND ----------

# ============================================================================
# STEP 2 — Load Configuration Metadata
# ============================================================================
# We load the source_config.json file to retrieve metadata configs dynamically.
# ============================================================================

try:
    with open(CONFIG_FILE_PATH, "r") as f:
        config_data = json.load(f)
    print(f"✅ Successfully loaded config file. Found {len(config_data['sources'])} sources.")
except Exception as e:
    print(f"❌ Error loading config file: {e}")
    raise e

# COMMAND ----------

# ============================================================================
# STEP 3 — Ingestion Auditing Logger
# ============================================================================
# Helper function to log run metadata into novabazaar.audit.log_pipeline_execution
# ============================================================================

def log_pipeline_step(pipeline_run_id, step_name, step_sequence, log_level, message, 
                      records_read=0, records_written=0, records_rejected=0, 
                      start_time=None, end_time=None, status="SUCCESS", error_message=""):
    
    start_ts = start_time if start_time else datetime.utcnow()
    end_ts = end_time if end_time else datetime.utcnow()
    duration = (end_ts - start_ts).total_seconds()
    
    # Create single row DataFrame to append
    log_df = spark.createDataFrame([{
        "log_id": str(uuid.uuid4()),
        "pipeline_name": "bronze_ingestion_framework",
        "pipeline_run_id": pipeline_run_id,
        "step_name": step_name,
        "step_sequence": int(step_sequence),
        "log_level": log_level,
        "message": message,
        "records_read": int(records_read),
        "records_written": int(records_written),
        "records_rejected": int(records_rejected),
        "start_timestamp": start_ts,
        "end_timestamp": end_ts,
        "duration_seconds": float(duration),
        "status": status,
        "error_message": error_message,
        "notebook_path": dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get(),
        "created_timestamp": datetime.utcnow()
    }])
    
    # Write to managed Delta audit table
    log_df.write.format("delta").mode("append").saveAsTable(f"{CATALOG}.audit.log_pipeline_execution")

# COMMAND ----------

# ============================================================================
# STEP 4 — Core Ingestion Engine Function
# ============================================================================
# This function dynamically configures the reader, reads raw files, appends
# audit metadata columns, and writes conformed Delta tables.
# ============================================================================

def ingest_source(source_id, run_id):
    start_time = datetime.utcnow()
    
    # Find configuration for target source_id
    src_config = next((s for s in config_data["sources"] if s["source_id"] == source_id), None)
    
    if not src_config:
        raise ValueError(f"❌ Source ID '{source_id}' not found in configuration.")
        
    if not src_config.get("is_active", True):
        print(f"⏭️ Skipping inactive source: {source_id}")
        return
        
    print(f"\n🚀 Ingesting: {source_id} ({src_config['source_name']})")
    
    # Extract metadata properties
    file_format = src_config["file_format"]
    file_path = src_config["file_path"]
    bronze_db = src_config["bronze_database"]
    bronze_table = src_config["bronze_table"]
    
    target_table_name = f"{bronze_db}.{bronze_table}"
    
    try:
        # 1. Dynamically configure PySpark Reader
        reader = spark.read.format(file_format)
        
        if file_format == "csv":
            delimiter = src_config.get("delimiter", ",")
            header = str(src_config.get("header", "true")).lower()
            reader = reader.option("sep", delimiter).option("header", header).option("inferSchema", "true")
            
        # 2. Read raw files
        df_raw = reader.load(file_path)
        records_read = df_raw.count()
        
        # 3. Append Audit Metadata Columns (Lineage)
        df_bronze = df_raw \
            .withColumn("_source_system", lit(source_id)) \
            .withColumn("_ingestion_timestamp", current_timestamp()) \
            .withColumn("_batch_id", lit(run_id)) \
            .withColumn("_file_name", input_file_name())
            
        # 4. Write to managed Delta Bronze table (Append-only)
        df_bronze.write.format("delta").mode("append").saveAsTable(target_table_name)
        records_written = df_bronze.count()
        
        end_time = datetime.utcnow()
        
        # 5. Log success step
        log_pipeline_step(
            pipeline_run_id=run_id,
            step_name=f"ingest_{source_id}",
            step_sequence=1,
            log_level="INFO",
            message=f"Successfully ingested {source_id} to Bronze table: {target_table_name}",
            records_read=records_read,
            records_written=records_written,
            start_time=start_time,
            end_time=end_time,
            status="SUCCESS"
        )
        print(f"✅ Ingestion successful. Written {records_written} records to {target_table_name}")
        
    except Exception as e:
        end_time = datetime.utcnow()
        err_msg = str(e)
        
        # Log failure step
        log_pipeline_step(
            pipeline_run_id=run_id,
            step_name=f"ingest_{source_id}",
            step_sequence=1,
            log_level="ERROR",
            message=f"Failed to ingest {source_id} to Bronze table",
            start_time=start_time,
            end_time=end_time,
            status="FAILED",
            error_message=err_msg
        )
        print(f"❌ Ingestion failed for {source_id}: {err_msg}")
        raise e

# COMMAND ----------

# ============================================================================
# STEP 5 — Single Table Verification Run
# ============================================================================
# Let's test a single small table to make sure the framework compiles.
# ============================================================================

test_run_id = str(uuid.uuid4())
print(f"🔑 Test Ingestion Run ID: {test_run_id}")

# Run Olist Sellers table
ingest_source("olist_sellers", test_run_id)

# COMMAND ----------

# ============================================================================
# STEP 6 — Loop over All Active Sources
# ============================================================================
# Loop and ingest all active data sources defined in metadata config.
# ============================================================================

batch_run_id = str(uuid.uuid4())
print(f"🔑 Production Ingestion Batch Run ID: {batch_run_id}")

success_sources = []
failed_sources = []

for src in config_data["sources"]:
    src_id = src["source_id"]
    if src.get("is_active", True) and src_id != "olist_sellers": # Skip sellers as we tested it
        try:
            ingest_source(src_id, batch_run_id)
            success_sources.append(src_id)
        except Exception as e:
            failed_sources.append(src_id)

print("\n" + "=" * 50)
print("🏁 BATCH RUN SUMMARY")
print("=" * 50)
print(f"   Success ({len(success_sources) + 1}): ['olist_sellers'] + {success_sources}")
print(f"   Failures ({len(failed_sources)}): {failed_sources}")
print("=" * 50)

# COMMAND ----------

# ============================================================================
# STEP 7 — Verification Queries
# ============================================================================

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Verify execution logs
# MAGIC SELECT pipeline_run_id, step_name, records_read, records_written, status, duration_seconds 
# MAGIC FROM novabazaar.audit.log_pipeline_execution
# MAGIC ORDER BY start_timestamp DESC;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Sample query from bronze sellers
# MAGIC SELECT * FROM novabazaar.bronze.olist_sellers LIMIT 5;

# COMMAND ----------

# ============================================================================
# STEP 8 — Hands-on Interview Prep & Exercises
# ============================================================================
#
# Q1. What is the benefit of adding metadata columns like _file_name in Bronze?
#     It guarantees full data lineage and auditability. If a row is corrupted or
#     duplicated, we can trace it back to the exact source file and batch ID.
#
# Q2. Why use Delta Lake format instead of standard CSV/JSON for Bronze?
#     Delta Lake provides ACID transactions (preventing partial writes on errors),
#     optimized performance (compaction, indexing), and is fully queryable via standard SQL.
#
# Q3. Why use a single dynamic notebook instead of multiple scripts?
#     Reduces maintenance overhead, enforces identical logging/lineage standards,
#     and allows onboarding a new table simply by modifying source_config.json.
# ============================================================================
