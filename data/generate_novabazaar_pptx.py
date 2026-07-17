#!/usr/bin/env python3
"""
Generate a premium, visual PowerPoint presentation for the NovaBazaar Enterprise Lakehouse Architecture.
Draws visual flowcharts, schema diagrams, and grids using python-pptx.
"""
import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

print("🚀 Initializing presentation generator...")

# Colors (Deep Slate & Teal Theme)
BG_COLOR = RGBColor(15, 23, 42)      # Deep Slate #0f172a
WHITE = RGBColor(248, 250, 252)     # #f8fafc
TEXT_LIGHT = RGBColor(241, 245, 249)# #f1f5f9
TEXT_MUTED = RGBColor(148, 163, 184)# #94a3b8
TEAL = RGBColor(20, 184, 166)       # Accent Teal #14b8a6
TEAL_LIGHT = RGBColor(204, 251, 241) # Light Teal #ccfbf1
BRONZE_COLOR = RGBColor(212, 175, 55)# Bronze #d4af37
SILVER_COLOR = RGBColor(192, 192, 192)# Silver #c0c0c0
GOLD_COLOR = RGBColor(255, 215, 0)   # Gold #ffd700
RED_ACCENT = RGBColor(239, 68, 68)   # Red #ef4444
DARK_CARD = RGBColor(30, 41, 59)     # Dark Slate Card #1e293b

prs = Presentation()
prs.slide_width = Inches(13.33)  # 16:9 Widescreen
prs.slide_height = Inches(7.5)

# Helper: Set background color
def set_slide_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = BG_COLOR

# Helper: Add Slide Header
def add_slide_header(slide, title_text, category_text="SOLUTION ARCHITECTURE"):
    # Category Tag
    tx_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
    tf_cat = tx_cat.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.name = "Arial"
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = TEAL
    
    # Title
    tx_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
    tf_title = tx_title.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.name = "Arial"
    p_title.font.size = Pt(28)
    p_title.font.bold = True
    p_title.font.color.rgb = WHITE

# ──────────────────────────────────────────────────────────
# SLIDE 1: TITLE SLIDE (Dark Premium)
# ──────────────────────────────────────────────────────────
slide_layout = prs.slide_layouts[6] # Blank
slide1 = prs.slides.add_slide(slide_layout)
set_slide_background(slide1)

# Large Center Accent Graphic (Teal bar)
shape = slide1.shapes.add_shape(
    MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(2.2), Inches(0.15), Inches(3.2)
)
shape.fill.solid()
shape.fill.fore_color.rgb = TEAL
shape.line.fill.background()

# Title text frame
tx = slide1.shapes.add_textbox(Inches(1.2), Inches(2.1), Inches(11.0), Inches(2.5))
tf = tx.text_frame
tf.word_wrap = True

p_main = tf.paragraphs[0]
p_main.text = "NovaBazaar Enterprise Lakehouse"
p_main.font.name = "Arial"
p_main.font.size = Pt(44)
p_main.font.bold = True
p_main.font.color.rgb = WHITE

p_sub = tf.add_paragraph()
p_sub.text = "Solution Design & Platform Architecture Blueprint"
p_sub.font.name = "Arial"
p_sub.font.size = Pt(22)
p_sub.font.color.rgb = TEAL
p_sub.space_before = Pt(12)

# Footnote
tx_foot = slide1.shapes.add_textbox(Inches(1.2), Inches(5.5), Inches(11.0), Inches(1.0))
tf_foot = tx_foot.text_frame
p_foot = tf_foot.paragraphs[0]
p_foot.text = "Databricks Community Edition  |  Unity Catalog  |  Medallion Architecture  |  Star Schema  |  Delta Lake"
p_foot.font.name = "Arial"
p_foot.font.size = Pt(12)
p_foot.font.color.rgb = TEXT_MUTED

# ──────────────────────────────────────────────────────────
# SLIDE 2: BUSINESS BACKGROUND & COST OF INACTION
# ──────────────────────────────────────────────────────────
slide2 = prs.slides.add_slide(slide_layout)
set_slide_background(slide2)
add_slide_header(slide2, "Business Case: The $530M Cost of Inaction", "BUSINESS OPPORTUNITY")

# Left Column: The Problem Statement (Card style)
card_left = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
card_left.fill.solid()
card_left.fill.fore_color.rgb = DARK_CARD
card_left.line.color.rgb = TEAL
card_left.line.width = Pt(1.5)

