# Databricks notebook source

# COMMAND ----------

# MAGIC %md
# MAGIC # 🧪 NovaBazaar — Scratch Playground Notebook
# MAGIC
# MAGIC **Purpose**: This is your personal sandbox. Use this notebook to experiment, test syntax,
# MAGIC and try things out BEFORE writing the clean version in the milestone notebooks.
# MAGIC
# MAGIC **Rules**:
# MAGIC - ✅ Write rough / exploratory code here freely.
# MAGIC - ✅ Try things, break things, debug things here.
# MAGIC - ❌ Never commit final production code from here.
# MAGIC - ❌ Never save permanent Delta tables from here (use temp views instead).
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 📌 Quick Reference: Our 13 Bronze Tables
# MAGIC
# MAGIC | Table | Domain | Primary Key |
# MAGIC |-------|--------|-------------|
# MAGIC | `novabazaar.bronze.olist_orders` | Sales | `order_id` |
# MAGIC | `novabazaar.bronze.olist_order_items` | Sales | `order_id + order_item_id` |
# MAGIC | `novabazaar.bronze.olist_order_payments` | Sales | `order_id + payment_sequential` |
# MAGIC | `novabazaar.bronze.olist_customers` | Customer | `customer_id` |
# MAGIC | `novabazaar.bronze.olist_order_reviews` | Customer | `review_id` |
# MAGIC | `novabazaar.bronze.olist_products` | Product | `product_id` |
# MAGIC | `novabazaar.bronze.olist_sellers` | Seller | `seller_id` |
# MAGIC | `novabazaar.bronze.olist_geolocation` | Reference | `zip_code_prefix` |
# MAGIC | `novabazaar.bronze.product_category_translation` | Reference | `product_category_name` |
# MAGIC | `novabazaar.bronze.employees` | HR | `employee_id` |
# MAGIC | `novabazaar.bronze.general_ledger` | Finance | `entry_id` |
# MAGIC | `novabazaar.bronze.exchange_rates` | Finance | `date + currency` |
# MAGIC | `novabazaar.bronze.promotions` | Marketing | `promotion_id` |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 🧭 How to Use This Notebook
# MAGIC
# MAGIC 1. Add new cells below for your experiments.
# MAGIC 2. Use `display(df.limit(10))` to preview data visually.
# MAGIC 3. Use `df.printSchema()` to inspect column types.
# MAGIC 4. Use `spark.sql("...")` for SQL exploration.
# MAGIC 5. Create **temp views** instead of tables: `df.createOrReplaceTempView("my_temp_view")`

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🔬 Experiment Zone
# MAGIC Add your exploratory cells below this line.

# COMMAND ----------

# Your experiments go here. This cell is intentionally blank.
# Example to get started - read any bronze table and explore it:
#
# df = spark.read.table("novabazaar.bronze.olist_sellers")
# df.printSchema()
# display(df.limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 💡 Helpful PySpark Cheat Sheet
# MAGIC
# MAGIC ### Reading Data
# MAGIC ```python
# MAGIC # Read a managed Delta table
# MAGIC df = spark.read.table("catalog.schema.table_name")
# MAGIC
# MAGIC # Run SQL directly
# MAGIC df = spark.sql("SELECT * FROM catalog.schema.table_name LIMIT 10")
# MAGIC ```
# MAGIC
# MAGIC ### Inspecting Data
# MAGIC ```python
# MAGIC df.printSchema()          # Print column names and types
# MAGIC df.describe().show()      # Summary statistics (count, mean, min, max)
# MAGIC display(df.limit(10))     # Visual table preview (Databricks only)
# MAGIC print(df.count())         # Total row count
# MAGIC ```
# MAGIC
# MAGIC ### Filtering Data
# MAGIC ```python
# MAGIC from pyspark.sql.functions import col
# MAGIC
# MAGIC df.filter(col("column").isNotNull())        # Remove nulls
# MAGIC df.filter(col("column") > 0)                # Numeric condition
# MAGIC df.filter(col("column").isin(["A", "B"]))   # IN list
# MAGIC ```
# MAGIC
# MAGIC ### Transforming Columns
# MAGIC ```python
# MAGIC from pyspark.sql.functions import col, upper, trim, lit, current_timestamp
# MAGIC
# MAGIC df.withColumn("new_col", col("old_col").cast("integer"))
# MAGIC df.withColumn("city_clean", upper(trim(col("seller_city"))))
# MAGIC df.withColumn("load_ts", current_timestamp())
# MAGIC df.withColumn("source", lit("olist_sellers"))
# MAGIC ```
# MAGIC
# MAGIC ### Writing Data (Temp Views — safe for sandbox use)
# MAGIC ```python
# MAGIC df.createOrReplaceTempView("my_view")
# MAGIC spark.sql("SELECT * FROM my_view LIMIT 5").show()
# MAGIC ```
