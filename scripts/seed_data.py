"""
Seed script to populate the NovaGear database with test customers and realistic orders.
Tests order tracking, return eligibility (both within and past 30 days), and delivery estimates.
"""
from datetime import date, timedelta
from db.db import SessionLocal
from db.db_model import Customer, Order

def seed_database():
    db = SessionLocal()
    today = date.today()

    try:
        print("🌱 Seeding customers and orders...")

        # 1. Customers
        customer_data = [
            {"name": "Rahul", "email": "rahulrajesh@gmail.com"},
            {"name": "Sarah Chen", "email": "sarah.chen@example.com"},
            {"name": "Marcus Vance", "email": "marcus.vance@example.com"},
            {"name": "Elena Rostova", "email": "elena.rostova@example.com"},
        ]

        customer_map = {}
        for c_data in customer_data:
            existing = db.query(Customer).filter(Customer.email == c_data["email"]).first()
            if not existing:
                cust = Customer(name=c_data["name"], email=c_data["email"])
                db.add(cust)
                db.flush()
                customer_map[c_data["email"]] = cust
                print(f"  + Added customer: {cust.name} (ID: {cust.id})")
            else:
                customer_map[c_data["email"]] = existing
                print(f"  • Existing customer: {existing.name} (ID: {existing.id})")

        # 2. Orders with diverse test scenarios
        rahul = customer_map["rahulrajesh@gmail.com"]
        sarah = customer_map["sarah.chen@example.com"]
        marcus = customer_map["marcus.vance@example.com"]
        elena = customer_map["elena.rostova@example.com"]

        orders_data = [
            # Rahul's orders:
            {
                "customer_id": rahul.id,
                "order_number": "ORD-9021",
                "item_name": "NovaBuds Pro 2",
                "amount": 189.00,
                "status": "delivered",
                "shipping_tier": "express",
                "date": today - timedelta(days=5),  # 5 days ago -> Eligible for return!
            },
            {
                "customer_id": rahul.id,
                "order_number": "ORD-7814",
                "item_name": "ErgoChair Pro",
                "amount": 429.00,
                "status": "delivered",
                "shipping_tier": "standard",
                "date": today - timedelta(days=45),  # 45 days ago -> Past 30 days return window!
            },
            {
                "customer_id": rahul.id,
                "order_number": "ORD-9430",
                "item_name": "NovaBeam Monitor Lightbar",
                "amount": 79.00,
                "status": "processing",
                "shipping_tier": "standard",
                "date": today,  # Today -> In progress, delivery estimate
            },

            # Sarah's orders:
            {
                "customer_id": sarah.id,
                "order_number": "ORD-8842",
                "item_name": "MetroPack 25L Backpack",
                "amount": 139.00,
                "status": "shipped",
                "shipping_tier": "express",
                "date": today - timedelta(days=1),
            },

            # Marcus's orders:
            {
                "customer_id": marcus.id,
                "order_number": "ORD-6520",
                "item_name": "NovaSense Smart Hub",
                "amount": 149.00,
                "status": "cancelled",
                "shipping_tier": "standard",
                "date": today - timedelta(days=10),
            },

            # Elena's orders:
            {
                "customer_id": elena.id,
                "order_number": "ORD-5109",
                "item_name": "NovaPower 65W GaN Charger",
                "amount": 49.00,
                "status": "refunded",
                "shipping_tier": "standard",
                "date": today - timedelta(days=20),
            },
        ]

        for o_data in orders_data:
            existing = db.query(Order).filter(Order.order_number == o_data["order_number"]).first()
            if not existing:
                order = Order(**o_data)
                db.add(order)
                print(f"  + Added order #{order.order_number}: {order.item_name} for Customer ID {order.customer_id}")
            else:
                print(f"  • Existing order #{existing.order_number}")

        db.commit()
        print("\n✅ Seeding complete!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