tf_left = card_left.text_frame
tf_left.word_wrap = True
tf_left.margin_left = Inches(0.3)
tf_left.margin_right = Inches(0.3)
tf_left.margin_top = Inches(0.3)

p_lp = tf_left.paragraphs[0]
p_lp.text = "The Challenge: Data Inefficiency"
p_lp.font.name = "Arial"
p_lp.font.size = Pt(20)
p_lp.font.bold = True
p_lp.font.color.rgb = TEAL
p_lp.space_after = Pt(14)

bullets = [
    "Data Silos: 15 disconnected source systems across e-commerce, POS, logistics, finance, and marketing.",
    "Batch Latency: Overnight updates limit customer responsiveness and result in frequent stockouts.",
    "Lack of Trust: Inconsistent metrics lead to manual reconciliation cycles (taking 15 days of manual effort/month).",
    "Analytics Ceiling: Unable to support predictive analytics or customer segmentation due to unreliable data."
]
for b in bullets:
    p = tf_left.add_paragraph()
    p.text = "• " + b
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_LIGHT
    p.space_after = Pt(10)

# Right Column: The Quantified Impact
tx_right_title = slide2.shapes.add_textbox(Inches(6.8), Inches(1.8), Inches(5.6), Inches(0.5))
p_rt = tx_right_title.text_frame.paragraphs[0]
p_rt.text = "Annual Cost of Inaction (Total: ~$530M)"
p_rt.font.name = "Arial"
p_rt.font.size = Pt(18)
p_rt.font.bold = True
p_rt.font.color.rgb = WHITE

# Grid of KPI Cards (2x2)
kpis = [
    {"val": "$320M", "label": "Inventory stockouts & overstock", "color": RED_ACCENT},
    {"val": "$85M", "label": "Marketing campaign waste", "color": TEAL},
    {"val": "$50M", "label": "Compliance & SOX audit risk", "color": BRONZE_COLOR},
    {"val": "$75M", "label": "Lost margin & pricing errors", "color": GOLD_COLOR}
]

positions = [
    (Inches(6.8), Inches(2.4)),  # Top Left
    (Inches(9.8), Inches(2.4)),  # Top Right
    (Inches(6.8), Inches(4.4)),  # Bottom Left
    (Inches(9.8), Inches(4.4))   # Bottom Right
]

for idx, kpi in enumerate(kpis):
    x, y = positions[idx]
    
    # KPI Box
    box = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, Inches(2.7), Inches(1.8))
    box.fill.solid()
    box.fill.fore_color.rgb = DARK_CARD
    box.line.color.rgb = kpi["color"]
    box.line.width = Pt(1.5)
    
    tf_box = box.text_frame
    tf_box.word_wrap = True
    tf_box.margin_left = Inches(0.15)
    tf_box.margin_right = Inches(0.15)
    tf_box.margin_top = Inches(0.2)
    
    p_val = tf_box.paragraphs[0]
    p_val.text = kpi["val"]
    p_val.alignment = PP_ALIGN.CENTER
    p_val.font.name = "Arial"
    p_val.font.size = Pt(36)
    p_val.font.bold = True
    p_val.font.color.rgb = kpi["color"]
    
    p_lbl = tf_box.add_paragraph()
    p_lbl.text = kpi["label"]
    p_lbl.alignment = PP_ALIGN.CENTER
    p_lbl.font.name = "Arial"
    p_lbl.font.size = Pt(11)
    p_lbl.font.color.rgb = TEXT_LIGHT
    p_lbl.space_before = Pt(8)

# ──────────────────────────────────────────────────────────
# SLIDE 3: MEDALLION ARCHITECTURE (Visual Flowchart)
# ──────────────────────────────────────────────────────────
slide3 = prs.slides.add_slide(slide_layout)
set_slide_background(slide3)
add_slide_header(slide3, "The Medallion Pipeline Architecture", "TECHNICAL BLUEPRINT")

# Ingestion Source Box (Left)
src_box = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(2.4), Inches(2.0), Inches(3.2))
src_box.fill.solid()
src_box.fill.fore_color.rgb = DARK_CARD
src_box.line.color.rgb = TEXT_MUTED
src_box.line.width = Pt(1.5)
tf_src = src_box.text_frame
tf_src.word_wrap = True
p_src = tf_src.paragraphs[0]
p_src.text = "🌊 SOURCE DATA\n\n- Olist E-Com (9)\n- Synthetic (6)\n- Format: CSV/JSON\n\nStaged in landing zone"
p_src.font.name = "Arial"
p_src.font.size = Pt(13)
p_src.font.color.rgb = TEXT_LIGHT

