# NovaBazaar Data Dictionary

This document details the schema definitions for all 15 source files ingested into the NovaBazaar Lakehouse.

## 1. Olist E-Commerce Data (Core Sources)

### `olist_orders`
| Column | Type | Description | Primary/Foreign Key |
|---|---|---|---|
| `order_id` | STRING | Unique identifier of the order | PK |
| `customer_id` | STRING | Key linking to the customer record | FK |
| `order_status` | STRING | Current status of the order (delivered, shipped, etc.) | - |
| `order_purchase_timestamp` | TIMESTAMP | Timestamp of the purchase | - |
| `order_approved_at` | TIMESTAMP | Timestamp of payment approval | - |
| `order_delivered_carrier_date` | TIMESTAMP | Date carrier picked up order | - |
| `order_delivered_customer_date`| TIMESTAMP | Date customer received order | - |
| `order_estimated_delivery_date`| TIMESTAMP | Estimated delivery date | - |

### `olist_order_items`
| Column | Type | Description | Primary/Foreign Key |
|---|---|---|---|
| `order_id` | STRING | Unique identifier of the order | PK, FK |
| `order_item_id` | INT | Sequential item identifier within order | PK |
| `product_id` | STRING | Unique product identifier | FK |
| `seller_id` | STRING | Unique seller identifier | FK |
| `shipping_limit_date` | TIMESTAMP | Seller shipping deadline date | - |
| `price` | DOUBLE | Selling price of item | - |
| `freight_value` | DOUBLE | Shipping cost | - |

### `olist_order_payments`
| Column | Type | Description | Primary/Foreign Key |
|---|---|---|---|
| `order_id` | STRING | Unique identifier of the order | PK, FK |
| `payment_sequential` | INT | Payment sequence identifier | PK |
| `payment_type` | STRING | Payment method (credit_card, boleto, voucher, debit_card) | - |
| `payment_installments` | INT | Selected payment installments | - |
| `payment_value` | DOUBLE | Transaction value paid | - |

### `olist_order_reviews`
| Column | Type | Description | Primary/Foreign Key |
|---|---|---|---|
| `review_id` | STRING | Unique identifier of review | PK |
| `order_id` | STRING | Unique identifier of order | FK |
| `review_score` | INT | Score rating 1 to 5 | - |
| `review_comment_title` | STRING | Customer feedback title | - |
| `review_comment_message` | STRING | Detail message feedback | - |
| `review_creation_date` | TIMESTAMP | Review creation timestamp | - |
| `review_answer_timestamp` | TIMESTAMP | Review reply timestamp | - |

### `olist_customers`
| Column | Type | Description | Primary/Foreign Key |
|---|---|---|---|
| `customer_id` | STRING | Unique customer token (per transaction) | PK |
| `customer_unique_id` | STRING | Permanent unique identifier of customer | - |
| `customer_zip_code_prefix`| INT | Shipping postal code prefix | FK |
| `customer_city` | STRING | Customer city | - |
| `customer_state` | STRING | Customer state code | - |

### `olist_products`
| Column | Type | Description | Primary/Foreign Key |
|---|---|---|---|
| `product_id` | STRING | Unique product identifier | PK |
| `product_category_name` | STRING | Category name in Portuguese | FK |
| `product_name_lenght` | INT | Name length in chars | - |
| `product_description_lenght`| INT | Description length in chars | - |
| `product_photos_qty` | INT | Count of product images | - |
| `product_weight_g` | INT | Product weight in grams | - |
| `product_length_cm` | INT | Product length in centimeters | - |
| `product_height_cm` | INT | Product height in centimeters | - |
| `product_width_cm` | INT | Product width in centimeters | - |

### `olist_sellers`
| Column | Type | Description | Primary/Foreign Key |
|---|---|---|---|
| `seller_id` | STRING | Unique seller identifier | PK |
| `seller_zip_code_prefix` | INT | Seller postal prefix | FK |
| `seller_city` | STRING | Seller city | - |
| `seller_state` | STRING | Seller state code | - |

