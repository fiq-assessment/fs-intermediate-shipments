from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.db import init_db
from .routers import shipments

app = FastAPI(
    title="Shipments Management API",
    version="1.0.0",
    description="FS Intermediate: Shipments + CSV Import"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(shipments.router)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/health")
async def health():
    return {"ok": True, "service": "shipments-api"}

@app.get("/facilities")
async def list_facilities():
    """Get all facilities"""
    from .core.db import db
    cursor = db.facilities.find()
    facilities = []
    async for doc in cursor:
        facilities.append({
            "id": str(doc["_id"]),
            "code": doc["code"],
            "name": doc["name"]
        })
    return {"items": facilities}

