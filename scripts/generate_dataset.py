"""Generate synthetic data for the Customer/Product/Orders/OrderItem ERD.

Run from the project root:  python scripts/generate_dataset.py
Output: dataset/customers.json, products.json, orders.json, orderItems.json
"""
import json
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 2102
N_CUSTOMERS, N_PRODUCTS, N_ORDERS, N_ITEMS = 10_000, 1_000, 10_000, 40_000
MAX_ITEMS_PER_ORDER = 8

random.seed(SEED)
OUT = Path(__file__).resolve().parent.parent / "dataset"

FIRST = ["Ahmad", "Siti", "Muhammad", "Nur", "Lee", "Tan", "Wong", "Lim", "Chong", "Ng",
         "Raj", "Kumar", "Priya", "Aisyah", "Farid", "Hana", "Daniel", "Sarah", "Jason",
         "Emily", "Kevin", "Mei", "Wei", "Jia", "Arif", "Zulkifli", "Devi", "Anand",
         "Amir", "Nadia", "Irfan", "Lina", "Haziq", "Syafiq", "Aina", "Ben", "Chloe"]
LAST = ["Abdullah", "Rahman", "Ismail", "Hassan", "Ibrahim", "Tan", "Lim", "Lee", "Wong",
        "Chan", "Ong", "Goh", "Teo", "Yap", "Krishnan", "Nair", "Pillai", "Singh",
        "Lau", "Chew", "Hashim", "Yusof", "Ali", "Omar", "Razak", "Kamal", "Lai", "Foo"]
STREETS = ["Jalan Bukit Bintang", "Jalan Ampang", "Jalan Tun Razak", "Jalan SS2/24",
           "Jalan Kenanga", "Jalan Mawar", "Jalan Melati", "Lorong Maarof", "Jalan Pantai",
           "Jalan Universiti", "Jalan Damai", "Jalan Setia", "Jalan Perdana", "Jalan Bayu"]
AREAS = [("Kuala Lumpur", "Wilayah Persekutuan", "50450"), ("Petaling Jaya", "Selangor", "47300"),
         ("Subang Jaya", "Selangor", "47500"), ("Shah Alam", "Selangor", "40000"),
         ("George Town", "Penang", "10200"), ("Johor Bahru", "Johor", "80000"),
         ("Ipoh", "Perak", "30000"), ("Melaka", "Melaka", "75000"),
         ("Kuching", "Sarawak", "93000"), ("Kota Kinabalu", "Sabah", "88000"),
         ("Seremban", "Negeri Sembilan", "70000"), ("Kuantan", "Pahang", "25000")]
DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "mail.com"]

# category -> (price range, product name pool)
CATALOG = {
    "Electronics": ((29, 4500), ["Wireless Mouse", "Mechanical Keyboard", "Bluetooth Speaker", "USB-C Hub",
                                 "Webcam HD", "Power Bank", "Smart Watch", "Noise Cancelling Headphones",
                                 "Portable SSD", "Monitor 24 inch", "Tablet", "Gaming Headset"]),
    "Clothing": ((15, 400), ["Cotton T-Shirt", "Slim Fit Jeans", "Hoodie", "Baju Kurung", "Polo Shirt",
                             "Running Shorts", "Rain Jacket", "Casual Dress", "Sports Socks", "Cap"]),
    "Home & Kitchen": ((10, 1200), ["Rice Cooker", "Air Fryer", "Blender", "Non-Stick Pan", "Knife Set",
                                    "Vacuum Flask", "Storage Box", "Electric Kettle", "Dinner Set", "Desk Lamp"]),
    "Books": ((12, 150), ["Database Systems Textbook", "Python Programming Guide", "Novel Collection",
                          "Cookbook", "Business Strategy Handbook", "Children Storybook", "History Atlas",
                          "Self-Help Journal"]),
    "Sports": ((20, 900), ["Yoga Mat", "Badminton Racket", "Football", "Dumbbell Set", "Skipping Rope",
                           "Cycling Helmet", "Tennis Racket", "Swimming Goggles", "Resistance Bands"]),
    "Beauty": ((8, 350), ["Face Moisturizer", "Sunscreen SPF50", "Lipstick", "Shampoo", "Perfume",
                          "Face Wash", "Hair Serum", "Body Lotion", "Eau de Toilette"]),
    "Toys": ((10, 500), ["Building Blocks", "Remote Control Car", "Puzzle Set", "Board Game",
                         "Plush Bear", "Art Kit", "Toy Train", "Action Figure"]),
    "Groceries": ((3, 120), ["Basmati Rice 5kg", "Olive Oil", "Instant Noodles Pack", "Coffee Beans",
                             "Green Tea Box", "Honey Jar", "Oat Cereal", "Dark Chocolate"]),
}
ADJ = ["Pro", "Lite", "Max", "Plus", "Classic", "Premium", "Eco", "Ultra", "Mini", "Deluxe"]
STATUSES = ["Pending", "Processing", "Shipped"]
STATUS_WEIGHTS = [0.25, 0.30, 0.45]