# Bronze Box
b_box = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(3.8), Inches(2.4), Inches(2.4), Inches(3.2))
b_box.fill.solid()
b_box.fill.fore_color.rgb = DARK_CARD
b_box.line.color.rgb = BRONZE_COLOR
b_box.line.width = Pt(2)
tf_b = b_box.text_frame
tf_b.word_wrap = True
p_b = tf_b.paragraphs[0]
p_b.text = "🥉 BRONZE LAYER\nRaw Ingestion\n\n- Schema-on-Read\n- Append-only structure\n- Added Ingestion Meta\n- Formatted as Delta"
p_b.font.name = "Arial"
p_b.font.size = Pt(13)
p_b.font.color.rgb = TEXT_LIGHT

# Silver Box
s_box = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.2), Inches(2.4), Inches(2.4), Inches(3.2))
s_box.fill.solid()
s_box.fill.fore_color.rgb = DARK_CARD
s_box.line.color.rgb = SILVER_COLOR
s_box.line.width = Pt(2)
tf_s = s_box.text_frame
tf_s.word_wrap = True
p_s = tf_s.paragraphs[0]
p_s.text = "🥈 SILVER LAYER\nCleanse & Conform\n\n- Data Quality validation\n- Route bad records to quarantine\n- SCD Type 1 & 2\n- Deduplication"
p_s.font.name = "Arial"
p_s.font.size = Pt(13)
p_s.font.color.rgb = TEXT_LIGHT

# Gold Box
g_box = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(10.6), Inches(2.4), Inches(2.0), Inches(3.2))
g_box.fill.solid()
g_box.fill.fore_color.rgb = DARK_CARD
g_box.line.color.rgb = GOLD_COLOR
g_box.line.width = Pt(2)
tf_g = g_box.text_frame
tf_g.word_wrap = True
p_g = tf_g.paragraphs[0]
p_g.text = "🥇 GOLD LAYER\nBusiness Serving\n\n- Star Schema\n- Pre-joined Facts & Dimensions\n- Pre-calculated KPIs\n- Fast serving views"
p_g.font.name = "Arial"
p_g.font.size = Pt(13)
p_g.font.color.rgb = TEXT_LIGHT

# Draw connecting arrows programmatically
arrows = [
    (Inches(2.9), Inches(3.8)),
    (Inches(6.3), Inches(3.8)),
    (Inches(9.7), Inches(3.8))
]
for x, y in arrows:
    arrow = slide3.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x, y, Inches(0.8), Inches(0.4))
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = TEAL
    arrow.line.fill.background()

# ──────────────────────────────────────────────────────────
# SLIDE 4: DATA DICTIONARY & DOMAINS
# ──────────────────────────────────────────────────────────
slide4 = prs.slides.add_slide(slide_layout)
set_slide_background(slide4)
add_slide_header(slide4, "Data Sources: 15 Heterogeneous Systems", "DATA INVENTORY")

# Grid table of source systems
rows, cols = 7, 3
left, top, width, height = Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.5)
table_shape = slide4.shapes.add_table(rows, cols, left, top, width, height)
table = table_shape.table

# Set column widths
table.columns[0].width = Inches(3.0)
table.columns[1].width = Inches(2.2)
table.columns[2].width = Inches(6.5)

