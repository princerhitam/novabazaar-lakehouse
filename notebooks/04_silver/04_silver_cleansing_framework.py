# Databricks notebook source

# COMMAND ----------

# ============================================================================
# NOTEBOOK: 04_silver_cleansing_framework (STUDENT WORKBOOK)
# ============================================================================
# Layer        : Silver (Cleansing & Conforming)
# Domain       : Core / transformations
# Author       : Data Engineering Team
# Role         : Hands-on Learner
# ============================================================================
#
# DESCRIPTION:
#   This is your hands-on coding workbook to build the Silver Cleansing
#   and Data Quality Gateway for NovaBazaar.
#
#   You will learn:
#     - How to cast column data types in PySpark
#     - How to parse string dates into Timestamps
#     - How to filter out invalid rows and route them to a Quarantine zone
#     - How to write clean tables to novabazaar.silver
# ============================================================================

# COMMAND ----------

# MAGIC %md
# MAGIC ### 📦 Step 1: Imports & Base Paths Setup
# MAGIC *   **What**: We import the necessary Spark SQL functions (`col`, `to_date`, `to_timestamp`, `when`, `lit`) and set target catalog/database names.
# MAGIC *   **Why**: These functions run optimized C++ code in Spark's Tungsten execution engine.
# MAGIC *   **How**: Run this setup cell to load your dependencies.

# COMMAND ----------

# TODO: Write imports and base path definitions
# Hint: You need to import: col, lit, when, to_date, to_timestamp, current_timestamp from pyspark.sql.functions

# COMMAND ----------

# MAGIC %md
# MAGIC ### 🔍 Step 2: Read Bronze Data & Define Schema Casting
# MAGIC *   **What**: Read the raw `novabazaar.bronze.olist_sellers` table and cast its columns to the correct types.
# MAGIC *   **Why**: Bronze columns are often auto-inferred as strings. Silver requires strict data types (e.g. integer zip codes, cleaned text) for analytics.
# MAGIC *   **How**:
# MAGIC     1. Read the table: `df = spark.read.table("novabazaar.bronze.olist_sellers")`
# MAGIC     2. Select and cast columns using `.select(col("column_name").cast("type"))`.
# MAGIC *   **💡 Tip**: In PySpark, `col("seller_zip_code_prefix").cast("int")` cleanses zip codes by converting them to clean integers.

# COMMAND ----------

# TODO: Read from novabazaar.bronze.olist_sellers, cast columns:
# - seller_id: string
# - seller_zip_code_prefix: integer
# - seller_city: string
# - seller_state: string
# Display the schema of the casted DataFrame.

# COMMAND ----------

# MAGIC %md
# MAGIC ### 🛡️ Step 3: Implement Data Quality Gateway (Quarantine Routing)
# MAGIC *   **What**: Validate that the seller records are correct. If a row has a null `seller_id` or an invalid zip code (e.g. negative or null), route it to a quarantine table. Otherwise, keep it.
# MAGIC *   **Why**: We must prevent bad data from polluting downstream dashboards, but we must not delete it (so developers can audit why the source sent bad data).
# MAGIC *   **How**:
# MAGIC     1. Define a filter condition for valid records: `valid_cond = (col("seller_id").isNotNull()) & (col("seller_zip_code_prefix") > 0)`
# MAGIC     2. Split the DataFrame into two:
# MAGIC        - Clean: `df_clean = df.filter(valid_cond)`
# MAGIC        - Bad (Quarantined): `df_bad = df.filter(~valid_cond)`
# MAGIC     3. Add a `_quarantine_reason` column to the bad DataFrame: `df_bad = df_bad.withColumn("_quarantine_reason", lit("Null Seller ID or Invalid Zip"))`
# MAGIC *   **💡 Tip**: The tilde `~` in PySpark acts as a logical NOT operator, reversing your boolean condition.

# COMMAND ----------

# TODO: Apply data quality checks.
# 1. Define the validation condition
# 2. Filter out clean and bad records
# 3. Print the count of clean vs. quarantined rows

# COMMAND ----------

# MAGIC %md
# MAGIC ### 💾 Step 4: Write Clean and Quarantined Data to Delta
# MAGIC *   **What**: Write the clean records to `novabazaar.silver.sellers` and append the bad records to `novabazaar.silver._quarantine`.
# MAGIC *   **Why**: Delta format supports transactional appends, schema enforcement, and compaction.
# MAGIC *   **How**:
# MAGIC     - Clean write: `df_clean.write.format("delta").mode("overwrite").saveAsTable("novabazaar.silver.sellers")`
# MAGIC     - Bad write: `df_bad.write.format("delta").mode("append").saveAsTable("novabazaar.silver._quarantine")`
# MAGIC *   **💡 Tip**: Use `"overwrite"` for dimensional tables to refresh the data, and `"append"` for logs and quarantine tables so history is preserved.

# COMMAND ----------

# TODO: Save your dataframes as Delta tables.
# 1. Write the clean dataframe to novabazaar.silver.sellers
# 2. Write the bad dataframe to novabazaar.silver._quarantine

# COMMAND ----------

# MAGIC %md
# MAGIC ### 🏁 Step 5: Verification Queries
# MAGIC *   **What**: Run SQL statements to check that the clean table was created and the quarantine table holds our bad files.
# MAGIC *   **Why**: Visual verification validates schema correctness.
# MAGIC *   **How**: Run the SQL commands in this cell.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- TODO: Write a query to select the first 5 rows of novabazaar.silver.sellers
