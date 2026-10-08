import os
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

uri = os.getenv("MONGODB_URI")
client = MongoClient(uri, serverSelectionTimeoutMS=5000)

try:
    client.admin.command("ping")
    print("MongoDB connection successful!")
except Exception as e:
    print("Connection failed:", e)
finally:
    client.close()

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))

db = client["ind320"]
collection = db["test_collection"]

# CREATE
collection.insert_one({
    "_id": "connection_test",
    "area": "NO",
    "fill_level": 0.75
})

# READ
print("Original:", collection.find_one({"_id": "connection_test"}))

# UPDATE
collection.update_one(
    {"_id": "connection_test"},
    {"$set": {"fill_level": 0.80}}
)

print("Updated:", collection.find_one({"_id": "connection_test"}))

# DELETE
collection.delete_one({"_id": "connection_test"})

print("Remaining:", collection.find_one({"_id": "connection_test"}))

client.close()