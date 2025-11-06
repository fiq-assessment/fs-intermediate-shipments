"""Seed database"""
import asyncio
from datetime import datetime, timedelta
import random
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URI = "mongodb://fiqtestuser:F9dAd0e0w!!%40@mysql1.interview.servers.fulfillmentiq.com:27017/fiqtest?authMechanism=SCRAM-SHA-1&authSource=admin"
DB_NAME = "fiqtest"

FACILITIES = [
    ("WH-01", "Main Warehouse"),
    ("WH-02", "Secondary Warehouse"),
    ("DC-01", "Distribution Center East"),
    ("DC-02", "Distribution Center West")
]

PRODUCTS = [
    ("SKU-001", "Widget A"),
    ("SKU-002", "Widget B"),
    ("SKU-003", "Gadget X"),
    ("SKU-004", "Tool Y")
]

async def seed_data():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    
    # Clear
    await db.facilities.delete_many({})
    await db.shipments.delete_many({})
    
    # Create facilities
    facilities = []
    for code, name in FACILITIES:
        result = await db.facilities.insert_one({"code": code, "name": name})
        facilities.append({"id": str(result.inserted_id), "code": code, "name": name})
    
    print(f"✓ Created {len(facilities)} facilities")
    
    # Create shipments
    statuses = ["pending", "in_transit", "delivered"]
    for i in range(50):
        facility = random.choice(facilities)
        items = []
        for _ in range(random.randint(1, 3)):
            code, name = random.choice(PRODUCTS)
            items.append({
                "productCode": code,
                "productName": name,
                "quantity": random.randint(1, 100)
            })
        
        await db.shipments.insert_one({
            "facilityId": facility["id"],
            "facilityName": facility["name"],
            "poNumber": f"PO-{1000 + i}",
            "status": random.choice(statuses),
            "items": items,
            "createdAt": datetime.utcnow() - timedelta(days=random.randint(0, 30))
        })
    
    print(f"✓ Created 50 shipments")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_data())

