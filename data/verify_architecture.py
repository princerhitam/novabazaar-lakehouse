#!/usr/bin/env python3
import os
import json
import urllib.request
import urllib.error
import time

print("🔍 Starting Architectural Audit & Consistency Verification...")

HOST = os.environ.get("DATABRICKS_HOST", "https://dbc-bdc4aa7c-39ec.cloud.databricks.com")
TOKEN = os.environ.get("DATABRICKS_TOKEN", "")
warehouse_id = "6591a9f8e281d7f2"

if not TOKEN:
    print("❌ DATABRICKS_TOKEN environment variable is not set.")
    exit(1)

def run_query(stmt):
    url = f"{HOST}/api/2.0/sql/statements"
    payload = {
        "statement": stmt,
        "warehouse_id": warehouse_id
    }
    req = urllib.request.Request(
        url, 
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as r:
            res = json.loads(r.read())
            statement_id = res["statement_id"]
            
            # Poll for completion (max 10 seconds)
            for _ in range(10):
                r2 = urllib.request.urlopen(urllib.request.Request(
                    f"{HOST}/api/2.0/sql/statements/{statement_id}",
                    headers={"Authorization": f"Bearer {TOKEN}"}
                ))
                res2 = json.loads(r2.read())
                state = res2.get("status", {}).get("state")
                if state == "SUCCEEDED":
                    return res2.get("result", {}).get("data_array", [])
                elif state in ["FAILED", "CANCELED"]:
                    return {"error": res2.get("status", {}).get("error", "Query failed")}
                time.sleep(1)
            return {"error": "Query timeout"}
    except Exception as e:
        return {"error": str(e)}

discrepancies = []

# ──────────────────────────────────────────────────────────
# 1. VERIFY SCHEMAS IN CATALOG
# ──────────────────────────────────────────────────────────
print("\n1. Auditing Metastore Schemas...")
expected_schemas = ["landing", "bronze", "silver", "gold", "audit", "config"]
schemas_data = run_query("SHOW SCHEMAS IN novabazaar")

if isinstance(schemas_data, dict) and "error" in schemas_data:
    print(f"❌ Failed to verify schemas: {schemas_data['error']}")
    discrepancies.append(f"Catalog novabazaar accessibility: {schemas_data['error']}")
else:
    actual_schemas = [row[0].lower() for row in schemas_data]
    for s in expected_schemas:
        if s in actual_schemas:
            print(f"   ✅ Schema exists: novabazaar.{s}")
        else:
            print(f"   ❌ Schema missing: novabazaar.{s}")
            discrepancies.append(f"Missing schema: novabazaar.{s}")

# ──────────────────────────────────────────────────────────
# 2. VERIFY AUDIT TABLES
# ──────────────────────────────────────────────────────────
print("\n2. Auditing Audit Tables...")
expected_tables = {
    "log_pipeline_execution": 17,
    "log_dq_results": 12,
    "log_reconciliation": 13,
    "log_cdc_tracking": 8,
    "watermark_tracking": 7
}

tables_data = run_query("SHOW TABLES IN novabazaar.audit")
if isinstance(tables_data, dict) and "error" in tables_data:
    print(f"❌ Failed to verify audit tables: {tables_data['error']}")
    discrepancies.append(f"Audit schema accessibility: {tables_data['error']}")
else:
    actual_tables = [row[1].lower() for row in tables_data]
    for t, expected_cols in expected_tables.items():
        if t in actual_tables:
            # Check column count
            desc = run_query(f"DESCRIBE TABLE novabazaar.audit.{t}")
            if isinstance(desc, list):
                col_count = len(desc)
                if col_count == expected_cols:
                    print(f"   ✅ Table novabazaar.audit.{t} exists (correct column count: {col_count})")
                else:
                    print(f"   ⚠️  Table novabazaar.audit.{t} column count mismatch: expected {expected_cols}, got {col_count}")
                    discrepancies.append(f"Column mismatch in novabazaar.audit.{t}: expected {expected_cols}, got {col_count}")
            else:
                discrepancies.append(f"Failed to describe table novabazaar.audit.{t}")
        else:
            print(f"   ❌ Table missing: novabazaar.audit.{t}")
            discrepancies.append(f"Missing table: novabazaar.audit.{t}")

# ──────────────────────────────────────────────────────────
# 3. VERIFY VOLUME AND LANDING SUBDIRECTORIES
# ──────────────────────────────────────────────────────────
print("\n3. Auditing Volume Landing Zone & Files...")
config_path = "/Users/rhitambhaduri/.gemini/antigravity/scratch/novabazaar-lakehouse/config/source_config.json"
if not os.path.exists(config_path):
    print(f"❌ Configuration file not found at: {config_path}")
    exit(1)

with open(config_path, "r") as f:
    config = json.load(f)

expected_source_ids = [src["source_id"] for src in config["sources"]]

# List files inside Volume
volume_data = run_query("LIST '/Volumes/novabazaar/landing/raw_files'")
if isinstance(volume_data, dict) and "error" in volume_data:
    print(f"❌ Failed to list files inside volume: {volume_data['error']}")
    discrepancies.append(f"Volume raw_files accessibility: {volume_data['error']}")
else:
    # LIST returns path and size
    actual_dirs = []
    for row in volume_data:
        # row[1] contains the relative path (e.g. 'employees/')
        dir_name = row[1].strip("/").lower()
        actual_dirs.append(dir_name)
            
    for s_id in expected_source_ids:
        if s_id.lower() in actual_dirs:
            print(f"   ✅ Landing directory exists: /Volumes/novabazaar/landing/raw_files/{s_id}")
        else:
            print(f"   ❌ Landing directory missing: /Volumes/novabazaar/landing/raw_files/{s_id}")
            discrepancies.append(f"Missing staged folder in volume: {s_id}")

# ──────────────────────────────────────────────────────────
# SUMMARY REPORT
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("🏁 AUDIT SUMMARY REPORT")
print("=" * 60)
if discrepancies:
    print(f"❌ Verification failed. Found {len(discrepancies)} discrepancies:")
    for d in discrepancies:
        print(f"   - {d}")
else:
    print("✅ Verification completed successfully. All components are aligned, consistent, and correct!")
print("=" * 60)