### `olist_geolocation`
| Column | Type | Description | Primary/Foreign Key |
|---|---|---|---|
| `geolocation_zip_code_prefix`| INT | Postal code prefix | PK |
| `geolocation_lat` | DOUBLE | Latitude coord | - |
| `geolocation_lng` | DOUBLE | Longitude coord | - |
| `geolocation_city` | STRING | Geolocation city | - |
| `geolocation_state` | STRING | Geolocation state code | - |

### `product_category_name_translation`
| Column | Type | Description | Primary/Foreign Key |
|---|---|---|---|
| `product_category_name` | STRING | Name in Portuguese | PK, FK |
| `product_category_name_english`| STRING | Translated English name | - |

---

## 2. Synthetic Enterprise Augmentations

### `employees` (HR Domain)
| Column | Type | Description | Primary/Foreign Key |
|---|---|---|---|
| `employee_id` | STRING | Unique staff identifier | PK |
| `first_name` | STRING | First name | - |
| `last_name` | STRING | Last name | - |
| `email` | STRING | Corporate email | - |
| `position` | STRING | Job title | - |
| `department` | STRING | Corporate department | - |
| `salary` | DOUBLE | Monthly wage | - |
| `hire_date` | DATE | Hire date | - |
| `manager_id` | STRING | Manager's employee ID | FK |
| `is_active` | BOOLEAN | Operational active flag | - |
| `modified_date` | TIMESTAMP | Last updated time | - |

### `general_ledger` (Finance Domain)
| Column | Type | Description | Primary/Foreign Key |
|---|---|---|---|
| `entry_id` | STRING | Unique journal entry ID | PK |
| `order_id` | STRING | Associated order | FK |
| `posting_date` | DATE | Ledger post date | - |
| `account_code` | STRING | General Ledger Account Code | - |
| `debit_amount` | DOUBLE | Debit value | - |
| `credit_amount` | DOUBLE | Credit value | - |
| `cost_center` | STRING | Department or category cost center | - |

### `inventory_snapshots` (Inventory Domain)
| Column | Type | Description | Primary/Foreign Key |
|---|---|---|---|
| `product_id` | STRING | Product reference | PK, FK |
| `snapshot_date` | DATE | Date of record snapshot | PK |
| `quantity_on_hand` | INT | In-stock quantity count | - |
| `quantity_on_order` | INT | Scheduled replenishment count | - |
| `reorder_point` | INT | Stock level trigger to reorder | - |
| `reorder_qty` | INT | Standard batch order qty | - |

### `marketing_campaigns` (Marketing Domain)
| Column | Type | Description | Primary/Foreign Key |
|---|---|---|---|
| `campaign_id` | STRING | Campaign reference | PK |
| `campaign_name` | STRING | Campaign name | - |
| `channel` | STRING | Media channel (email, social, ad) | - |
| `start_date` | DATE | Start date | - |
| `end_date` | DATE | Close date | - |
| `budget` | DOUBLE | Campaign budget spend | - |

### `promotions` (Marketing Domain)
| Column | Type | Description | Primary/Foreign Key |
|---|---|---|---|
| `promotion_id` | STRING | Unique promo code | PK |
| `promo_name` | STRING | Customer-facing promo name | - |
| `discount_pct` | DOUBLE | Percent deduction | - |
| `start_date` | DATE | Offer start | - |
| `end_date` | DATE | Offer end | - |
| `is_active` | BOOLEAN | Current status flag | - |
| `modified_date` | TIMESTAMP | Last updated time | - |

### `exchange_rates` (Finance Domain)
| Column | Type | Description | Primary/Foreign Key |
|---|---|---|---|
| `date` | DATE | Exchange rate date | PK |
| `currency` | STRING | Currency code (USD, EUR) | PK |
| `rate_to_brl` | DOUBLE | Convert multiplier to BRL | - |
