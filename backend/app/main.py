from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from app.core.database import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Connect to the database
    await db.connect()
    # 2. Store the database client in app state for later use
    app.state.db = db

    yield  # app is running

    # 3. Disconnect from the database when the application shuts down
    await db.disconnect()


app: FastAPI = FastAPI(lifespan=lifespan)


@app.get('/')
def read_root() -> dict[str, Any]:
    db_instance = app.state.db
    return {'Hello': 'Welcome to Nova Kicks API!', 'db_connected': db_instance.client is not None}
