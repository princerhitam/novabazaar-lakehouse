#!/usr/bin/env python3
import os
import json
import urllib.request
import urllib.error
import time

print("🚀 Starting Developer Portal & Schema Dashboard creation in Notion...")

TOKEN = os.environ.get("NOTION_TOKEN", "")
NOTION_VERSION = "2022-06-28"
PARENT_PAGE_ID = os.environ.get("NOTION_PARENT_PAGE_ID", "376b02f5-197a-80c9-a17a-ed46a260d43e")

def api_call(method, endpoint, payload=None):
    url = f"https://api.notion.com/v1{endpoint}"
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    req = urllib.request.Request(
        url, 
        data=data, 
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION
        },
        method=method
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        err = e.read().decode('utf-8')
        print(f"❌ HTTP {e.code} Error: {err}")
        return {"error": err, "code": e.code}
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return {"error": str(e)}

# Helper functions for blocks
def heading_1(text):
    return {
        "object": "block",
        "type": "heading_1",
        "heading_1": {
            "rich_text": [{"type": "text", "text": {"content": text, "link": None}, "annotations": {"bold": True}}]
        }
    }

def heading_2(text):
    return {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": text, "link": None}, "annotations": {"bold": True}}]
        }
    }

def heading_3(text):
    return {
        "object": "block",
        "type": "heading_3",
        "heading_3": {
            "rich_text": [{"type": "text", "text": {"content": text, "link": None}, "annotations": {"bold": True}}]
        }
    }

def divider():
    return {"object": "block", "type": "divider", "divider": {}}

def callout(text, icon="💡", color="blue_background"):
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
            "icon": {"type": "emoji", "emoji": icon},
            "color": color
        }
    }

def paragraph(text, bold_prefix="", link_url="", link_text=""):
    rt = []
    if bold_prefix:
        rt.append({"type": "text", "text": {"content": bold_prefix}, "annotations": {"bold": True}})
    if text:
        rt.append({"type": "text", "text": {"content": text}})
    if link_url and link_text:
        rt.append({"type": "text", "text": {"content": link_text, "link": {"url": link_url}}, "annotations": {"bold": True, "color": "blue"}})
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": rt}
    }

def code_block(content, language="plain text"):
    if len(content) > 2000:
        content = content[:1997] + "..."
    return {
        "object": "block",
        "type": "code",
        "code": {
            "rich_text": [{"type": "text", "text": {"content": content}}],
            "language": language
        }
    }

def bulleted_list_item(text):
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text}}]}
    }

# DBML Schema Code
dbml_code = """// NovaBazaar Star Schema DBML Definition
// Paste this code into https://dbdiagram.io to visualize & edit!

Table fact_sales {
  sales_key bigint [pk, increment, note: 'Surrogate Key']
  order_id varchar [note: 'Business Key']
  order_item_id int
  customer_key bigint [ref: > dim_customer.customer_key]
  product_key bigint [ref: > dim_product.product_key]
  seller_key bigint [ref: > dim_seller.seller_key]
  employee_key bigint [ref: > dim_employee.employee_key]
  order_date_key int [ref: > dim_date.date_key]
  price double
  freight_value double
  quantity int
  margin double
}

Table fact_inventory_snapshot {
  inventory_key bigint [pk, increment]
  store_key bigint [ref: > dim_store.store_key]
  product_key bigint [ref: > dim_product.product_key]
  date_key int [ref: > dim_date.date_key]
  quantity_on_hand int
  quantity_on_order int
  reorder_point int
}

Table dim_customer {
  customer_key bigint [pk]
  customer_id varchar
  customer_unique_id varchar
  zip_code_prefix varchar
  city varchar
  state varchar
  effective_start_date timestamp
  effective_end_date timestamp
  is_current boolean
}

Table dim_product {
  product_key bigint [pk]
  product_id varchar
  category_name varchar
  category_name_english varchar
  name_length int
  description_length int
  photos_qty int
  weight_g int
  length_cm int
  height_cm int
  width_cm int
  effective_start_date timestamp
  effective_end_date timestamp
  is_current boolean
}

Table dim_seller {
  seller_key bigint [pk]
  seller_id varchar
  zip_code_prefix varchar
  city varchar
  state varchar
}

Table dim_employee {
  employee_key bigint [pk]
  employee_id int
  first_name varchar
  last_name varchar
  role varchar
  department varchar
  salary double
  manager_id int
  effective_start_date timestamp
  effective_end_date timestamp
  is_current boolean
}

Table dim_store {
  store_key bigint [pk]
  store_id varchar
  store_name varchar
  city varchar
  state varchar
}

Table dim_date {
  date_key int [pk]
  full_date date
  day_of_week int
  day_name varchar
  day_of_month int
  month int
  month_name varchar
  quarter int
  year int
  is_weekend boolean
}
"""

