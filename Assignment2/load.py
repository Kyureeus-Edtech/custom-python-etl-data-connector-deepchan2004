import os
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
from extract import extract_wayback 
from transform import transform_wayback
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

_client = None

def get_mongo_client():
    global _client
    if _client is None:
        if not MONGO_URI:
            raise ValueError("[ERROR] MONGO_URI not found in .env file")
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return _client


def load_to_mongodb(document: dict, collection_name: str = None, upsert_key: str = "url") -> None:
    
    collection_name = collection_name
    client = get_mongo_client()
    db = client[MONGO_DB]
    collection = db[collection_name]


    document["last_updated"] = datetime.utcnow()
    created_at = document.get("created_at", datetime.utcnow())

    
    doc_for_set = {k: v for k, v in document.items() if k != "created_at"}

    try:
        result = collection.update_one(
            {upsert_key: document.get(upsert_key)},
            {"$set": doc_for_set, "$setOnInsert": {"created_at": created_at}},
            upsert=True
        )

        if result.upserted_id:
            print(f"Inserted new record for {document.get(upsert_key)}")
        elif result.modified_count > 0:
            print(f"Updated record for {document.get(upsert_key)}")
        else:
            print(f"No changes for {document.get(upsert_key)}")

    except PyMongoError as e:
        print(f"[ERROR] MongoDB operation failed: {e}")



