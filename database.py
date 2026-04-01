import motor.motor_asyncio
import os
from datetime import datetime

# Secure Connection to MongoDB via Environment Variables
# For local development, set these in your .env or system environment
MONGODB_URI = os.getenv("MONGODB_URI", "YOUR_FALLBACK_URI_HERE")
DATABASE_NAME = os.getenv("DATABASE_NAME", "openenv_expense")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
db = client[DATABASE_NAME]

users_collection = db["users"]
env_history_collection = db["history"]
env_state_collection = db["states"]

async def save_user_state(user_id: str, state: dict, day: int, balance: float):
    """ Persists the current environment state for a user. """
    await env_state_collection.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id, "state": state, "day": day, "balance": balance}},
        upsert=True
    )

async def get_user_state(user_id: str):
    """ Retrieves the persisted environment state for a user. """
    return await env_state_collection.find_one({"user_id": user_id})

async def add_history_entry(user_id: str, action: int, reward: float, balance: float, day: int):
    """ Logs every action taken to history for full world trace. """
    await env_history_collection.insert_one({
        "user_id": user_id,
        "action": action,
        "reward": reward,
        "balance": balance,
        "day": day,
        "timestamp": datetime.utcnow()
    })
