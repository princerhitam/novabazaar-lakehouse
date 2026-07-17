# Databricks notebook source

# COMMAND ----------

# ============================================================================
# NOTEBOOK: 01_data_upload_guide
# ============================================================================
# Layer        : Ingestion Support / Guide
# Domain       : Infrastructure / Data Setup
# Author       : Data Engineering Team
# Created Date : 2026-07-17
# Last Modified: 2026-07-17
# ============================================================================
#
# DESCRIPTION:
#   This notebook serves as the operational guide and verification utility
#   to load all 15 raw source datasets (Olist core e-commerce data + 
#   synthetic enterprise augmentations + CDC snapshots) into the landing zone
#   directories of the Databricks File System (DBFS).
#
#   In Databricks Community Edition (which lacks direct API ingestion or CLI
#   secrets configuration in most setups), files must be uploaded manually
#   using the Databricks Workspace UI or Databricks CLI.
#
#   This notebook:
#     1. Details the source-to-landing mappings.
#     2. Provides utility commands to verify files have been uploaded correctly.
#     3. Displays sizes and row counts of raw files in the landing zones.
#
# BUSINESS CONTEXT:
#   Before pipelines can run, source data must be staged in the Landing Zone.
#   In an enterprise environment, this is automated via SFTP, Kafka Connect,
#   AWS DMS, or Azure Data Factory copy activities.
#
#   For this portfolio-ready Databricks Community Edition project, we simulate
#   this by downloading the dataset locally, generating synthetic ledger and
#   HR datasets, and staging them in DBFS landing paths.
#
# DEPENDENCIES:
#   • Databricks Runtime 13.x+
#   • 00_environment_setup notebook (must be run first to create directories)
#
# ============================================================================

# COMMAND ----------

# ============================================================================
# STEP 1 — Documenting Source-to-Landing Directory Mapping
# ============================================================================
# This dictionary maps local files to their target DBFS landing directories.
#
# Local Repository Path: /data/
# ├── olist/               <- Core e-commerce tables
# ├── synthetic/           <- Multi-domain augmentations (HR, Finance, Inv)
# └── cdc/                 <- Day 2 and Day 3 updates for CDC/SCD testing
# ============================================================================

# COMMAND ----------

# Unity Catalog Volumes Target Base Path
BASE_LANDING_PATH = "/Volumes/novamart/landing/raw_files"

# Source File Metadata Mapping
source_files = {
    # 1. Olist Core CSVs
    "olist_orders_dataset.csv":          f"{BASE_LANDING_PATH}/olist_orders/olist_orders_dataset.csv",
    "olist_order_items_dataset.csv":     f"{BASE_LANDING_PATH}/olist_order_items/olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv":  f"{BASE_LANDING_PATH}/olist_order_payments/olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv":   f"{BASE_LANDING_PATH}/olist_order_reviews/olist_order_reviews_dataset.csv",
    "olist_customers_dataset.csv":       f"{BASE_LANDING_PATH}/olist_customers/olist_customers_dataset.csv",
    "olist_products_dataset.csv":        f"{BASE_LANDING_PATH}/olist_products/olist_products_dataset.csv",
    "olist_sellers_dataset.csv":         f"{BASE_LANDING_PATH}/olist_sellers/olist_sellers_dataset.csv",
    "olist_geolocation_dataset.csv":     f"{BASE_LANDING_PATH}/olist_geolocation/olist_geolocation_dataset.csv",
    "product_category_name_translation.csv": f"{BASE_LANDING_PATH}/product_category_translation/product_category_name_translation.csv",
    
    # 2. Synthetic Enterprise Augmentations
    "employees.csv":                     f"{BASE_LANDING_PATH}/employees/employees.csv",
    "general_ledger.csv":                f"{BASE_LANDING_PATH}/general_ledger/general_ledger.csv",
    "inventory_snapshots.json":          f"{BASE_LANDING_PATH}/inventory_snapshots/inventory_snapshots.json",
    "marketing_campaigns.json":          f"{BASE_LANDING_PATH}/marketing_campaigns/marketing_campaigns.json",
    "promotions.csv":                    f"{BASE_LANDING_PATH}/promotions/promotions.csv",
    "exchange_rates.csv":                f"{BASE_LANDING_PATH}/exchange_rates/exchange_rates.csv",
}

