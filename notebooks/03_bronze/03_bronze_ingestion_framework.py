# Databricks notebook source

# COMMAND ----------

# ============================================================================
# NOTEBOOK: 03_bronze_ingestion_framework (WORKBOOK EDITION)
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
#     - A blank coding block for you to write the code.
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

# TODO: Write your code below to load and print the config contents
# 1. Open the file
# 2. Parse the JSON
# 3. Print a confirmation statement

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

# TODO: Define your log_pipeline_step function below
# Parameters: pipeline_run_id, step_name, step_sequence, log_level, message, 
#             records_read=0, records_written=0, start_time=None, end_time=None, 
#             status="SUCCESS", error_message=""

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
# MAGIC        - `_file_name`: `input_file_name()`
# MAGIC     6. Save as Delta: `df_bronze.write.format("delta").mode("append").saveAsTable(f"{src['bronze_database']}.{src['bronze_table']}")`
# MAGIC *   **💡 Tip**: Use `input_file_name()` from PySpark functions to capture the actual file path. This is vital for verifying data lineage!

# COMMAND ----------

# TODO: Implement the ingest_source(source_id, run_id) function below
# Ensure you wrap the read and write logic in a try-except block so that you can
# log SUCCESS or FAILED steps in your log_pipeline_execution table!

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

# TODO: Generate a test run ID and call ingest_source for "olist_sellers"

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

# TODO: Implement the batch ingestion loop and print a final run summary report.

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
# MAGIC -- Write a SQL query below to select and view the newest pipeline execution logs
# MAGIC -- TODO: SELECT * FROM ...

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Write a SQL query below to sample the first 5 rows of the bronze sellers table
# MAGIC -- TODO: SELECT * FROM ...
