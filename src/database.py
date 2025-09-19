# src/database.py

import os
from typing import List, Optional

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import OperationFailure, ConnectionFailure

# Import the Pydantic model from the models module
from src.models import Vehicle

# Load environment variables from a .env file for local development
load_dotenv()

# --- Database Configuration ---
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Ensure necessary configuration is present
if not MONGO_URI or not DATABASE_NAME:
    raise RuntimeError(
        "MONGO_URI and DATABASE_NAME must be set in the environment or a .env file."
    )

# =============================================================================
# ## Database Connection Class
# =============================================================================
#
# Manages the connection pool and provides access to collections.
#
# =============================================================================

class DatabaseConnection:
    """
    A singleton-style class to manage the MongoDB connection, client, and collections.
    """
    def __init__(self):
        """
        Initializes the database connection, verifies it, and sets up collection handles.
        """
        self.client = None
        self.db = None
        self.vehicle_collection = None
        try:
            # Set a 5-second timeout to quickly fail if the server is not available
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

            # The 'ping' command is a lightweight way to verify a connection.
            self.client.admin.command('ping')
            print("✅ MongoDB connection successful.")

            self.db = self.client[DATABASE_NAME]
            self.vehicle_collection = self.db["vehicles"]

        except ConnectionFailure as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            # Ensure resources are cleaned up if connection fails
            self.client = None
            self.db = None
            self.vehicle_collection = None

# --- Singleton Instance ---
# Create a single, module-level instance of the connection to be shared by all functions.
db_connection = DatabaseConnection()

# =============================================================================
# ## Helper Functions (CRUD Operations for Vehicles)
# =============================================================================
#
# These functions provide a clean, typed interface for interacting with the database.
#
# =============================================================================

def get_all_vehicles() -> List[Vehicle]:
    """
    Retrieves all vehicle documents from the collection.

    Returns:
        A list of `Vehicle` model instances. Returns an empty list on error or if
        the database connection is not available.
    """
    if not db_connection.vehicle_collection:
        print("Cannot get vehicles: Database not connected.")
        return []

    try:
        vehicles_cursor = db_connection.vehicle_collection.find()
        # Validate each document against the Pydantic model
        return [Vehicle.model_validate(doc) for doc in vehicles_cursor]
    except OperationFailure as e:
        print(f"Error fetching vehicles: {e}")
        return []

def get_vehicle_by_id(vehicle_id: str) -> Optional[Vehicle]:
    """
    Retrieves a single vehicle by its document ID.

    Args:
        vehicle_id: The string representation of the vehicle's ObjectId.

    Returns:
        A `Vehicle` model instance if found, otherwise `None`.
    """
    if not db_connection.vehicle_collection:
        print("Cannot get vehicle by ID: Database not connected.")
        return None

    try:
        # Convert the ID string to a BSON ObjectId for querying
        object_id = ObjectId(vehicle_id)
        document = db_connection.vehicle_collection.find_one({"_id": object_id})

        return Vehicle.model_validate(document) if document else None
    except Exception:
        # Catches errors from invalid ObjectId strings
        return None

def add_vehicle(vehicle: Vehicle) -> Optional[str]:
    """
    Adds a new vehicle document to the collection.

    Args:
        vehicle: A `Vehicle` Pydantic model instance to be added.

    Returns:
        The string representation of the new document's ID if successful, otherwise `None`.
    """
    if not db_connection.vehicle_collection:
        print("Cannot add vehicle: Database not connected.")
        return None

    try:
        # Convert the Pydantic model to a dict.
        # `by_alias=True` ensures that our `id` field is converted to `_id` for MongoDB.
        vehicle_dict = vehicle.model_dump(by_alias=True)

        result = db_connection.vehicle_collection.insert_one(vehicle_dict)

        return str(result.inserted_id)
    except OperationFailure as e:
        print(f"Error adding vehicle: {e}")
        return None
