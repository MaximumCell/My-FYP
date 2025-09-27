"""
Simulation Schema and Service for PhysicsLab Application
Handles simulation data validation, database operations, and business logic
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
from bson import ObjectId
from pymongo.collection import Collection
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom ObjectId type for Pydantic
from pydantic import field_serializer

class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic models"""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(cls.validate)
    
    @classmethod
    def validate(cls, v, info=None):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            return ObjectId(v)
        raise ValueError('Invalid ObjectId')
    
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, handler):
        field_schema.update(type="string")
        return field_schema

# Enums
class SimulationType(str, Enum):
    plot2d = "plot2d"
    plot3d = "plot3d"
    interactive_physics = "interactive-physics"
    custom_equation = "custom-equation"
    projectile_motion = "projectile-motion"
    electric_field = "electric-field"
    wave_simulation = "wave-simulation"
    other = "other"

# Pydantic Models
class SimulationConfig(BaseModel):
    """Simulation configuration schema"""
    equation: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    variables: List[str] = Field(default_factory=list)
    plot_type: Optional[str] = None
    x_range: Optional[List[float]] = None
    y_range: Optional[List[float]] = None
    z_range: Optional[List[float]] = None
    resolution: Optional[int] = None
    animation_settings: Optional[Dict[str, Any]] = None

class SimulationCreate(BaseModel):
    """Schema for creating a new simulation"""
    simulation_name: str = Field(..., min_length=1, max_length=200)
    simulation_type: SimulationType
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = Field(default_factory=list)
    
    # Configuration and execution info
    config: SimulationConfig
    execution_time: float = Field(..., gt=0)  # in seconds
    
    # Plot settings
    plot_title: Optional[str] = Field(None, max_length=200)
    x_label: Optional[str] = Field(None, max_length=100)
    y_label: Optional[str] = Field(None, max_length=100)
    z_label: Optional[str] = Field(None, max_length=100)
    
    # Sharing settings
    is_public: bool = Field(default=False)

class SimulationUpdate(BaseModel):
    """Schema for updating an existing simulation"""
    simulation_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None

