import os
import pymongo
import streamlit as st
from typing import List, Optional
from bson import ObjectId
from src.models import Vehicle, WorkOrder


MONGO_URI = st.secrets["MONGO_URI"]
DATABASE_NAME = st.secrets["DATABASE_NAME"]

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
    """Fetches all vehicles from the database."""
    try:
        vehicles_cursor = db_connection.vehicle_collection.find()
        vehicle_list = []
        for doc in vehicles_cursor:
            print("--- RAW DOCUMENT FROM MONGO ---")
            print(doc)
            vehicle_list.append(Vehicle.model_validate(doc))
        return vehicle_list
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
        # Separate the main updates from the fields to unset
        update_operation = {"$set": {}, "$unset": {}}

        for key, value in updates.items():
            if value is None:
                # If the value is None, we want to remove the field
                update_operation["$unset"][key] = ""
            else:
                # Otherwise, we set the new value
                update_operation["$set"][key] = value

        # Clean up empty operators
        if not update_operation["$set"]:
            del update_operation["$set"]
        if not update_operation["$unset"]:
            del update_operation["$unset"]

        result = db_connection.vehicle_collection.update_one(
            {"_id": ObjectId(vehicle_id)},
            update_operation
        )
        return result.modified_count > 0 or result.matched_count > 0
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

def add_work_order(work_order: WorkOrder) -> str:
    """Adds a new work order to the database."""
    try:
        # Get the dedicated work_orders collection
        collection = db_connection.db["work_orders"]
        work_order_dict = work_order.model_dump(by_alias=True)
        result = collection.insert_one(work_order_dict)
        return str(result.inserted_id)
    except Exception as e:
        print(f"An error occurred while adding work order: {e}")
        return ""

def get_work_orders_for_vehicle(vehicle_id: str) -> List[WorkOrder]:
    """Fetches all work orders for a specific vehicle."""
    try:
        collection = db_connection.db["work_orders"]
        # Find all orders where vehicle_id matches
        orders_cursor = collection.find({"vehicle_id": ObjectId(vehicle_id)})
        return [WorkOrder.model_validate(doc) for doc in orders_cursor]
    except Exception as e:
        print(f"An error occurred while fetching work orders: {e}")
        return []
