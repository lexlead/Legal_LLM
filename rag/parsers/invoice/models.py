from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str
    quantity: int
    unit_price: Decimal
    total: Decimal


class InvoiceOutput(BaseModel):
    invoice_number: str
    invoice_date: date
    po_number: str
    vendor_name: str
    vendor_address: str
    line_items: List[LineItem]
    subtotal: Decimal
    tax: Optional[Decimal]
    total_amount: Decimal
    payment_terms: str


class EarlyPaymentDiscount(BaseModel):
    percentage: float = Field(..., description="Discount percentage if paid early.")
    days: int = Field(..., description="Number of days within which the payment must be made to apply the discount.")


class BulkOrderDiscount(BaseModel):
    percentage: float = Field(..., description="Discount percentage for bulk orders.")
    threshold: float = Field(..., description="Subtotal threshold above which the bulk discount applies.")


class VendorContractTerms(BaseModel):
    payment_terms: str = Field(..., description="The standard payment terms (e.g., Net 30).")
    early_payment_discount: Optional[EarlyPaymentDiscount] = Field(
        None,
        description="Optional early payment discount terms."
    )
    bulk_order_discount: Optional[BulkOrderDiscount] = Field(
        None,
        description="Optional bulk order discount terms."
    )


class PaymentDueReport(BaseModel):
    """Final payments due report."""
    invoice_number: str = Field(..., description="The identifier of the invoice this report refers to.")
    original_amount_due: float = Field(
        ..., description="The amount due without any discounts or early payment considerations."
    )
    early_payment_amount_due: Optional[float] = Field(
        None, description="The discounted amount if paid before the early payment deadline."
    )
    early_payment_deadline: Optional[date] = Field(
        None, description="The last date by which the early payment discount can be applied."
    )
    bulk_discount_applied: bool = Field(
        ..., description="Indicates whether a bulk order discount has been applied."
    )
    recommended_action: str = Field(
        ..., description="A recommendation for how and when to pay (e.g., 'Pay early to save 5%')."
    )
    notes: Optional[str] = Field(
        None, description="Additional commentary, instructions, or considerations for the payer."
    )
