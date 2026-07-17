#!/usr/bin/env python3
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import time

HOST = os.environ.get("DATABRICKS_HOST", "https://dbc-bdc4aa7c-39ec.cloud.databricks.com")
TOKEN = os.environ.get("DATABRICKS_TOKEN", "")
USER_EMAIL = os.environ.get("DATABRICKS_USER_EMAIL", "rhitambhaduri7@gmail.com")
GIT_USERNAME = os.environ.get("GIT_USERNAME", "princerhitam")
GIT_PAT = os.environ.get("GIT_PAT", "")
REPO_URL = "https://github.com/princerhitam/novabazaar-lakehouse.git"
BRANCH = "feature/M1-M2-setup-generation"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

def api_call(method, endpoint, payload=None, is_json=True):
    url = f"{HOST}{endpoint}"
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    
    headers = HEADERS.copy()
    if is_json and method in ["POST", "PATCH", "PUT"]:
        headers["Content-Type"] = "application/json"
        
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8')
        print(f"❌ API Error {e.code} on {method} {endpoint}: {err_msg}")
        return {"error": err_msg, "code": e.code}
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return {"error": str(e)}

# ──────────────────────────────────────────────────────────
# 1. SETUP GIT CREDENTIALS
# ──────────────────────────────────────────────────────────
def setup_git_credentials():
    print("\n⚙️ Setting up GitHub credentials in Databricks...")
    res = api_call("GET", "/api/2.0/git-credentials")
    creds = res.get("credentials", [])
    
    payload = {
        "personal_access_token": GIT_PAT,
        "git_username": GIT_USERNAME,
        "git_provider": "gitHub"
    }
    
    if creds:
        cred_id = creds[0]["credential_id"]
        print(f"   Updating existing credential ID: {cred_id}")
        res = api_call("PATCH", f"/api/2.0/git-credentials/{cred_id}", payload)
    else:
        print("   Creating new git credential entry...")
        res = api_call("POST", "/api/2.0/git-credentials", payload)
    
    if "error" in res:
        print("❌ Failed to set Git credentials.")
    else:
        print("✅ Git credentials set successfully.")

# ──────────────────────────────────────────────────────────
# 2. CLONE OR RE-SYNC REPOSITORY
# ──────────────────────────────────────────────────────────
def clone_repository():
    print(f"\n📂 Syncing repository '{REPO_URL}' in Databricks...")
    res = api_call("GET", "/api/2.0/repos")
    repos = res.get("repos", [])
    
    target_path = f"/Repos/{USER_EMAIL}/novabazaar-lakehouse"
    existing_repo = None
    for r in repos:
        if r["path"] == target_path:
            existing_repo = r
            break
            
    if existing_repo:
        repo_id = existing_repo["id"]
        print(f"   Repository already exists in Databricks (ID: {repo_id}). Recreating for clean slate...")
        api_call("DELETE", f"/api/2.0/repos/{repo_id}")
        time.sleep(1)
    else:
        # Fallback: Delete the folder directly in case of a non-repo directory conflict
        print("   Checking/deleting conflicting workspace directories...")
        api_call("POST", "/api/2.0/workspace/delete", {"path": target_path, "recursive": True})
        time.sleep(1)
        
    payload = {
        "url": REPO_URL,
        "provider": "gitHub",
        "path": target_path
    }
    print(f"   Cloning repo into {target_path}...")
    res = api_call("POST", "/api/2.0/repos", payload)
    
    if "error" in res:
        print(f"❌ Failed to clone repository: {res.get('error')}")
        return False
        
    repo_id = res["id"]
    print(f"✅ Repository cloned successfully (ID: {repo_id}).")
    
    # Checkout branch
    print(f"   Checking out branch: {BRANCH}...")
    branch_payload = {"branch": BRANCH}
    res = api_call("PATCH", f"/api/2.0/repos/{repo_id}", branch_payload)
    if "error" in res:
        print(f"❌ Failed to checkout branch {BRANCH}: {res.get('error')}")
        return False
    print(f"✅ Active branch set to: {BRANCH}")
    return True