class Simulation(BaseModel):
    """Complete simulation schema for database storage"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId
    
    # Basic info
    simulation_name: str
    simulation_type: SimulationType
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # File info (Cloudinary)
    plot_html_url: str
    plot_public_id: str
    plot_thumbnail_url: Optional[str] = None  # PNG thumbnail
    plot_thumbnail_public_id: Optional[str] = None
    file_size: int  # in bytes (HTML file size)
    
    # Configuration and execution info
    config: SimulationConfig
    execution_time: float  # in seconds
    
    # Plot settings
    plot_title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    z_label: Optional[str] = None
    
    # Sharing settings
    is_public: bool = Field(default=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_serializer('id', 'user_id')
    def serialize_object_id(self, value):
        return str(value) if value else None

class SimulationResponse(BaseModel):
    """Simulation response schema for API responses"""
    id: str
    user_id: str
    simulation_name: str
    simulation_type: SimulationType
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    plot_html_url: str
    plot_public_id: str
    plot_thumbnail_url: Optional[str] = None
    plot_thumbnail_public_id: Optional[str] = None
    file_size: int
    
    config: SimulationConfig
    execution_time: float
    
    plot_title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    z_label: Optional[str] = None
    
    is_public: bool = Field(default=False)
    
    created_at: datetime
    updated_at: datetime

class SimulationListResponse(BaseModel):
    """Paginated response for simulation listing"""
    simulations: List[SimulationResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool

# Service Class
class SimulationService:
    """Service class for simulation operations"""
    
    def __init__(self, database):
        self.db = database
        self.collection: Collection = database['simulations']
    
    def create_simulation(
        self, 
        user_id: str, 
        simulation_data: SimulationCreate, 
        file_info: Dict[str, Any],
        thumbnail_info: Optional[Dict[str, Any]] = None
    ) -> Optional[SimulationResponse]:
        """Create a new simulation record"""
        try:
            # Convert user_id to ObjectId
            user_object_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
            
            # Create simulation dictionary manually to preserve ObjectId
            simulation_dict = {
                "user_id": user_object_id,  # Store as ObjectId
                "simulation_name": simulation_data.simulation_name,
                "simulation_type": simulation_data.simulation_type.value,
                "description": simulation_data.description,
                "tags": simulation_data.tags,
                "plot_html_url": file_info['secure_url'],
                "plot_public_id": file_info['public_id'],
                "plot_thumbnail_url": thumbnail_info['secure_url'] if thumbnail_info else None,
                "plot_thumbnail_public_id": thumbnail_info['public_id'] if thumbnail_info else None,
                "file_size": file_info['file_size'],
                "config": simulation_data.config.model_dump(),
                "execution_time": simulation_data.execution_time,
                "plot_title": simulation_data.plot_title,
                "x_label": simulation_data.x_label,
                "y_label": simulation_data.y_label,
                "z_label": simulation_data.z_label,
                "is_public": simulation_data.is_public,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert directly into database
            result = self.collection.insert_one(simulation_dict)
            
            if result.inserted_id:
                created_simulation = self.collection.find_one({"_id": result.inserted_id})
                # Convert to response model
                created_simulation['id'] = str(created_simulation['_id'])
                created_simulation['user_id'] = str(created_simulation['user_id'])
                return SimulationResponse(**created_simulation)
            return None
        except Exception as e:
            print(f"Error creating simulation: {str(e)}")
            return None
    
    def get_simulation_by_id(self, simulation_id: str, user_id: str = None) -> Optional[SimulationResponse]:
        """Get simulation by ID, optionally filtered by user"""
        try:
            query = {"_id": ObjectId(simulation_id)}
            if user_id:
                # Handle both string and ObjectId user_ids
                if isinstance(user_id, str) and len(user_id) == 24:
                    try:
                        query["user_id"] = ObjectId(user_id)
                    except:
                        query["user_id"] = user_id
                else:
                    query["user_id"] = user_id
            
            simulation_data = self.collection.find_one(query)
            if simulation_data:
                # Convert for response
                simulation_data['id'] = str(simulation_data['_id'])
                simulation_data['user_id'] = str(simulation_data['user_id'])
                return SimulationResponse(**simulation_data)
            return None
        except Exception as e:
            print(f"Error getting simulation: {str(e)}")
            return None
    
    def get_user_simulations(
        self, 
        user_id: str, 
        page: int = 1, 
        page_size: int = 10,
        simulation_type: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> SimulationListResponse:
        """Get paginated list of user's simulations with optional filtering"""
        try:
            # Build query - handle both string and ObjectId user_ids
            if isinstance(user_id, str) and len(user_id) == 24:
                try:
                    # Try to convert to ObjectId if it looks like one
                    query = {"user_id": ObjectId(user_id)}
                except:
                    # If conversion fails, use as string
                    query = {"user_id": user_id}
            else:
                # Use as-is (string or already ObjectId)
                query = {"user_id": user_id}
            
            if simulation_type:
                query["simulation_type"] = simulation_type
            
            if search_query:
                query["$or"] = [
                    {"simulation_name": {"$regex": search_query, "$options": "i"}},
                    {"description": {"$regex": search_query, "$options": "i"}},
                    {"tags": {"$in": [search_query]}}
                ]
            
            # Get total count
            total_count = self.collection.count_documents(query)
            
            # Calculate pagination
            skip = (page - 1) * page_size
            total_pages = (total_count + page_size - 1) // page_size
            
            # Get paginated results
            cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
            simulations = []
            
            for doc in cursor:
                doc['id'] = str(doc['_id'])
                doc['user_id'] = str(doc['user_id'])
                simulations.append(SimulationResponse(**doc))
            
            return SimulationListResponse(
                simulations=simulations,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1
            )
        except Exception as e:
            print(f"Error getting user simulations: {str(e)}")
            return SimulationListResponse(
                simulations=[],
                total_count=0,
                page=page,
                page_size=page_size,
                total_pages=0,
                has_next=False,
                has_previous=False
            )
    
    def get_public_simulations(
        self, 
        page: int = 1, 
        page_size: int = 10
    ) -> SimulationListResponse:
        """Get paginated list of public simulations"""
        try:
            query = {"is_public": True}
            
            # Get total count
            total_count = self.collection.count_documents(query)
            
            # Calculate pagination
            skip = (page - 1) * page_size
            total_pages = (total_count + page_size - 1) // page_size
            
            # Get paginated results
            cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
            simulations = []
            
            for doc in cursor:
                doc['id'] = str(doc['_id'])
                doc['user_id'] = str(doc['user_id'])
                simulations.append(SimulationResponse(**doc))
            
            return SimulationListResponse(
                simulations=simulations,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1
            )
        except Exception as e:
            print(f"Error getting public simulations: {str(e)}")
            return SimulationListResponse(
                simulations=[],
                total_count=0,
                page=page,
                page_size=page_size,
                total_pages=0,
                has_next=False,
                has_previous=False
            )
    
    def update_simulation(
        self, 
        simulation_id: str, 
        user_id: str, 
        update_data: SimulationUpdate
    ) -> Optional[SimulationResponse]:
        """Update an existing simulation"""
        try:
            # Build query
            query = {"_id": ObjectId(simulation_id)}
            if isinstance(user_id, str) and len(user_id) == 24:
                try:
                    query["user_id"] = ObjectId(user_id)
                except:
                    query["user_id"] = user_id
            else:
                query["user_id"] = user_id
            
            # Build update document
            update_doc = {"$set": {"updated_at": datetime.utcnow()}}
            
            update_dict = update_data.model_dump(exclude_unset=True)
            if update_dict:
                update_doc["$set"].update(update_dict)
            
            # Update document
            result = self.collection.update_one(query, update_doc)
            
            if result.modified_count > 0:
                # Return updated simulation
                return self.get_simulation_by_id(simulation_id, user_id)
            return None
        except Exception as e:
            print(f"Error updating simulation: {str(e)}")
            return None
    
    def delete_simulation(self, simulation_id: str, user_id: str) -> bool:
        """Delete a simulation"""
        try:
            # Build query
            query = {"_id": ObjectId(simulation_id)}
            if isinstance(user_id, str) and len(user_id) == 24:
                try:
                    query["user_id"] = ObjectId(user_id)
                except:
                    query["user_id"] = user_id
            else:
                query["user_id"] = user_id
            
            result = self.collection.delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting simulation: {str(e)}")
            return False