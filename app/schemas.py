from typing import Optional
from pydantic import BaseModel


class LineItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    specifications: Optional[str] = None


class RFQExtraction(BaseModel):
    rfq_number: Optional[str] = None
    buyer_company: Optional[str] = None
    issue_date: Optional[str] = None
    response_deadline: Optional[str] = None
    delivery_location: Optional[str] = None
    delivery_date: Optional[str] = None
    payment_terms: Optional[str] = None
    currency: Optional[str] = None
    items: list[LineItem] = []
    special_requirements: list[str] = []


class ExtractRequest(BaseModel):
    text: str