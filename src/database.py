import os
import pymongo
from dotenv import load_dotenv
from typing import List, Optional
from bson import ObjectId
from src.models import Vehicle

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

class DatabaseConnection:
    def __init__(self):
        self.client = None
        self.db = None
        self.vehicle_collection = None
        try:
            self.client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[DATABASE_NAME]
            self.vehicle_collection = self.db["vehicles"]
            print("✅ Database connection successful.")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")

db_connection = DatabaseConnection()

def get_all_vehicles() -> List[Vehicle]:
    try:
        vehicles_cursor = db_connection.vehicle_collection.find()
        return [Vehicle.model_validate(doc) for doc in vehicles_cursor]
    except Exception as e:
        print(f"An error occurred while fetching vehicles: {e}")
        return []

def add_vehicle(vehicle: Vehicle) -> str:
    try:
        vehicle_dict = vehicle.model_dump(by_alias=True)
        result = db_connection.vehicle_collection.insert_one(vehicle_dict)
        return str(result.inserted_id)
    except Exception as e:
        print(f"An error occurred while adding vehicle: {e}")
        return ""

def update_vehicle(vehicle_id: str, updates: dict) -> bool:
    """Updates a vehicle in the database."""
    try:
        result = db_connection.vehicle_collection.update_one(
            {"_id": ObjectId(vehicle_id)},
            {"$set": updates}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"An error occurred while updating vehicle: {e}")
        return False

def delete_vehicle(vehicle_id: str) -> bool:
    """Deletes a vehicle from the database."""
    try:
        result = db_connection.vehicle_collection.delete_one(
            {"_id": ObjectId(vehicle_id)}
        )
        return result.deleted_count > 0
    except Exception as e:
        print(f"An error occurred while deleting vehicle: {e}")
        return False
