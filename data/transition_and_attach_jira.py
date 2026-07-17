#!/usr/bin/env python3
import os
import requests
from requests.auth import HTTPBasicAuth

print("🚀 Starting JIRA updates (Done transitions & attachments)...")

HOST = os.environ.get("JIRA_HOST", "https://princerhitam.atlassian.net")
EMAIL = os.environ.get("JIRA_EMAIL", "princerhitam@gmail.com")
TOKEN = os.environ.get("JIRA_TOKEN", "")

if not TOKEN:
    print("❌ JIRA_TOKEN environment variable not set.")
    exit(1)

auth = HTTPBasicAuth(EMAIL, TOKEN)
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# ──────────────────────────────────────────────────────────
# 1. TRANSITION COMPLETED TICKETS TO DONE (ID = 41)
# ──────────────────────────────────────────────────────────
completed_keys = ["SCRUM-6", "SCRUM-11", "SCRUM-12", "SCRUM-13"]
transition_id = "41" # Done

print("\n⚙️ Transitioning completed issues to 'Done' status...")
for key in completed_keys:
    url = f"{HOST}/rest/api/2/issue/{key}/transitions"
    payload = {
        "transition": {
            "id": transition_id
        }
    }
    
    response = requests.post(url, json=payload, auth=auth, headers=headers)
    if response.status_code == 204:
        print(f"   ✅ Issue {key} transitioned to Done.")
    else:
        print(f"   ❌ Failed to transition {key}: {response.status_code} - {response.text}")

# ──────────────────────────────────────────────────────────
# 2. UPLOAD ARCHITECTURE DOCS TO THE FOUNDATIONS EPIC (SCRUM-6)
# ──────────────────────────────────────────────────────────
target_epic = "SCRUM-6"
files_to_attach = [
    "/Users/rhitambhaduri/Desktop/NovaBazaar_Enterprise_Architecture.pptx",
    "/Users/rhitambhaduri/.gemini/antigravity/scratch/novabazaar-lakehouse/docs/architecture.md",
    "/Users/rhitambhaduri/.gemini/antigravity/scratch/novabazaar-lakehouse/docs/data_dictionary.md"
]

print(f"\n📎 Attaching architectural documentation to Epic {target_epic}...")
attach_url = f"{HOST}/rest/api/2/issue/{target_epic}/attachments"
attach_headers = {
    "X-Atlassian-Token": "no-check"
}

for file_path in files_to_attach:
    if not os.path.exists(file_path):
        print(f"   ⚠️ File not found, skipping attachment: {file_path}")
        continue
        
    file_name = os.path.basename(file_path)
    print(f"   Uploading: {file_name}...")
    
    try:
        with open(file_path, "rb") as f:
            files = {
                "file": (file_name, f, "application/octet-stream")
            }
            response = requests.post(attach_url, headers=attach_headers, auth=auth, files=files)
            
        if response.status_code == 200:
            print(f"   ✅ Successfully attached {file_name} to {target_epic}.")
        else:
            print(f"   ❌ Failed to attach {file_name}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Network/File Error during upload: {e}")

print("\n🎉 JIRA board transition and documentation uploads completed successfully!")
