import os
import pymongo
import streamlit as st
from typing import List, Optional
from bson import ObjectId
from src.models import Vehicle, WorkOrder # <-- Ensure WorkOrder is imported here

# Get secrets using st.secrets
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

# --- VEHICLE FUNCTIONS ---
def get_all_vehicles() -> List[Vehicle]:
    """Fetches all vehicles from the database."""
    try:
        vehicles_cursor = db_connection.vehicle_collection.find()
        vehicle_list = []
        for doc in vehicles_cursor:
            vehicle_list.append(Vehicle.model_validate(doc))
        return vehicle_list
    except Exception as e:
        print(f"An error occurred while fetching vehicles: {e}")
        return []

def add_vehicle(vehicle: Vehicle) -> str:
    """Adds a new vehicle to the database."""
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
        update_operation = {}
        fields_to_set = {}
        fields_to_unset = {}
        for key, value in updates.items():
            if value is None:
                fields_to_unset[key] = ""
            else:
                fields_to_set[key] = value
        if fields_to_set:
            update_operation["$set"] = fields_to_set
        if fields_to_unset:
            update_operation["$unset"] = fields_to_unset
        if not update_operation:
            return True
        result = db_connection.vehicle_collection.update_one(
            {"_id": ObjectId(vehicle_id)},
            update_operation
        )
        return result.matched_count > 0
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

# --- WORK ORDER FUNCTIONS ---
def add_work_order(work_order: WorkOrder) -> str:
    """Adds a new work order to the database."""
    try:
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
        orders_cursor = collection.find({"vehicle_id": ObjectId(vehicle_id)})
        return [WorkOrder.model_validate(doc) for doc in orders_cursor]
    except Exception as e:
        print(f"An error occurred while fetching work orders: {e}")
        return []
