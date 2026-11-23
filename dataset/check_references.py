
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

embedded = client["ecommerce_embedded"]
referenced = client["ecommerce_referenced"]


def check_reference(name, child_collection, child_field,
                    parent_collection, parent_field):

    # Get all parent IDs
    parent_ids = set(
        parent_collection.distinct(parent_field)
    )

    # Find child documents with missing references
    total = child_collection.count_documents({})

    invalid = child_collection.count_documents({
        child_field: {"$nin": list(parent_ids)}
    })

    print(f"\n{name}")
    print(f"Total records: {total}")
    print(f"Invalid references: {invalid}")

    if invalid == 0:
        print("Result: PASS")
    else:
        print("Result: FAIL")


print("========== REFERENCED MODEL ==========")

# Orders -> Customers
check_reference(
    "Orders -> Customers",
    referenced.orders,
    "CustomerID",
    referenced.customers,
    "CustomerID"
)

# OrderItems -> Orders
check_reference(
    "OrderItems -> Orders",
    referenced.orderItems,
    "OrderID",
    referenced.orders,
    "OrderID"
)

# OrderItems -> Products
check_reference(
    "OrderItems -> Products",
    referenced.orderItems,
    "ProductID",
    referenced.products,
    "ProductID"
)


print("\n========== EMBEDDED MODEL ==========")

# Orders -> Customers
check_reference(
    "Orders -> Customers",
    embedded.orders,
    "CustomerID",
    embedded.customers,
    "CustomerID"
)

# Embedded Items -> Products
# First, collect all ProductIDs from embedded items

embedded_product_ids = set(
    embedded.products.distinct("ProductID")
)

invalid_items = 0
total_items = 0

for order in embedded.orders.find({}, {"Items": 1}):
    for item in order.get("Items", []):
        total_items += 1

        if item.get("ProductID") not in embedded_product_ids:
            invalid_items += 1

print("\nEmbedded Items -> Products")
print(f"Total records: {total_items}")
print(f"Invalid references: {invalid_items}")

if invalid_items == 0:
    print("Result: PASS")
else:
    print("Result: FAIL")

client.close()
