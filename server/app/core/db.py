from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

client = AsyncIOMotorClient(settings.MONGODB_URI)
db = client[settings.DB_NAME]

async def init_db():
    """Initialize database indexes"""
    await db.shipments.create_index([("facilityId", 1)])
    await db.shipments.create_index([("status", 1)])
    await db.shipments.create_index([("createdAt", -1)])
    await db.shipments.create_index([("poNumber", 1)])
    await db.facilities.create_index([("code", 1)], unique=True)
    print("✓ Database indexes created")

