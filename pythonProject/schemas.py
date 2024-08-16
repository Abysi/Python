from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Customer(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    email: str
    registration_date: datetime
    total_spend: float
    last_purchase_date: Optional[datetime]

    class Config:
        from_attributes = True

class TopCustomer(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    total_spend: float

class AnalyticsResponse(BaseModel):
    average_total_spend: float
    active_customers_percentage: float
    top_customers: List[TopCustomer]