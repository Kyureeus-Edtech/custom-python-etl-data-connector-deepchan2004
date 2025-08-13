import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

def load_to_mongodb(document, collection_name):
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[collection_name]
    collection.insert_one(document)
    client.close()
