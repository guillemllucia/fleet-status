# src/models.py

from datetime import date
from enum import Enum
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, model_validator

# =============================================================================
# 1. Base & Helper Models
# =============================================================================

class VehicleCondition(str, Enum):
    """Enumeration for the operational condition of a vehicle."""
    RUNNING = "RUNNING"
    NON_RUNNING = "NON_RUNNING"


class Documentation(BaseModel):
    """Model for a vehicle's documentation due dates."""
    inspection_due: date
    tax_due: date


class NonRunningDetails(BaseModel):
    """Model for details required when a vehicle is not running."""
    explanation: str
    estimated_budget: float
    eta: date

# =============================================================================
# 2. Main Vehicle Model
# =============================================================================

class Vehicle(BaseModel):
    """
    Represents a vehicle in the fleet.
    This model defines the structure for a document in the 'vehicles' collection.
    """
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    alias: str
    photo_url: Optional[str] = None
    condition: VehicleCondition
    non_running_details: Optional[NonRunningDetails] = None
    documentation: Documentation
    location: str

    @model_validator(mode='after')
    def check_non_running_details_logic(self) -> 'Vehicle':
        """Ensures non_running_details is populated only when condition is NON_RUNNING."""
        is_non_running = self.condition == VehicleCondition.NON_RUNNING
        details_provided = self.non_running_details is not None

        if is_non_running and not details_provided:
            raise ValueError("non_running_details must be provided when condition is NON_RUNNING")
        if not is_non_running and details_provided:
            raise ValueError("non_running_details must not be provided when condition is RUNNING")

        return self

    @property
    def is_available(self) -> bool:
        """
        A derived property to determine if a vehicle is available for use.
        A vehicle is available if it's RUNNING and its documentation is up-to-date.
        This field is calculated on the fly and not stored in the database.
        """
        today = date.today()
        docs_ok = (
            self.documentation.inspection_due > today and
            self.documentation.tax_due > today
        )
        return self.condition == VehicleCondition.RUNNING and docs_ok

    class Config:
        """Pydantic model configuration for MongoDB compatibility."""
        populate_by_name = True # Replaces allow_population_by_field_name
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# =============================================================================
# 3. WorkOrder Model
# =============================================================================

class WorkOrder(BaseModel):
    """
    Represents a work order for a specific vehicle.
    This model defines the structure for a document in the 'work_orders' collection.
    """
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    vehicle_id: ObjectId
    description: str
    cost: float
    start_date: date
    completion_date: Optional[date] = None
    tasks: List[str]

    class Config:
        """Pydantic model configuration for MongoDB compatibility."""
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