headers = ["Source System", "Domain", "Key Entities & Description"]
for idx, text in enumerate(headers):
    cell = table.cell(0, idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = DARK_CARD
    p = cell.text_frame.paragraphs[0]
    p.text = text
    p.font.name = "Arial"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = TEAL

data = [
    ["POS & E-Commerce Orders", "Sales", "Real order transactions, payments, reviews, and line items (Olist)."],
    ["Customers & Geography", "Customer / Ref", "Relational geo-prefix table and permanent customer IDs."],
    ["Products & Categories", "Product", "Product details, dimensions, and Portuguese-to-English translations."],
    ["HR Employees (SCD2)", "HR (Synthetic)", "Organizational structure, manager hierarchies, and wage details."],
    ["General Ledger (39K rows)", "Finance (Synth)", "Accounting entries mapped directly to order values for reconciliation audits."],
    ["Inventory Snapshots", "Inventory (Synth)", "Historical daily snapshots of stock on hand, reorder boundaries."]
]

for row_idx, row_data in enumerate(data, 1):
    for col_idx, text in enumerate(row_data):
        cell = table.cell(row_idx, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = BG_COLOR
        p = cell.text_frame.paragraphs[0]
        p.text = text
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_LIGHT

# ──────────────────────────────────────────────────────────
# SLIDE 5: STORAGE ARCHITECTURE — UNITY CATALOG
# ──────────────────────────────────────────────────────────
slide5 = prs.slides.add_slide(slide_layout)
set_slide_background(slide5)
add_slide_header(slide5, "Governed Storage with Unity Catalog Volumes", "DATA GOVERNANCE")

# Left Column (Card for Details)
left_card = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.0), Inches(4.8))
left_card.fill.solid()
left_card.fill.fore_color.rgb = DARK_CARD
left_card.line.color.rgb = TEAL
left_card.line.width = Pt(1.5)

tf_lc = left_card.text_frame
tf_lc.word_wrap = True
tf_lc.margin_left = Inches(0.3)
tf_lc.margin_right = Inches(0.3)
tf_lc.margin_top = Inches(0.3)

p_lct = tf_lc.paragraphs[0]
p_lct.text = "Modern Storage Specifications"
p_lct.font.name = "Arial"
p_lct.font.size = Pt(18)
p_lct.font.bold = True
p_lct.font.color.rgb = TEAL
p_lct.space_after = Pt(14)

uc_bullets = [
    "Volume Path: /Volumes/novamart/landing/raw_files/ -- fully governed directories managed by Unity Catalog.",
    "Security Upgrade: Public DBFS root (/FileStore/) is disabled to protect against data leakage.",
    "Managed Tables: Medallion layer tables (bronze, silver, gold) are stored as managed Delta tables without hardcoding locations.",
    "Storage Isolation: Decouples metadata catalogs from S3 bucket credentials, ensuring strict namespace access control."
]
for b in uc_bullets:
    p = tf_lc.add_paragraph()
    p.text = "• " + b
    p.font.name = "Arial"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_LIGHT
    p.space_after = Pt(10)

# Right: Draw File upload architecture diagram
# Draw Local Mac
mac_box = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.5), Inches(2.2), Inches(2.2), Inches(1.0))
mac_box.fill.solid()
mac_box.fill.fore_color.rgb = DARK_CARD
mac_box.line.color.rgb = TEXT_MUTED
mac_box.text_frame.paragraphs[0].text = "💻 Local Mac\n/data/ directory"
mac_box.text_frame.paragraphs[0].font.name = "Arial"
mac_box.text_frame.paragraphs[0].font.size = Pt(13)
mac_box.text_frame.paragraphs[0].font.color.rgb = WHITE

# Draw Arrow
arr1 = slide5.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(9.0), Inches(2.5), Inches(0.8), Inches(0.4))
arr1.fill.solid()
arr1.fill.fore_color.rgb = TEAL
arr1.line.fill.background()

# Draw Files API Box
api_box = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.1), Inches(2.2), Inches(2.4), Inches(1.0))
api_box.fill.solid()
api_box.fill.fore_color.rgb = DARK_CARD
api_box.line.color.rgb = TEAL
api_box.text_frame.paragraphs[0].text = "🔌 Databricks Files API\nPOST /api/2.0/fs/files/"
api_box.text_frame.paragraphs[0].font.name = "Arial"
api_box.text_frame.paragraphs[0].font.size = Pt(13)
api_box.text_frame.paragraphs[0].font.color.rgb = WHITE

# Draw Down Arrow
arr2 = slide5.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(11.1), Inches(3.4), Inches(0.4), Inches(0.8))
arr2.fill.solid()
arr2.fill.fore_color.rgb = TEAL
arr2.line.fill.background()

# Draw UC Volume Box (Bottom)
vol_box = slide5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.5), Inches(4.5), Inches(6.0), Inches(1.5))
vol_box.fill.solid()
vol_box.fill.fore_color.rgb = DARK_CARD
vol_box.line.color.rgb = TEAL
vol_box.line.width = Pt(2)
tf_vol = vol_box.text_frame
tf_vol.word_wrap = True
tf_vol.margin_left = Inches(0.2)
tf_vol.margin_top = Inches(0.2)
p_vol = tf_vol.paragraphs[0]
p_vol.text = "📂 Unity Catalog Managed Volume"
p_vol.font.name = "Arial"
p_vol.font.size = Pt(15)
p_vol.font.bold = True
p_vol.font.color.rgb = TEAL