print("📌 Target Landings mapped. Use the Databricks UI (Catalog -> DBFS -> FileStore) to upload files.")

# COMMAND ----------

# ============================================================================
# STEP 2 — How to Upload via Databricks UI
# ============================================================================
# Since DBFS direct upload commands are blocked or restricted in CE, use:
#
# 1. Open Databricks Workspace -> Click "Catalog" in the sidebar.
# 2. Click "DBFS" tab (if not visible, enable it in Admin Settings -> Workspace Settings -> DBFS File Browser).
# 3. Navigate to FileStore -> novabazaar -> landing.
# 4. Enter each source folder, click "Upload" in the top-right, and upload the corresponding file.
#
# Note: For CDC folders, create day2/day3 directories inside landing/
#       or stage them under the base landing directories before running CDC pipelines.
# ============================================================================

# COMMAND ----------

# ============================================================================
# STEP 3 — Verify Uploaded Files
# ============================================================================
# This script lists all folders and verifies if the expected file exists.
# It prints the size of each file.
# ============================================================================

import os

print("🔍 Scanning DBFS Landing Zone for uploaded files...\n")
print(f"{'Source System / File':<35} | {'Status':<10} | {'File Size (MB)':<15} | {'Path'}")
print("-" * 110)

missing_count = 0
found_count = 0

for file_name, dbfs_path in source_files.items():
    try:
        # Check file existence in DBFS using dbutils
        file_info_list = dbutils.fs.ls(os.path.dirname(dbfs_path))
        
        # Look for the file in the directory
        file_info = None
        for info in file_info_list:
            if info.name == file_name:
                file_info = info
                break
        
        if file_info:
            size_mb = round(file_info.size / (1024 * 1024), 2)
            print(f"{file_name:<35} | {'✅ FOUND':<10} | {size_mb:<15} | {dbfs_path}")
            found_count += 1
        else:
            print(f"{file_name:<35} | {'❌ MISSING':<10} | {'-':<15} | {dbfs_path}")
            missing_count += 1
            
    except Exception as e:
        # Occurs if directory itself doesn't exist or is empty
        print(f"{file_name:<35} | {'❌ MISSING':<10} | {'-':<15} | {dbfs_path}")
        missing_count += 1

print("\n" + "=" * 110)
print(f"📊 SUMMARY: {found_count} files found, {missing_count} files missing.")
print("=" * 110)

if missing_count > 0:
    print("⚠️  Action required: Please upload the missing files to the respective folders before starting Milestone 3 Ingestion.")
else:
    print("🎉 Success! All landing zone files verified and ready for Bronze ingestion.")

# COMMAND ----------

# ============================================================================
# STEP 4 — Preview Uploaded Data
# ============================================================================
# Quick check to ensure spark can read the landed data.
# Previews first 3 rows of Olist Orders and Synthetic Employees if found.
# ============================================================================

orders_path = source_files["olist_orders_dataset.csv"]
employees_path = source_files["employees.csv"]

# 1. Preview Olist Orders
try:
    print("📖 Previewing olist_orders_dataset.csv:")
    df_orders = spark.read.option("header", "true").option("inferSchema", "true").csv(orders_path)
    df_orders.limit(3).show(truncate=False)
except Exception as e:
    print("   ❌ Cannot preview orders. File might be missing.")

print("\n" + "-" * 50 + "\n")

# 2. Preview Synthetic Employees
try:
    print("📖 Previewing employees.csv:")
    df_emp = spark.read.option("header", "true").option("inferSchema", "true").csv(employees_path)
    df_emp.limit(3).show(truncate=False)
except Exception as e:
    print("   ❌ Cannot preview employees. File might be missing.")

# COMMAND ----------

# ============================================================================
# STEP 5 — Common Interview Questions
# ============================================================================
# Q1: In an enterprise environment, how do you ingest CSV and JSON files?
# A1: Using orchestration tools like Airflow or ADF, staging files onto cloud storage
#     (S3/ADLS/GCS) in parquet format or loading directly using Spark Auto Loader.
#
# Q2: Why is it bad practice to run spark.read with inferSchema=True in production?
# A2: InferSchema requires a full read of the dataset to infer datatypes, doubling 
#     read I/O. In production, we explicitly define schemas as StructTypes to
#     ensure reliability, speed, and schema enforcement.
# ============================================================================