def write(name, rows):
    with open(OUT / name, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
        f.write("\n")


def make_customers():
    rows, used = [], set()
    for i in range(1, N_CUSTOMERS + 1):
        first, last = random.choice(FIRST), random.choice(LAST)
        name = f"{first} {last}"
        email = f"{first}.{last}{i}@{random.choice(DOMAINS)}".lower()
        city, state, postcode = random.choice(AREAS)
        address = (f"{random.randint(1, 250)}, {random.choice(STREETS)}, "
                   f"{postcode} {city}, {state}")
        contact = f"+601{random.choice('0123456789')}{random.randint(0, 9999999):07d}"
        assert email not in used
        used.add(email)
        rows.append({"CustomerID": f"C{i:05d}", "Name": name, "Email": email,
                     "ContactNo": contact, "Address": address})
    return rows


def make_products():
    rows, used = [], set()
    cats = list(CATALOG)
    for i in range(1, N_PRODUCTS + 1):
        cat = cats[(i - 1) % len(cats)]
        (lo, hi), names = CATALOG[cat]
        while True:
            pname = f"{random.choice(names)} {random.choice(ADJ)} {random.randint(100, 999)}"
            if pname not in used:
                used.add(pname)
                break
        # skewed toward lower prices, ends in .90 / .00 / random cents
        price = round(lo + (hi - lo) * random.random() ** 2.5, 2)
        rows.append({"ProductID": f"P{i:04d}", "ProductName": pname, "Category": cat,
                     "Price": max(price, 0.01)})
    return rows


def make_orders(customers):
    start, end = date(2023, 1, 1), date(2025, 12, 31)
    span = (end - start).days
    rows = []
    for i in range(1, N_ORDERS + 1):
        rows.append({
            "OrderID": f"O{i:05d}",
            "CustomerID": random.choice(customers)["CustomerID"],
            "OrderDate": (start + timedelta(days=random.randint(0, span))).isoformat(),
            "Status": random.choices(STATUSES, STATUS_WEIGHTS)[0],
        })
    return rows


def make_items(orders, products):
    # every order gets 1 item, then the remaining items are spread randomly
    counts = [1] * N_ORDERS
    open_slots = list(range(N_ORDERS))
    for _ in range(N_ITEMS - N_ORDERS):
        k = random.randrange(len(open_slots))
        idx = open_slots[k]
        counts[idx] += 1
        if counts[idx] >= MAX_ITEMS_PER_ORDER:
            open_slots[k] = open_slots[-1]
            open_slots.pop()
    rows, n = [], 0
    for order, cnt in zip(orders, counts):
        for prod in random.sample(products, cnt):  # no duplicate product in one order
            n += 1
            qty = random.choices([1, 2, 3, 4, 5, 6, 10], [45, 25, 12, 8, 5, 3, 2])[0]
            rows.append({
                "OrderItemID": f"I{n:05d}",
                "OrderID": order["OrderID"],
                "ProductID": prod["ProductID"],
                "Quantity": qty,
                "Subtotal": round(prod["Price"] * qty, 2),  # Product.Price x Quantity
            })
    return rows


def validate(customers, products, orders, items):
    assert (len(customers), len(products), len(orders), len(items)) == (
        N_CUSTOMERS, N_PRODUCTS, N_ORDERS, N_ITEMS)
    cids = {c["CustomerID"] for c in customers}
    pids = {p["ProductID"] for p in products}
    oids = {o["OrderID"] for o in orders}
    assert all(o["CustomerID"] in cids for o in orders)
    assert all(i["OrderID"] in oids and i["ProductID"] in pids for i in items)
    assert {i["OrderID"] for i in items} == oids
    assert all(len(c["CustomerID"]) == 6 and len(c["Email"]) <= 50 and len(c["Name"]) <= 50
               and len(c["ContactNo"]) <= 15 and len(c["Address"]) <= 100 for c in customers)
    assert all(len(p["ProductID"]) == 5 and len(p["ProductName"]) <= 50 and p["Price"] > 0
               and p["Price"] < 10**8 for p in products)
    price = {p["ProductID"]: p["Price"] for p in products}
    assert all(i["Subtotal"] == round(price[i["ProductID"]] * i["Quantity"], 2) for i in items)
    assert all(len(o["OrderID"]) == 6 and o["Status"] in STATUSES for o in orders)
    assert all(len(i["OrderItemID"]) == 6 and i["Quantity"] > 0 and i["Subtotal"] > 0
               for i in items)


def main():
    OUT.mkdir(exist_ok=True)
    customers = make_customers()
    products = make_products()
    orders = make_orders(customers)
    items = make_items(orders, products)
    validate(customers, products, orders, items)
    write("customers.json", customers)
    write("products.json", products)
    write("orders.json", orders)
    write("orderItems.json", items)
    print(f"customers={len(customers)} products={len(products)} "
          f"orders={len(orders)} orderItems={len(items)}")


if __name__ == "__main__":
    main()