p_vol2 = tf_vol.add_paragraph()
p_vol2.text = "Path: /Volumes/novamart/landing/raw_files/\nStaged as raw CSV and JSON subfolders. Accessible directly via standard Spark API."
p_vol2.font.name = "Arial"
p_vol2.font.size = Pt(12)
p_vol2.font.color.rgb = TEXT_LIGHT
p_vol2.space_before = Pt(6)

# ──────────────────────────────────────────────────────────
# SLIDE 6: STAR SCHEMA SYSTEM (Visual Schema Diagram!)
# ──────────────────────────────────────────────────────────
slide6 = prs.slides.add_slide(slide_layout)
set_slide_background(slide6)
add_slide_header(slide6, "The Serving Gold Star Schema Design", "GOLD SERVINGS")

# Draw Central Fact Box
fact_box = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.8), Inches(3.2), Inches(3.6), Inches(2.2))
fact_box.fill.solid()
fact_box.fill.fore_color.rgb = DARK_CARD
fact_box.line.color.rgb = GOLD_COLOR
fact_box.line.width = Pt(2.5)

tf_f = fact_box.text_frame
tf_f.word_wrap = True
tf_f.margin_top = Inches(0.15)
p_ft = tf_f.paragraphs[0]
p_ft.text = "⭐ fact_sales"
p_ft.alignment = PP_ALIGN.CENTER
p_ft.font.name = "Arial"
p_ft.font.size = Pt(18)
p_ft.font.bold = True
p_ft.font.color.rgb = GOLD_COLOR

p_fc = tf_f.add_paragraph()
p_fc.text = "Grain: Order Item level\nMeasures: Price, Freight, Margin, Quantity\nForeign Keys: customer_key, product_key, seller_key, order_date_key"
p_fc.font.name = "Arial"
p_fc.font.size = Pt(11)
p_fc.font.color.rgb = TEXT_LIGHT
p_fc.space_before = Pt(8)

# Surrounding Dimensions Boxes (4 cards)
dims = [
    {"name": "dim_customer (SCD2)", "pos": (Inches(0.8), Inches(1.8))},
    {"name": "dim_product (SCD2)", "pos": (Inches(9.5), Inches(1.8))},
    {"name": "dim_date (Static)", "pos": (Inches(0.8), Inches(4.8))},
    {"name": "dim_seller (SCD1)", "pos": (Inches(9.5), Inches(4.8))}
]

for dim in dims:
    x, y = dim["pos"]
    d_box = slide6.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, Inches(3.0), Inches(1.2))
    d_box.fill.solid()
    d_box.fill.fore_color.rgb = DARK_CARD
    d_box.line.color.rgb = TEAL
    d_box.line.width = Pt(1.5)
    
    tf_d = d_box.text_frame
    tf_d.word_wrap = True
    p_dt = tf_d.paragraphs[0]
    p_dt.text = dim["name"]
    p_dt.font.name = "Arial"
    p_dt.font.size = Pt(14)
    p_dt.font.bold = True
    p_dt.font.color.rgb = TEAL
    p_dt.alignment = PP_ALIGN.CENTER
    
    p_dc = tf_d.add_paragraph()
    p_dc.text = "Key: surrogate_key\nFields: Conformed metrics"
    p_dc.font.name = "Arial"
    p_dc.font.size = Pt(10)
    p_dc.font.color.rgb = TEXT_MUTED
    p_dc.alignment = PP_ALIGN.CENTER
    p_dc.space_before = Pt(6)

# ──────────────────────────────────────────────────────────
# SLIDE 7: DATA QUALITY GATEWAY (Flowchart)
# ──────────────────────────────────────────────────────────
slide7 = prs.slides.add_slide(slide_layout)
set_slide_background(slide7)
add_slide_header(slide7, "Automated Data Quality & Quarantine Framework", "QUALITY ASSURANCE")

