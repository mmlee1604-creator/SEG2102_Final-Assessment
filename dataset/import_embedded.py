
import json
from collections import defaultdict
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Select embedded database
db = client["ecommerce_embedded"]

# Read orders.json
with open("orders.json", "r", encoding="utf-8") as file:
    orders = json.load(file)

# Read orderItems.json
with open("orderItems.json", "r", encoding="utf-8") as file:
    order_items = json.load(file)

# Group order items by OrderID
items_by_order = defaultdict(list)

for item in order_items:
    order_id = item["OrderID"]

    # Keep the original order item fields,
    # but remove OrderID because it is no longer needed inside Items
    embedded_item = {
        key: value
        for key, value in item.items()
        if key != "OrderID"
    }

    items_by_order[order_id].append(embedded_item)

# Add Items array to each order
for order in orders:
    order["Items"] = items_by_order[order["OrderID"]]

# Import into MongoDB
db.orders.drop()

if orders:
    db.orders.insert_many(orders)

print(f"Successfully imported {len(orders)} orders.")
print(f"Embedded {len(order_items)} order items.")
