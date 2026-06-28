from datetime import UTC, datetime
from typing import Any

from beanie import Document, Indexed, Insert, Save, Update, before_event
from pydantic import Field
from pymongo import TEXT, IndexModel
from slugify import slugify


class Category(Document):
    name: str = Indexed(typ=str, unique=True)
    description: str | None
    slug: str | None = Indexed(typ=str, unique=True, sparse=True)
    image_url: str

    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

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

    @before_event([Update, Save])
    def update_timestamp(self) -> None:
        self.name = self.name.strip().title()
        self.updated_at = datetime.now(tz=UTC)

    class Settings:
        name: str = 'categories'

        indexes: list[Any] = [
            'created_at',
            'updated_at',
            IndexModel(
                [('name', TEXT), ('description', TEXT)],
                weights={'name': 10, 'description': 2},
                name='category_text_index',
            ),
        ]
