"""
User Model for PhysicsLab Application
"""
from datetime import datetime
from typing import Optional, Dict, Any, Annotated
from pydantic import BaseModel, Field, BeforeValidator, PlainSerializer
from bson import ObjectId

def validate_object_id(v: Any) -> ObjectId:
    """Validate and convert to ObjectId"""
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str):
        if ObjectId.is_valid(v):
            return ObjectId(v)
    raise ValueError('Invalid ObjectId')

def serialize_object_id(v: ObjectId) -> str:
    """Serialize ObjectId to string"""
    return str(v)

# Custom ObjectId type for Pydantic v2
PyObjectId = Annotated[
    ObjectId,
    BeforeValidator(validate_object_id),
    PlainSerializer(serialize_object_id, return_type=str),
]

class UsageAnalytics(BaseModel):
    """User usage analytics model"""
    total_models_trained: int = Field(default=0, description="Total number of ML models trained")
    total_simulations_run: int = Field(default=0, description="Total number of simulations executed")
    total_training_time: int = Field(default=0, description="Total training time in seconds")
    last_activity: Optional[datetime] = Field(default=None, description="Last activity timestamp")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

class User(BaseModel):
    """User model matching the MongoDB collection schema"""
    id: Optional[PyObjectId] = Field(alias='_id', default=None)
    clerk_user_id: str = Field(..., description="Unique Clerk user identifier")
    email: str = Field(..., description="User email address")
    name: str = Field(..., description="User display name")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    usage_analytics: UsageAnalytics = Field(default_factory=UsageAnalytics, description="User usage statistics")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
    }

class UserCreate(BaseModel):
    """User creation model (from Clerk webhook/sync)"""
    clerk_user_id: str
    email: str
    name: str

class UserUpdate(BaseModel):
    """User update model"""
    email: Optional[str] = None
    name: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserResponse(BaseModel):
    """User response model for API responses"""
    id: str
    clerk_user_id: str
    email: str
    name: str
    created_at: datetime
    updated_at: datetime
    usage_analytics: UsageAnalytics
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }

# Database operations for User model
class UserService:
    """Service class for User database operations"""
    
    def __init__(self, db):
        self.db = db
        self.collection = db.users
        
        # Create unique index on clerk_user_id
        self.collection.create_index("clerk_user_id", unique=True)
    
    def create_user(self, user_data: UserCreate) -> Optional[User]:
        """Create a new user"""
        try:
            user = User(**user_data.model_dump())
            result = self.collection.insert_one(user.model_dump(by_alias=True, exclude={'id'}))
            
            if result.inserted_id:
                created_user = self.collection.find_one({"_id": result.inserted_id})
                return User(**created_user)
            return None
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return None
    
    def get_user_by_clerk_id(self, clerk_user_id: str) -> Optional[User]:
        """Get user by Clerk user ID"""
        try:
            user_data = self.collection.find_one({"clerk_user_id": clerk_user_id})
            if user_data:
                return User(**user_data)
            return None
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None
    
    def update_user(self, clerk_user_id: str, update_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        try:
            update_dict = update_data.model_dump(exclude_unset=True)
            update_dict['updated_at'] = datetime.utcnow()
            
            result = self.collection.update_one(
                {"clerk_user_id": clerk_user_id},
                {"$set": update_dict}
            )
            
            if result.modified_count > 0:
                return self.get_user_by_clerk_id(clerk_user_id)
            return None
        except Exception as e:
            print(f"Error updating user: {str(e)}")
            return None
    
    def sync_user(self, user_data: UserCreate) -> User:
        """Sync user from Clerk (create or update)"""
        try:
            existing_user = self.get_user_by_clerk_id(user_data.clerk_user_id)
            
            if existing_user:
                # Update existing user
                update_data = UserUpdate(
                    email=user_data.email,
                    name=user_data.name
                )
                updated_user = self.update_user(user_data.clerk_user_id, update_data)
                return updated_user or existing_user
            else:
                # Create new user
                new_user = self.create_user(user_data)
                return new_user
        except Exception as e:
            print(f"Error syncing user: {str(e)}")
            raise
    
    def update_usage_analytics(self, clerk_user_id: str, analytics_update: Dict[str, Any]) -> bool:
        """Update user usage analytics"""
        try:
            update_fields = {}
            for key, value in analytics_update.items():
                if key in ['total_models_trained', 'total_simulations_run', 'total_training_time']:
                    update_fields[f'usage_analytics.{key}'] = value
            
            update_fields['usage_analytics.last_activity'] = datetime.utcnow()
            update_fields['updated_at'] = datetime.utcnow()
            
            result = self.collection.update_one(
                {"clerk_user_id": clerk_user_id},
                {"$set": update_fields}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating usage analytics: {str(e)}")
            return False