# Draw Flowchart Boxes
# 1. Input Data
ib = slide7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(2.6), Inches(2.2), Inches(1.2))
ib.fill.solid()
ib.fill.fore_color.rgb = DARK_CARD
ib.line.color.rgb = TEXT_MUTED
ib.text_frame.paragraphs[0].text = "Raw Bronze Data\n\nIncoming batch stream"
ib.text_frame.paragraphs[0].font.size = Pt(12)

# Arrow
a1 = slide7.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(3.2), Inches(3.0), Inches(0.6), Inches(0.4))
a1.fill.solid()
a1.fill.fore_color.rgb = TEAL
a1.line.fill.background()

# 2. Check Decision Diamond
cb = slide7.shapes.add_shape(MSO_SHAPE.DIAMOND, Inches(4.1), Inches(2.0), Inches(2.6), Inches(2.4))
cb.fill.solid()
cb.fill.fore_color.rgb = DARK_CARD
cb.line.color.rgb = TEAL
cb.line.width = Pt(2)
cb.text_frame.paragraphs[0].text = "Run DQ Rules\n(Null, Type, Keys)\nPassed?"
cb.text_frame.paragraphs[0].font.size = Pt(11)
cb.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

# True Arrow (Right)
a_true = slide7.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(7.0), Inches(3.0), Inches(0.8), Inches(0.4))
a_true.fill.solid()
a_true.fill.fore_color.rgb = TEAL
a_true.line.fill.background()
tx_yes = slide7.shapes.add_textbox(Inches(7.0), Inches(2.5), Inches(0.8), Inches(0.4))
tx_yes.text_frame.paragraphs[0].text = "YES"
tx_yes.text_frame.paragraphs[0].font.bold = True
tx_yes.text_frame.paragraphs[0].font.color.rgb = TEAL

# 3. Clean Target
target_b = slide7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.1), Inches(2.6), Inches(2.2), Inches(1.2))
target_b.fill.solid()
target_b.fill.fore_color.rgb = DARK_CARD
target_b.line.color.rgb = TEAL
target_b.text_frame.paragraphs[0].text = "🥈 Silver Table\n\nMerge & Ingest"
target_b.text_frame.paragraphs[0].font.size = Pt(12)

# False Arrow (Down)
a_false = slide7.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(5.2), Inches(4.6), Inches(0.4), Inches(0.8))
a_false.fill.solid()
a_false.fill.fore_color.rgb = RED_ACCENT
a_false.line.fill.background()
tx_no = slide7.shapes.add_textbox(Inches(5.7), Inches(4.7), Inches(0.8), Inches(0.4))
tx_no.text_frame.paragraphs[0].text = "NO"
tx_no.text_frame.paragraphs[0].font.bold = True
tx_no.text_frame.paragraphs[0].font.color.rgb = RED_ACCENT

# 4. Quarantine Box (Bottom)
q_b = slide7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.1), Inches(5.6), Inches(2.6), Inches(1.0))
q_b.fill.solid()
q_b.fill.fore_color.rgb = DARK_CARD
q_b.line.color.rgb = RED_ACCENT
q_b.text_frame.paragraphs[0].text = "⚠️ Quarantine Table\nFlag for alerting/review"
q_b.text_frame.paragraphs[0].font.size = Pt(12)

# ──────────────────────────────────────────────────────────
# SLIDE 8: CDC & SCD (SLOWLY CHANGING DIMENSIONS)
# ──────────────────────────────────────────────────────────
slide8 = prs.slides.add_slide(slide_layout)
set_slide_background(slide8)
add_slide_header(slide8, "CDC & Slowly Changing Dimensions (SCD)", "DATA TRANSFORMATIONS")

# Left Column (SCD Type 1)
box_scd1 = slide8.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
box_scd1.fill.solid()
box_scd1.fill.fore_color.rgb = DARK_CARD
box_scd1.line.color.rgb = TEAL
box_scd1.line.width = Pt(1.5)

tf_s1 = box_scd1.text_frame
tf_s1.word_wrap = True
tf_s1.margin_left = Inches(0.3)
tf_s1.margin_top = Inches(0.3)

p_s1 = tf_s1.paragraphs[0]
p_s1.text = "🔄 SCD Type 1: Overwrite"
p_s1.font.size = Pt(18)
p_s1.font.bold = True
p_s1.font.color.rgb = TEAL
p_s1.space_after = Pt(10)

