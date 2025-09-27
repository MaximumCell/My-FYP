"""
ML Model Schema and Service for PhysicsLab Application
Handles ML model data validation, database operations, and business logic
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
from pydantic.json_schema import JsonSchemaValue

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
class ModelType(str, Enum):
    regression = "regression"
    classification = "classification"
    clustering = "clustering"
    deep_learning = "deep-learning"
    other = "other"

# Pydantic Models
class DatasetInfo(BaseModel):
    """Dataset information schema"""
    columns: List[str]
    target_column: str
    data_shape: Dict[str, int]  # {"rows": 1000, "columns": 10}
    feature_types: Optional[Dict[str, str]] = None  # {"feature1": "numeric", "feature2": "categorical"}

class PerformanceMetrics(BaseModel):
    """Model performance metrics schema"""
    # Common metrics
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    
    # Regression metrics
    mse: Optional[float] = None
    rmse: Optional[float] = None
    mae: Optional[float] = None
    r2_score: Optional[float] = None
    
    # Cross-validation
    cross_val_score: Optional[float] = None
    
    # Custom metrics
    custom_metrics: Optional[Dict[str, float]] = None

class MLModelCreate(BaseModel):
    """Schema for creating a new ML model"""
    model_name: str = Field(..., min_length=1, max_length=200)
    model_type: ModelType
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = Field(default_factory=list)
    
    # Dataset and performance info
    dataset_info: DatasetInfo
    performance_metrics: PerformanceMetrics
    training_time: float = Field(..., gt=0)  # in seconds
    
    # Algorithm details
    algorithm_name: Optional[str] = Field(None, max_length=100)
    hyperparameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Sharing settings
    is_public: bool = Field(default=False)

class MLModelUpdate(BaseModel):
    """Schema for updating an existing ML model"""
    model_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None

class MLModel(BaseModel):
    """Complete ML model schema for database storage"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId
    
    # Basic info
    model_name: str
    model_type: ModelType
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # File info (Cloudinary)
    file_url: str
    file_public_id: str
    file_size: int  # in bytes
    
    # Dataset and performance info
    dataset_info: DatasetInfo
    performance_metrics: PerformanceMetrics
    training_time: float  # in seconds
    
    # Algorithm details
    algorithm_name: Optional[str] = None
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Sharing settings
    is_public: bool = Field(default=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_serializer('id', 'user_id')
    def serialize_object_id(self, value):
        return str(value) if value else None

class MLModelResponse(BaseModel):
    """ML model response schema for API responses"""
    id: str
    user_id: str
    model_name: str
    model_type: ModelType
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    file_url: str
    file_public_id: str
    file_size: int
    
    dataset_info: DatasetInfo
    performance_metrics: PerformanceMetrics
    training_time: float
    
    algorithm_name: Optional[str] = None
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    
    is_public: bool = Field(default=False)
    
    created_at: datetime
    updated_at: datetime

class MLModelListResponse(BaseModel):
    """Paginated response for model listing"""
    models: List[MLModelResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool

# Service Class
class MLModelService:
    """Service class for ML model operations"""
    
    def __init__(self, database):
        self.db = database
        self.collection: Collection = database['ml_models']
    
    def create_model(
        self, 
        user_id: str, 
        model_data: MLModelCreate, 
        file_info: Dict[str, Any]
    ) -> Optional[MLModelResponse]:
        """Create a new ML model record"""
        try:
            # Convert user_id to ObjectId
            user_object_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
            
            # Create model dictionary manually to preserve ObjectId
            model_dict = {
                "user_id": user_object_id,  # Store as ObjectId
                "model_name": model_data.model_name,
                "model_type": model_data.model_type.value,
                "description": model_data.description,
                "tags": model_data.tags,
                "file_url": file_info['secure_url'],
                "file_public_id": file_info['public_id'],
                "file_size": file_info['file_size'],
                "dataset_info": model_data.dataset_info.model_dump(),
                "performance_metrics": model_data.performance_metrics.model_dump(),
                "training_time": model_data.training_time,
                "algorithm_name": model_data.algorithm_name,
                "hyperparameters": model_data.hyperparameters,
                "is_public": model_data.is_public,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert directly into database
            result = self.collection.insert_one(model_dict)
            
            if result.inserted_id:
                created_model = self.collection.find_one({"_id": result.inserted_id})
                # Convert to response model
                created_model['id'] = str(created_model['_id'])
                created_model['user_id'] = str(created_model['user_id'])
                return MLModelResponse(**created_model)
            return None
        except Exception as e:
            print(f"Error creating model: {str(e)}")
            return None
    
    def get_model_by_id(self, model_id: str, user_id: str = None) -> Optional[MLModelResponse]:
        """Get model by ID, optionally filtered by user"""
        try:
            query = {"_id": ObjectId(model_id)}
            if user_id:
                # Handle both string and ObjectId user_ids
                if isinstance(user_id, str) and len(user_id) == 24:
                    try:
                        query["user_id"] = ObjectId(user_id)
                    except:
                        query["user_id"] = user_id
                else:
                    query["user_id"] = user_id
            
            model_data = self.collection.find_one(query)
            if model_data:
                # Convert for response
                model_data['id'] = str(model_data['_id'])
                model_data['user_id'] = str(model_data['user_id'])
                return MLModelResponse(**model_data)
            return None
        except Exception as e:
            print(f"Error getting model: {str(e)}")
            return None
    
    def get_user_models(
        self, 
        user_id: str, 
        page: int = 1, 
        page_size: int = 10,
        model_type: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> MLModelListResponse:
        """Get paginated list of user's models with optional filtering"""
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
            
            if model_type:
                query["model_type"] = model_type
            
            if search_query:
                query["$or"] = [
                    {"model_name": {"$regex": search_query, "$options": "i"}},
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
            models = []
            
            for doc in cursor:
                doc['id'] = str(doc['_id'])
                doc['user_id'] = str(doc['user_id'])
                models.append(MLModelResponse(**doc))
            
            return MLModelListResponse(
                models=models,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1
            )
        except Exception as e:
            print(f"Error getting user models: {str(e)}")
            return MLModelListResponse(
                models=[],
                total_count=0,
                page=page,
                page_size=page_size,
                total_pages=0,
                has_next=False,
                has_previous=False
            )
    
    def get_public_models(
        self, 
        page: int = 1, 
        page_size: int = 10
    ) -> MLModelListResponse:
        """Get paginated list of public models"""
        try:
            query = {"is_public": True}
            
            # Get total count
            total_count = self.collection.count_documents(query)
            
            # Calculate pagination
            skip = (page - 1) * page_size
            total_pages = (total_count + page_size - 1) // page_size
            
            # Get paginated results
            cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
            models = []
            
            for doc in cursor:
                doc['id'] = str(doc['_id'])
                doc['user_id'] = str(doc['user_id'])
                models.append(MLModelResponse(**doc))
            
            return MLModelListResponse(
                models=models,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1
            )
        except Exception as e:
            print(f"Error getting public models: {str(e)}")
            return MLModelListResponse(
                models=[],
                total_count=0,
                page=page,
                page_size=page_size,
                total_pages=0,
                has_next=False,
                has_previous=False
            )
    
    def update_model(
        self, 
        model_id: str, 
        user_id: str, 
        update_data: MLModelUpdate
    ) -> Optional[MLModelResponse]:
        """Update an existing model"""
        try:
            # Build query
            query = {"_id": ObjectId(model_id)}
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
                # Return updated model
                return self.get_model_by_id(model_id, user_id)
            return None
        except Exception as e:
            print(f"Error updating model: {str(e)}")
            return None
    
    def delete_model(self, model_id: str, user_id: str) -> bool:
        """Delete a model"""
        try:
            # Build query
            query = {"_id": ObjectId(model_id)}
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
            print(f"Error deleting model: {str(e)}")
            return False