# ──────────────────────────────────────────────────────────
# 3. UPLOAD FILES TO UNITY CATALOG VOLUME VIA FILES API
# ──────────────────────────────────────────────────────────
def upload_file_to_volume(local_path, volume_path):
    print(f"📤 Uploading: {os.path.basename(local_path)} -> {volume_path}")
    if not os.path.exists(local_path):
        print(f"   ❌ Local file does not exist: {local_path}")
        return False
        
    # URL format: https://<databricks-instance>/api/2.0/fs/files/Volumes/<path>
    url = f"{HOST}/api/2.0/fs/files{volume_path}"
    
    # We open file and stream/send it directly as binary payload
    try:
        with open(local_path, "rb") as f:
            file_data = f.read()
            
        req = urllib.request.Request(
            url, 
            data=file_data, 
            headers={
                "Authorization": f"Bearer {TOKEN}",
                "Content-Type": "application/octet-stream"
            },
            method="PUT"
        )
        
        with urllib.request.urlopen(req) as r:
            resp_body = r.read()
            if resp_body:
                res = json.loads(resp_body)
            
        print(f"   ✅ Uploaded successfully.")
        return True
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8')
        print(f"   ❌ Failed upload: HTTP {e.code} - {err_msg}")
        return False
    except Exception as e:
        print(f"   ❌ Network Error: {e}")
        return False

# ──────────────────────────────────────────────────────────
# MAIN RUNNER
# ──────────────────────────────────────────────────────────
def main():
    setup_git_credentials()
    if not clone_repository():
        print("❌ Git repository sync failed. Exiting.")
        return
        
    print("\n🚀 Uploading datasets directly into Unity Catalog Volumes...")
    
    local_base = "/Users/rhitambhaduri/.gemini/antigravity/scratch/novabazaar-lakehouse/data"
    volume_base = "/Volumes/novamart/landing/raw_files"
    
    files_to_upload = [
        # Olist Core
        (f"{local_base}/olist/olist_orders_dataset.csv", f"{volume_base}/olist_orders/olist_orders_dataset.csv"),
        (f"{local_base}/olist/olist_order_items_dataset.csv", f"{volume_base}/olist_order_items/olist_order_items_dataset.csv"),
        (f"{local_base}/olist/olist_order_payments_dataset.csv", f"{volume_base}/olist_order_payments/olist_order_payments_dataset.csv"),
        (f"{local_base}/olist/olist_order_reviews_dataset.csv", f"{volume_base}/olist_order_reviews/olist_order_reviews_dataset.csv"),
        (f"{local_base}/olist/olist_customers_dataset.csv", f"{volume_base}/olist_customers/olist_customers_dataset.csv"),
        (f"{local_base}/olist/olist_products_dataset.csv", f"{volume_base}/olist_products/olist_products_dataset.csv"),
        (f"{local_base}/olist/olist_sellers_dataset.csv", f"{volume_base}/olist_sellers/olist_sellers_dataset.csv"),
        (f"{local_base}/olist/olist_geolocation_dataset.csv", f"{volume_base}/olist_geolocation/olist_geolocation_dataset.csv"),
        (f"{local_base}/olist/product_category_name_translation.csv", f"{volume_base}/product_category_translation/product_category_name_translation.csv"),
        
        # Synthetic Augmentation
        (f"{local_base}/synthetic/employees.csv", f"{volume_base}/employees/employees.csv"),
        (f"{local_base}/synthetic/general_ledger.csv", f"{volume_base}/general_ledger/general_ledger.csv"),
        (f"{local_base}/synthetic/inventory_snapshots.json", f"{volume_base}/inventory_snapshots/inventory_snapshots.json"),
        (f"{local_base}/synthetic/marketing_campaigns.json", f"{volume_base}/marketing_campaigns/marketing_campaigns.json"),
        (f"{local_base}/synthetic/promotions.csv", f"{volume_base}/promotions/promotions.csv"),
        (f"{local_base}/synthetic/exchange_rates.csv", f"{volume_base}/exchange_rates/exchange_rates.csv"),
    ]
    
    success_count = 0
    for local_path, vol_path in files_to_upload:
        if upload_file_to_volume(local_path, vol_path):
            success_count += 1
            
    print(f"\n🎉 Databricks integration completed! Uploaded {success_count}/{len(files_to_upload)} files to UC Volumes.")

if __name__ == "__main__":
    main()
