from typing import Any

from beanie import init_beanie
from pymongo import AsyncMongoClient

from app.core.config import settings
from app.models import Category, Order, Product, User


class Database:
    def __init__(self) -> None:
        self.client: AsyncMongoClient[dict[str, Any]] | None = None

    async def connect(self) -> None:
        """
        Connect to the MongoDB database using Beanie and AsyncMongoClient.
        """

        try:
            self.client = AsyncMongoClient[dict[str, Any]](settings.mongo_uri)

            await init_beanie(
                database=self.client[settings.mongo_db_name],
                document_models=[User, Category, Product, Order],
            )

            print('Connected to Database')
        except Exception as e:
            print(f'Error connecting to MongoDB: {e}')
            raise e

    async def disconnect(self) -> None:
        """
        Disconnect from the MongoDB database.
        """
        print('Disconnecting from Database')
        if self.client:
            await self.client.close()


db: Database = Database()
