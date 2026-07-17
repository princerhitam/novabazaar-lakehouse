#!/usr/bin/env python3
import os
import csv
import json
import base64
import urllib.request
import urllib.error
import time

print("🚀 Starting JIRA backlog import for NovaBazaar...")

HOST = os.environ.get("JIRA_HOST", "https://princerhitam.atlassian.net")
EMAIL = os.environ.get("JIRA_EMAIL", "princerhitam@gmail.com")
TOKEN = os.environ.get("JIRA_TOKEN", "")
PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY", "SCRUM")

auth_str = f"{EMAIL}:{TOKEN}"
b64_auth = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')

HEADERS = {
    "Authorization": f"Basic {b64_auth}",
    "Content-Type": "application/json"
}

def api_call(method, endpoint, payload=None):
    url = f"{HOST}{endpoint}"
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
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

# Load CSV tickets
csv_path = "/Users/rhitambhaduri/Desktop/NovaBazaar_Jira_Import.csv"
if not os.path.exists(csv_path):
    print(f"❌ Source CSV file not found at: {csv_path}")
    exit(1)

epics_list = []
stories_list = []

with open(csv_path, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["Issue Type"] == "Epic":
            epics_list.append(row)
        else:
            stories_list.append(row)

print(f"📝 Read {len(epics_list)} Epics and {len(stories_list)} Stories/Tasks from CSV.")

# ──────────────────────────────────────────────────────────
# 1. CREATE EPICS
# ──────────────────────────────────────────────────────────
epic_map = {} # Maps Epic Summary -> Epic Key (e.g. SCRUM-5)

print("\n🏗️ Creating Epics in Jira...")
for epic in epics_list:
    summary = epic["Summary"]
    description = epic["Description"]
    
    # Append Acceptance Criteria to description
    full_desc = f"{description}\n\n*Acceptance Criteria:*\n{epic['Acceptance Criteria']}"
    
    payload = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": full_desc,
            "issuetype": {"name": "Epic"},
            "priority": {"name": epic["Priority"]},
            "labels": [l.strip() for l in epic["Labels"].split(",") if l.strip()]
        }
    }
    
    # Use API v2 for easy string descriptions
    res = api_call("POST", "/rest/api/2/issue", payload)
    if "error" in res:
        print(f"❌ Failed to create Epic '{summary}': {res.get('error')}")
    else:
        epic_key = res["key"]
        epic_map[summary] = epic_key
        print(f"✅ Epic Created: {epic_key} - {summary}")
        time.sleep(0.5)

# ──────────────────────────────────────────────────────────
# 2. CREATE STORIES & LINK TO EPICS
# ──────────────────────────────────────────────────────────
print("\n📋 Creating Stories and linking to parents...")
for story in stories_list:
    summary = story["Summary"]
    description = story["Description"]
    epic_link = story["Epic Link"]
    story_points = story["Story Points"]
    labels = [l.strip() for l in story["Labels"].split(",") if l.strip()]
    
    # Build complete description detailing estimate and criteria
    full_desc = description
    if story_points:
        full_desc += f"\n\n*Story Points Estimate:* {story_points}"
    if story["Acceptance Criteria"]:
        full_desc += f"\n\n*Acceptance Criteria:*\n{story['Acceptance Criteria']}"
        
    payload = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": full_desc,
            "issuetype": {"name": "Story"},
            "priority": {"name": story["Priority"]},
            "labels": labels
        }
    }
    
    # Link to parent Epic if mapped
    if epic_link in epic_map:
        payload["fields"]["parent"] = {"key": epic_map[epic_link]}
        
    res = api_call("POST", "/rest/api/2/issue", payload)
    if "error" in res:
        # Fallback without parent key in case the issue type scheme restricts it
        print(f"   ⚠️ Link failed, attempting story creation without parent link...")
        payload["fields"].pop("parent", None)
        res = api_call("POST", "/rest/api/2/issue", payload)
        
    if "error" in res:
         print(f"❌ Failed to create Story '{summary}': {res.get('error')}")
    else:
        story_key = res["key"]
        print(f"✅ Story Created: {story_key} (Linked to {epic_map.get(epic_link, 'None')}) - {summary}")
        time.sleep(0.5)

print("\n🎉 JIRA Backlog Import Completed Successfully!")
