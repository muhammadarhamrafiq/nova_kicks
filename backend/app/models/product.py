from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from beanie import Document, Indexed, Insert, Link, Update, before_event
from pydantic import BaseModel, Field, model_validator
from pymongo import TEXT, IndexModel
from slugify import slugify

from app.models import Category


class ProductOptions(BaseModel):
    name: str
    values: list[str] = Field(default_factory=list)


class ProductVariant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    sku: str
    attributes: dict[str, str] = Field(default_factory=dict)

    price: Decimal
    compare_at_price: Decimal | None = None
    cost_per_item: Decimal | None = None

    stock_quantity: int = 0
    low_stock_threshold: int = 5
    sold_count: int = 0

    image_urls: list[str] = Field(default_factory=list)

    is_active: bool = True


class Product(Document):
    name: str = Indexed(typ=str)
    description: str | None = None
    slug: str = Indexed(typ=str, unique=True, sparse=True)
    image_urls: list[str] = Field(default_factory=list)
    category: Link[Category] | None = None

    options: list[ProductOptions] = Field(default_factory=list)
    variants: list[ProductVariant] = Field(default_factory=list)

    brand: str | None = None
    tags: list[str] = Field(default_factory=list)

    is_active: bool = True
    is_featured: bool = False

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    embedding: list[float] | None = None

    @classmethod
    async def generate_unique_slug(cls, name: str) -> str:
        base = slugify(name)
        slug = base
        counter = 1

        while await cls.find_one(cls.slug == slug):
            slug = f'{base}-{counter}'
            counter += 1

        return slug

    @before_event(Insert)
    async def generate_slug(self) -> None:
        self.name = self.name.strip().title()

        if self.name and not self.slug:
            self.slug = await self.generate_unique_slug(self.name)

    @before_event([Insert, Update])
    def update_timestamp(self) -> None:
        self.name = self.name.strip().title()
        self.updated_at = datetime.now(UTC)

    @model_validator(mode='after')
    def validate_variants(self):
        if not self.variants:
            raise ValueError('At least one variant is required for a product.')
        return self

    class Settings:
        name = 'products'

        indexes = [
            'created_at',
            'updated_at',
            'brand',
            'is_active',
            'is_featured',
            IndexModel(
                [('name', TEXT), ('desciprtion', TEXT), ('tags', TEXT)],
                weights={'name': 10, 'description': 5, 'tags': 2},
                name='product_text_index',
            ),
            IndexModel(
                [
                    ('category', 1),
                    ('is_active', 1),
                ]
            ),
            IndexModel(
                [
                    ('is_featured', 1),
                    ('created_at', -1),
                ]
            ),
            IndexModel(
                [
                    ('variants.sku', 1),
                ],
                unique=True,
            ),
        ]
