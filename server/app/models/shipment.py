from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class ShipmentItem(BaseModel):
    """Individual item in a shipment"""
    productCode: str
    productName: str
    quantity: int = Field(ge=0)

class ShipmentOut(BaseModel):
    """Shipment output"""
    id: str
    facilityId: str
    facilityName: str
    poNumber: str
    status: str
    items: List[ShipmentItem]
    createdAt: datetime

class BulkItemUpdate(BaseModel):
    """Bulk update items"""
    items: List[ShipmentItem]

