from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import MONGODB_URI, MONGODB_DB
import asyncio

# Global variable to store MongoDB connection
mongo_client: AsyncIOMotorClient | None = None
mongo_db: AsyncIOMotorDatabase | None = None


def connect_to_mongo():
    """
    Create MongoDB connection when app starts. This function does not
    perform a network ping; it only constructs the Motor client and
    selects the database. Server selection / DNS will happen lazily on
    first operation. This mirrors the previous, lazy behavior.
    """
    global mongo_client, mongo_db

    if mongo_client is not None:
        return

    print("Connecting to MongoDB (lazy, no ping)...")
    mongo_client = AsyncIOMotorClient(MONGODB_URI)
    mongo_db = mongo_client[MONGODB_DB]
    print("MongoDB client created (server selection deferred).")


async def close_mongo_connection():
    """
    Close MongoDB connection when app stops.
    """
    global mongo_client
    if mongo_client is not None:
        print("Closing MongoDB connection...")
        mongo_client.close()
        mongo_client = None
        print("MongoDB connection closed!")


def get_database() -> AsyncIOMotorDatabase:
    """
    Get the MongoDB database instance. Returns None if client not
    initialized; callers should handle that case.
    """
    return mongo_db