s1_bullets = [
    "Concept: Updates overwrite existing records. No history is kept.",
    "Used for: Reference/lookup data where history is not analytical (e.g. store details, category English translations, merchant details).",
    "Implementation: PySpark MERGE statement updates matching records and inserts new ones.",
    "Saves storage and retains simple schema relationships."
]
for b in s1_bullets:
    p = tf_s1.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_LIGHT
    p.space_after = Pt(10)

# Right Column (SCD Type 2)
box_scd2 = slide8.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8))
box_scd2.fill.solid()
box_scd2.fill.fore_color.rgb = DARK_CARD
box_scd2.line.color.rgb = GOLD_COLOR
box_scd2.line.width = Pt(1.5)

tf_s2 = box_scd2.text_frame
tf_s2.word_wrap = True
tf_s2.margin_left = Inches(0.3)
tf_s2.margin_top = Inches(0.3)

p_s2 = tf_s2.paragraphs[0]
p_s2.text = "🕰️ SCD Type 2: Historical Versioning"
p_s2.font.size = Pt(18)
p_s2.font.bold = True
p_s2.font.color.rgb = GOLD_COLOR
p_s2.space_after = Pt(10)

s2_bullets = [
    "Concept: Creates a new row for each change, retaining version history.",
    "Used for: Core master data (customers, products, employees).",
    "Key Columns Added: effective_start_date, effective_end_date, is_current (true/false).",
    "Implementation: Perform update on old records (set current=false, end_date=now) and insert the new row.",
    "Critical for accurate point-in-time sales analysis."
]
for b in s2_bullets:
    p = tf_s2.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_LIGHT
    p.space_after = Pt(10)

# ──────────────────────────────────────────────────────────
# SLIDE 9: OPERATIONAL MONITORS & AUDITS
# ──────────────────────────────────────────────────────────
slide9 = prs.slides.add_slide(slide_layout)
set_slide_background(slide9)
add_slide_header(slide9, "Operational Audit & Monitoring Framework", "OBSERVABILITY")

# List of 5 Audit Tables (Grid style)
audits = [
    {"name": "log_pipeline_execution", "desc": "Logs start/end, status, duration, and error codes for every notebook run.", "col": TEAL},
    {"name": "log_dq_results", "desc": "Tracks checks run, records passed/failed, and overall table quality scores.", "col": TEAL},
    {"name": "log_reconciliation", "desc": "SOX-compliant count/sum control comparisons from source to destination.", "col": TEAL},
    {"name": "log_cdc_tracking", "desc": "Monitors insert, update, and delete volume to detect batch anomalies.", "col": TEAL},
    {"name": "watermark_tracking", "desc": "Maintains offsets/timestamps to enable safe incremental pipeline restarts.", "col": TEAL}
]

y_pos = Inches(1.8)
for audit in audits:
    # Color bar
    bar = slide9.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y_pos, Inches(0.15), Inches(0.8))
    bar.fill.solid()
    bar.fill.fore_color.rgb = audit["col"]
    bar.line.fill.background()
    
    # Text
    tx_a = slide9.shapes.add_textbox(Inches(1.1), y_pos - Inches(0.1), Inches(11.4), Inches(0.8))
    tf_a = tx_a.text_frame
    p_at = tf_a.paragraphs[0]
    p_at.text = audit["name"]
    p_at.font.name = "Arial"
    p_at.font.size = Pt(16)
    p_at.font.bold = True
    p_at.font.color.rgb = WHITE
    
    p_ad = tf_a.add_paragraph()
    p_ad.text = audit["desc"]
    p_ad.font.name = "Arial"
    p_ad.font.size = Pt(12)
    p_ad.font.color.rgb = TEXT_LIGHT
    p_ad.space_before = Pt(2)
    
    y_pos += Inches(1.0)

# ──────────────────────────────────────────────────────────
# SLIDE 10: ROADMAP — 9 MILESTONES
# ──────────────────────────────────────────────────────────
slide10 = prs.slides.add_slide(slide_layout)
set_slide_background(slide10)
add_slide_header(slide10, "9-Milestone Progression Roadmap", "ROADMAP")

