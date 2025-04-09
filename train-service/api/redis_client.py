import os
import redis
from fastapi import HTTPException
import uuid

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Connect to Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Constants
LOCK_EXPIRATION_TIME = 600  # 10 minutes

def lock_seat(train_id, seat_number: str) -> str:
    key = f"seat:{train_id}:{seat_number}"
    lock_id = str(uuid.uuid4())

    acquired = redis_client.set(key, lock_id, ex=LOCK_EXPIRATION_TIME, nx=True)
    if not acquired:
        raise HTTPException(status_code=409, detail="Seat already locked")

    return lock_id

def unlock_seat(train_id, seat_number: str, lock_id: str) -> None:
    key = f"seat:{train_id}:{seat_number}"
    
    # Ensures only the owner of the lock can release it
    stored_lock_id = redis_client.get(key)
    if stored_lock_id and stored_lock_id == lock_id:
        redis_client.delete(key)
