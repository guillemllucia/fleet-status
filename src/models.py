# src/models.py

from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Any

from bson import ObjectId
from pydantic import BaseModel, Field, model_validator, computed_field

# =============================================================================
# 1. Base & Helper Models
# =============================================================================

class VehicleCondition(str, Enum):
    """Enumeration for the operational condition of a vehicle."""
    RUNNING = "RUNNING"
    NON_RUNNING = "NON_RUNNING"


class Documentation(BaseModel):
    """Model for a vehicle's documentation due dates."""
    inspection_due: datetime
    tax_due: datetime


class NonRunningDetails(BaseModel):
    """Model for details required when a vehicle is not running."""
    explanation: str
    estimated_budget: float
    eta: datetime

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

    @model_validator(mode='before')
    @classmethod
    def check_non_running_details_logic(cls, data: Any) -> Any:
        if isinstance(data, dict):
            condition = data.get('condition')
            details = data.get('non_running_details')

            if condition == VehicleCondition.RUNNING.value and details:
                raise ValueError("Non-running details should not be provided for a running vehicle.")
            if condition == VehicleCondition.NON_RUNNING.value and not details:
                raise ValueError("Non-running details are required for a non-running vehicle.")
        return data

    @computed_field
    @property
    def is_available(self) -> bool:
        """A vehicle is available if its condition is 'Running' and docs are current."""
        docs_are_valid = (
            self.documentation.inspection_due.date() > date.today() and
            self.documentation.tax_due.date() > date.today()
        )
        return self.condition == VehicleCondition.RUNNING and docs_are_valid

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
