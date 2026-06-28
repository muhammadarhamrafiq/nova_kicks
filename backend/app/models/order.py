from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import uuid4

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from pymongo import IndexModel


class OrderItem(BaseModel):
    product_id: str
    variant_sku: str | None = None

    product_name: str
    varaint_name: str | None = None

    quantity: int

    unit_price: Decimal
    total_price: Decimal

    image_url: str | None = None


class Address(BaseModel):
    first_name: str
    last_name: str

    phone: str
    address_line_1: str
    address_line_2: str | None = None

    city: str
    state: str
    postal_code: str
    country: str


class OrderStatus(StrEnum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'


class PaymentStatus(StrEnum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'


class Order(Document):
    order_number: str = Indexed(typ=str, unique=True)
    items: list[OrderItem]

    shipping_address: Address

    subtotal: Decimal
    shipping_cost: Decimal = Decimal(value=0)
    tax: Decimal = Decimal(value=0)
    discount: Decimal = Decimal(value=0)

    total: Decimal

    status: OrderStatus = OrderStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.PENDING

    notes: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    @classmethod
    def generate_order_number(cls):
        return f'ORD-{uuid4().hex[:10].upper()}'

    class Settings:
        name: str = 'orders'

        indexes = [
            'created_at',
            'updated_at',
            'status',
            'payment_status',
            IndexModel(
                keys=[
                    ('status', 1),
                    ('created_at', -1),
                ]
            ),
            IndexModel(
                keys=[
                    ('payment_status', 1),
                    ('created_at', -1),
                ]
            ),
        ]