# Draw Milestone timeline (3 columns x 3 rows)
milestones = [
    {"num": "M1", "name": "Environment Setup", "lvl": "Junior", "col": BRONZE_COLOR},
    {"num": "M2", "name": "Synthetic Data", "lvl": "Junior", "col": BRONZE_COLOR},
    {"num": "M3", "name": "Bronze Ingestion", "lvl": "Junior", "col": BRONZE_COLOR},
    {"num": "M4", "name": "Silver Cleaning", "lvl": "Mid", "col": SILVER_COLOR},
    {"num": "M5", "name": "Gold Star Schema", "lvl": "Mid", "col": SILVER_COLOR},
    {"num": "M6", "name": "Advanced SQL", "lvl": "Senior", "col": GOLD_COLOR},
    {"num": "M7", "name": "Orchestration", "lvl": "Senior", "col": GOLD_COLOR},
    {"num": "M8", "name": "Query Tuning", "lvl": "Lead", "col": TEAL},
    {"num": "M9", "name": "Production Suite", "lvl": "Architect", "col": TEAL}
]

grid_positions = [
    (Inches(0.8), Inches(1.8)), (Inches(4.8), Inches(1.8)), (Inches(8.8), Inches(1.8)),
    (Inches(0.8), Inches(3.4)), (Inches(4.8), Inches(3.4)), (Inches(8.8), Inches(3.4)),
    (Inches(0.8), Inches(5.0)), (Inches(4.8), Inches(5.0)), (Inches(8.8), Inches(5.0))
]

for idx, m in enumerate(milestones):
    x, y = grid_positions[idx]
    
    # Milestone card
    card = slide10.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, Inches(3.7), Inches(1.2))
    card.fill.solid()
    card.fill.fore_color.rgb = DARK_CARD
    card.line.color.rgb = m["col"]
    card.line.width = Pt(1.5)
    
    tf_m = card.text_frame
    tf_m.word_wrap = True
    tf_m.margin_left = Inches(0.15)
    tf_m.margin_top = Inches(0.15)
    
    p_mt = tf_m.paragraphs[0]
    p_mt.text = f"{m['num']}: {m['name']}"
    p_mt.font.name = "Arial"
    p_mt.font.size = Pt(14)
    p_mt.font.bold = True
    p_mt.font.color.rgb = WHITE
    
    p_ml = tf_m.add_paragraph()
    p_ml.text = f"Level: {m['lvl']}"
    p_ml.font.name = "Arial"
    p_ml.font.size = Pt(11)
    p_ml.font.color.rgb = m["col"]
    p_ml.space_before = Pt(4)

# ──────────────────────────────────────────────────────────
# SLIDE 11: NEXT STEPS & ACTION ITEMS
# ──────────────────────────────────────────────────────────
slide11 = prs.slides.add_slide(slide_layout)
set_slide_background(slide11)
add_slide_header(slide11, "Roadmap: Immediate Actions & Next Steps", "ACTION PLAN")

# Centered Next Steps Card
ns_card = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.6), Inches(1.8), Inches(8.0), Inches(4.5))
ns_card.fill.solid()
ns_card.fill.fore_color.rgb = DARK_CARD
ns_card.line.color.rgb = TEAL
ns_card.line.width = Pt(2)

tf_ns = ns_card.text_frame
tf_ns.word_wrap = True
tf_ns.margin_left = Inches(0.4)
tf_ns.margin_right = Inches(0.4)
tf_ns.margin_top = Inches(0.4)

p_nst = tf_ns.paragraphs[0]
p_nst.text = "🎯 Executing Milestone 3: Bronze Ingestion"
p_nst.font.name = "Arial"
p_nst.font.size = Pt(20)
p_nst.font.bold = True
p_nst.font.color.rgb = TEAL
p_nst.space_after = Pt(14)

ns_bullets = [
    "Run Environment Setup: Open 00_environment_setup notebook in Databricks and run it to prepare the schemas and audit framework.",
    "Verify Raw Files: Run 01_data_upload_guide to confirm all 15 source datasets are correctly located in the landing volume.",
    "Begin Bronze Ingestion Code: Design and implement the generic, config-driven ingestion notebook that reads config from Git and automatically appends metadata and registers Delta tables.",
    "Configure Watermarking: Establish watermark checks in the pipeline so it only loads new files, matching standard production designs."
]
for b in ns_bullets:
    p = tf_ns.add_paragraph()
    p.text = "👉 " + b
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_LIGHT
    p.space_after = Pt(12)

# Save presentation
target_path = "/Users/rhitambhaduri/Desktop/NovaBazaar_Enterprise_Architecture.pptx"
prs.save(target_path)
print(f"🎉 Presentation saved successfully to: {target_path}")
