from fastapi import APIRouter, HTTPException, UploadFile, File
from ..core.db import db, client
from ..models.shipment import ShipmentOut, BulkItemUpdate
from bson import ObjectId
from datetime import datetime
import base64
import csv
import io

router = APIRouter(prefix="/shipments", tags=["shipments"])

# EXPECTATION:
# - Cursor-based pagination
# - Multi-criteria filtering (status, facilityId, dates, PO)
# - Bulk updates with MongoDB transactions
# - CSV import with validation

@router.get("")
async def list_shipments(
    cursor: str | None = None,
    limit: int = 20,
    status: str | None = None,
    facilityId: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    po: str | None = None
):
    """List shipments with filtering and cursor pagination"""
    query = {}
    
    # Filters
    if status:
        query["status"] = status
    if facilityId:
        query["facilityId"] = facilityId
    if po:
        query["poNumber"] = {"$regex": po, "$options": "i"}
    
    # Date range
    if from_date or to_date:
        date_query = {}
        if from_date:
            date_query["$gte"] = datetime.fromisoformat(from_date)
        if to_date:
            date_query["$lte"] = datetime.fromisoformat(to_date)
        if date_query:
            query["createdAt"] = date_query
    
    # Cursor decoding
    if cursor:
        try:
            cursor_data = base64.b64decode(cursor).decode('utf-8')
            last_created_at = datetime.fromisoformat(cursor_data)
            query["createdAt"] = {**query.get("createdAt", {}), "$lt": last_created_at}
        except:
            raise HTTPException(400, "Invalid cursor")
    
    # Fetch
    cursor_db = db.shipments.find(query).sort("createdAt", -1).limit(limit + 1)
    shipments = []
    async for doc in cursor_db:
        shipments.append(doc)
    
    # Has more
    has_more = len(shipments) > limit
    if has_more:
        shipments = shipments[:limit]
    
    # Next cursor
    next_cursor = None
    if has_more and shipments:
        last = shipments[-1]
        next_cursor = base64.b64encode(
            last["createdAt"].isoformat().encode('utf-8')
        ).decode('utf-8')
    
    # Format
    items = []
    for shipment in shipments:
        items.append({
            "id": str(shipment["_id"]),
            "facilityId": shipment["facilityId"],
            "facilityName": shipment["facilityName"],
            "poNumber": shipment["poNumber"],
            "status": shipment["status"],
            "items": shipment["items"],
            "createdAt": shipment["createdAt"]
        })
    
    return {
        "items": items,
        "nextCursor": next_cursor
    }

@router.patch("/{id}/items")
async def update_shipment_items(id: str, update: BulkItemUpdate):
    """Bulk update shipment items (with transaction)"""
    try:
        oid = ObjectId(id)
    except:
        raise HTTPException(400, "Invalid shipment ID")
    
    # Use transaction for atomic update
    async with await client.start_session() as session:
        async with session.start_transaction():
            shipment = await db.shipments.find_one({"_id": oid}, session=session)
            if not shipment:
                raise HTTPException(404, "Shipment not found")
            
            # Update items
            await db.shipments.update_one(
                {"_id": oid},
                {"$set": {
                    "items": [item.model_dump() for item in update.items],
                    "updatedAt": datetime.utcnow()
                }},
                session=session
            )
    
    return {"message": "Items updated successfully"}

@router.post("/import")
async def import_csv(file: UploadFile = File(...)):
    """Import shipments from CSV file"""
    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(400, "File must be CSV")
    
    contents = await file.read()
    text = contents.decode('utf-8')
    
    reader = csv.DictReader(io.StringIO(text))
    imported = 0
    errors = []
    
    for i, row in enumerate(reader, start=2):
        try:
            # Validate required fields
            if not all(k in row for k in ['facilityCode', 'poNumber', 'productCode', 'productName', 'quantity']):
                errors.append(f"Row {i}: Missing required fields")
                continue
            
            # Get or create facility
            facility = await db.facilities.find_one({"code": row['facilityCode']})
            if not facility:
                errors.append(f"Row {i}: Facility {row['facilityCode']} not found")
                continue
            
            # Create shipment
            doc = {
                "facilityId": str(facility["_id"]),
                "facilityName": facility["name"],
                "poNumber": row['poNumber'],
                "status": "pending",
                "items": [{
                    "productCode": row['productCode'],
                    "productName": row['productName'],
                    "quantity": int(row['quantity'])
                }],
                "createdAt": datetime.utcnow()
            }
            
            await db.shipments.insert_one(doc)
            imported += 1
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")
    
    return {
        "imported": imported,
        "errors": errors
    }

