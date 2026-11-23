from typing import Optional

from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str = Field(
        description="Product or service name including its key specifications"
    )
    quantity: Optional[float] = Field(
        default=None, description="Numeric quantity only, for example 500"
    )
    unit: Optional[str] = Field(
        default=None,
        description="Unit of measure as written, for example meters, pairs, pieces, units",
    )
    specifications: Optional[str] = Field(
        default=None, description="Extra technical details if listed separately"
    )


class RFQExtraction(BaseModel):
    rfq_number: Optional[str] = Field(
        default=None, description="RFQ reference number or ID"
    )
    buyer_company: Optional[str] = Field(
        default=None, description="Name of the company issuing the RFQ"
    )
    issue_date: Optional[str] = Field(
        default=None, description="Date the RFQ was issued, as written"
    )
    response_deadline: Optional[str] = Field(
        default=None,
        description="Deadline for suppliers to submit quotations, including time and timezone if given",
    )
    delivery_location: Optional[str] = Field(
        default=None, description="Place where goods must be delivered"
    )
    delivery_date: Optional[str] = Field(
        default=None, description="Date by which goods must be delivered, as written"
    )
    payment_terms: Optional[str] = Field(
        default=None, description="Payment terms, for example Net 45 days"
    )
    currency: Optional[str] = Field(
        default=None,
        description="Currency for quotes as a 3-letter code, for example USD, AED, EUR",
    )
    items: list[LineItem] = Field(
        default_factory=list, description="Every requested line item"
    )
    special_requirements: list[str] = Field(
        default_factory=list,
        description="Certifications, warranties, documents or compliance conditions required from suppliers, one short string each",
    )


class ExtractRequest(BaseModel):
    text: str