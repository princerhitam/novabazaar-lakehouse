# Databricks notebook source

# COMMAND ----------

# ============================================================================
# NOTEBOOK: 03_bronze_ingestion_framework
# ============================================================================
# Layer        : Bronze (Raw Ingestion)
# Domain       : Core / Ingestion Framework
# Author       : Data Engineering Team
# Role         : Hands-on Learner
# ============================================================================
#
# DESCRIPTION:
#   This is your hands-on coding workbook to build the Metadata-Driven Ingestion 
#   Engine for NovaBazaar.
#
#   Each section contains:
#     - A detailed instruction block explaining the What, Why, and How.
#     - A fully populated, commented code block ready for you to execute.
# ============================================================================

# COMMAND ----------

# MAGIC %md
# MAGIC ### 📦 Step 1: Set Up Imports & Core Paths
# MAGIC *   **What**: We import the necessary Spark SQL functions, datetime modules, and UUID generators. We also set our catalog target and config file paths.
# MAGIC *   **Why**: Spark operations are optimized when using built-in functions. Keeping base paths parameterized prevents hardcoding paths.
# MAGIC *   **How**: Just run this cell to initialize the setup variables.

# COMMAND ----------

import os
import json
import uuid
from datetime import datetime
from pyspark.sql.functions import lit, current_timestamp, input_file_name

CATALOG = "novabazaar"
REPO_PATH = f"/Workspace/Repos/rhitambhaduri7@gmail.com/novabazaar-lakehouse"
CONFIG_FILE_PATH = f"{REPO_PATH}/config/source_config.json"