# Mermaid schema code for native Notion rendering
mermaid_code = """erDiagram
    fact_sales }|..|| dim_customer : customer_key
    fact_sales }|..|| dim_product : product_key
    fact_sales }|..|| dim_seller : seller_key
    fact_sales }|..|| dim_employee : employee_key
    fact_sales }|..|| dim_date : order_date_key
    fact_inventory_snapshot }|..|| dim_store : store_key
    fact_inventory_snapshot }|..|| dim_product : product_key
    fact_inventory_snapshot }|..|| dim_date : date_key
"""

# Assemble page blocks
blocks = [
    callout(
        "Welcome to the NovaBazaar Developer Portal & Data Architecture Dashboard. Below are the key project links and interactive tools to explore, visualize, and modify the enterprise lakehouse schemas.",
        "🛠️", "blue_background"
    ),
    divider(),
    
    heading_2("🔗 Important Project Links"),
    paragraph("🐙 GitHub Repository: ", link_url="https://github.com/princerhitam/novabazaar-lakehouse", link_text="princerhitam/novabazaar-lakehouse (feature/M1-M2-setup-generation)"),
    paragraph("📊 JIRA Kanban Board: ", link_url="https://princerhitam.atlassian.net/jira/software/projects/SCRUM/boards/1", link_text="Jira active Sprint Board (My Software Team)"),
    paragraph("📋 JIRA Backlog Planning: ", link_url="https://princerhitam.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog", link_text="Jira Backlog Tracker"),
    paragraph("📈 JIRA Project Roadmap: ", link_url="https://princerhitam.atlassian.net/jira/software/projects/SCRUM/boards/1/timeline", link_text="Jira Project Roadmap Timeline"),
    paragraph("🖥️ Databricks Workspace: ", link_url="https://dbc-bdc4aa7c-39ec.cloud.databricks.com", link_text="Databricks Community Edition Instance"),
    paragraph("🎨 Interactive Schema Visualizer: ", link_url="https://dbdiagram.io", link_text="dbdiagram.io editor"),
    divider(),
    
    heading_2("📐 Interactive Data Model Playboard"),
    paragraph("We define our schemas using DBML (Database Markup Language). This allows us to maintain text-based diagrams that are easy to version control in Git and simple to update."),
    callout("How to play with the schema: Copy the DBML code block at the bottom of this page, open dbdiagram.io, paste it in the editor on the left. The interactive diagram will render instantly. You can double click entities, drag connections, and export schema SQL scripts!", "💡", "green_background"),
    
    heading_3("Gold Layer Relationships (Mermaid.js Representation)"),
    code_block(mermaid_code, "mermaid"),
    divider(),
    
    heading_2("📝 DBML Schema Specification"),
    code_block(dbml_code, "sql")
]

# Create the page
payload = {
    "parent": {"page_id": PARENT_PAGE_ID},
    "icon": {"type": "emoji", "emoji": "🛠️"},
    "properties": {
        "title": {
            "title": [{"type": "text", "text": {"content": "🛠️ Developer Portal & Data Architecture Dashboard"}}]
        }
    },
    "children": blocks[:100]
}

res = api_call("POST", "/pages", payload)
if "error" in res:
    print(f"❌ Failed to create Notion dashboard page: {res.get('error')}")
else:
    print(f"✅ Notion Dashboard created successfully!")
    print(f"   URL: {res.get('url', 'N/A')}")