print(f"✅ Setup complete. Config file path: {CONFIG_FILE_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 📂 Step 2: Load the Configuration File
# MAGIC *   **What**: Load and parse the configuration file (`source_config.json`) using Python's built-in `json` library.
# MAGIC *   **Why**: In an enterprise metadata-driven pipeline, the configuration file tells the engine what to do. If we add a new table tomorrow, we only change the JSON file, not the code.
# MAGIC *   **How**:
# MAGIC     1. Use Python's open context manager: `with open(CONFIG_FILE_PATH, "r") as f:`
# MAGIC     2. Parse it into a dictionary: `config_data = json.load(f)`
# MAGIC     3. Print the number of sources found: `print(len(config_data["sources"]))`
# MAGIC *   **💡 Tip**: Python context managers automatically close the file for you, preventing memory leaks.

# COMMAND ----------

# 1. Open the source config file in read mode
with open(CONFIG_FILE_PATH, "r") as f:
    # 2. Parse the JSON file into a Python dictionary
    config_data = json.load(f)

# 3. Print the count of sources to verify success
sources_count = len(config_data["sources"])
print(f"✅ Successfully loaded configuration. Found {sources_count} source systems.")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 📝 Step 3: Implement the Pipeline Execution Logger
# MAGIC *   **What**: Create a function `log_pipeline_step()` that builds a single-row DataFrame containing run statistics and appends it to the Delta table: `novabazaar.audit.log_pipeline_execution`.
# MAGIC *   **Why**: Observability is a critical production requirement. If a night job fails, operators need to see exactly when it started, when it stopped, what the error was, and how many rows it read/wrote.
# MAGIC *   **How**:
# MAGIC     1. Calculate duration: `duration = (end_time - start_time).total_seconds()`
# MAGIC     2. Build a python dictionary matching the table schema.
# MAGIC     3. Convert the list of dicts to a Spark DataFrame: `log_df = spark.createDataFrame([log_entry])`
# MAGIC     4. Write it to Delta: `log_df.write.format("delta").mode("append").saveAsTable("novabazaar.audit.log_pipeline_execution")`
# MAGIC *   **💡 Tip**: PySpark's `createDataFrame()` expects a list of dictionaries. Ensure your numeric types (like counts) are cast to `int` and strings to `str` to avoid schema mismatches in Delta.

# COMMAND ----------

def log_pipeline_step(pipeline_run_id, step_name, step_sequence, log_level, message, 
                      records_read=0, records_written=0, records_rejected=0, 
                      start_time=None, end_time=None, status="SUCCESS", error_message=""):
    
    # 1. Fallback to current time if start/end times aren't provided
    start_ts = start_time if start_time else datetime.utcnow()
    end_ts = end_time if end_time else datetime.utcnow()
    
    # 2. Calculate duration in seconds
    duration = (end_ts - start_ts).total_seconds()
    
    # 3. Create a single log entry dictionary matching the table schema
    log_entry = {
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
    }
    
    # 4. Convert the dictionary list into a PySpark DataFrame
    log_df = spark.createDataFrame([log_entry])
    
    # 5. Append the DataFrame row directly to the Delta audit table
    log_df.write.format("delta").mode("append").saveAsTable(f"{CATALOG}.audit.log_pipeline_execution")
    
print("✅ log_pipeline_step function registered successfully.")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 🚀 Step 4: Build the Core Ingestion Engine
# MAGIC *   **What**: Define a function `ingest_source(source_id, run_id)` that looks up the configuration for `source_id`, reads the raw file using Spark, appends conformed audit columns, and writes it as an append-only Delta table.
# MAGIC *   **Why**: Enforces absolute consistency. Every table gets the identical load options, lineage columns, and audit logs without writing duplicate scripts.
# MAGIC *   **How**:
# MAGIC     1. Filter config_data: `src = next(s for s in config_data["sources"] if s["source_id"] == source_id)`
# MAGIC     2. Set up reader: `reader = spark.read.format(src["file_format"])`
# MAGIC     3. If CSV, add separator/header options: `.option("sep", src.get("delimiter", ",")).option("header", "true").option("inferSchema", "true")`
# MAGIC     4. Load raw DataFrame: `df_raw = reader.load(src["file_path"])`
# MAGIC     5. Add audit columns:
# MAGIC        - `_source_system`: `lit(source_id)`
# MAGIC        - `_ingestion_timestamp`: `current_timestamp()`
# MAGIC        - `_batch_id`: `lit(run_id)`
# MAGIC        - `_file_name`: `df_raw["_metadata.file_path"]`
# MAGIC     6. Save as Delta: `df_bronze.write.format("delta").mode("append").saveAsTable(f"{src['bronze_database']}.{src['bronze_table']}")`
# MAGIC *   **💡 Tip**: In Unity Catalog, use `_metadata.file_path` to capture the file path. The legacy `input_file_name()` function is blocked by Unity Catalog security and will crash!

# COMMAND ----------

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
            .withColumn("_file_name", df_raw["_metadata.file_path"])
            
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
        print(f"   ✅ Ingestion successful. Written {records_written} records to {target_table_name}")
        
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
        print(f"   ❌ Ingestion failed for {source_id}: {err_msg}")
        raise e

# COMMAND ----------

# MAGIC %md
# MAGIC ### 🧪 Step 5: Test Your Ingestion Engine
# MAGIC *   **What**: Generate a test UUID run ID and execute the `ingest_source()` function specifically for the `olist_sellers` dataset.
# MAGIC *   **Why**: We always run a validation tests on a single table first before running a full loop, to isolate errors quickly.
# MAGIC *   **How**:
# MAGIC     1. Create a run ID: `test_run_id = str(uuid.uuid4())`
# MAGIC     2. Call: `ingest_source("olist_sellers", test_run_id)`
# MAGIC *   **💡 Tip**: Verify in the console output that it prints "Ingestion successful" and prints the record count.

# COMMAND ----------

test_run_id = str(uuid.uuid4())
print(f"🔑 Test Ingestion Run ID: {test_run_id}")

ingest_source("olist_sellers", test_run_id)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 🔄 Step 6: Ingest All Active Sources (The Batch Loop)
# MAGIC *   **What**: Write a loop that iterates through your config data list, checks if the source is active (`is_active` == true), and calls `ingest_source()` for each.
# MAGIC *   **Why**: Automates the entire Bronze landing zone load in one single process.
# MAGIC *   **How**:
# MAGIC     1. Generate a new run ID for this batch.
# MAGIC     2. Loop: `for src in config_data["sources"]:`
# MAGIC     3. If `src.get("is_active", True)` is true, call `ingest_source(src["source_id"], batch_run_id)`.
# MAGIC *   **💡 Tip**: Keep track of successful and failed source IDs in separate lists so you can print a final Batch Summary Report!

# COMMAND ----------

batch_run_id = str(uuid.uuid4())
print(f"🔑 Production Ingestion Batch Run ID: {batch_run_id}")

success_sources = []
failed_sources = []

for src in config_data["sources"]:
    src_id = src["source_id"]
    if src.get("is_active", True) and src_id != "olist_sellers": # Skip sellers as we already tested it
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

# MAGIC %md
# MAGIC ### 🔍 Step 7: Verify via SQL
# MAGIC *   **What**: Run SQL queries on your newly ingested tables to verify they exist and contain columns.
# MAGIC *   **Why**: Visual confirmation checks prove that the data metastores are structurally sound.
# MAGIC *   **How**:
# MAGIC     1. Run a query on `novabazaar.audit.log_pipeline_execution` to see your runs.
# MAGIC     2. Run a query on `novabazaar.bronze.olist_sellers` to verify records.

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
