"""
Physics Chat Sessions Model
Manages physics learning conversations and context
"""

from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

load_dotenv()

class LearningContext(BaseModel):
    current_topic: Optional[str] = None
    difficulty_preference: str = "intermediate"  # "beginner", "intermediate", "advanced"
    response_length_preference: str = "long"  # "short", "long"
    preferred_books: List[str] = []
    learning_goals: List[str] = []

class MessageMetadata(BaseModel):
    question_type: Optional[str] = None  # "concept", "derivation", "problem_solving"
    sources_used: List[str] = []
    confidence_level: Optional[float] = None
    visual_aids_generated: List[str] = []
    response_length: Optional[str] = None
    book_reference_used: Optional[str] = None

class ConversationMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str
    message_metadata: MessageMetadata = MessageMetadata()
    timestamp: datetime = Field(default_factory=datetime.now)

class SessionAnalytics(BaseModel):
    topics_covered: List[str] = []
    learning_progress: Dict[str, Any] = {}
    areas_needing_review: List[str] = []

class PhysicsChatSession(BaseModel):
    user_id: str
    session_id: str
    learning_context: LearningContext = LearningContext()
    conversation_history: List[ConversationMessage] = []
    session_analytics: SessionAnalytics = SessionAnalytics()
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class PhysicsChatSessionDB:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client.physicslab
        self.collection = self.db.physics_chat_sessions
        
        # Create indexes for efficient querying
        self.create_indexes()
    
    def create_indexes(self):
        """Create database indexes for optimized querying"""
        try:
            # Primary indexes
            self.collection.create_index([("user_id", 1), ("created_at", -1)])
            self.collection.create_index([("session_id", 1)])
            self.collection.create_index([("learning_context.current_topic", 1)])
            self.collection.create_index([("updated_at", -1)])
            
            print("Physics chat session indexes created successfully")
        except Exception as e:
            print(f"Error creating chat session indexes: {e}")
    
    def create_session(self, session: PhysicsChatSession) -> str:
        """Create new physics chat session"""
        try:
            session_dict = session.dict()
            result = self.collection.insert_one(session_dict)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating chat session: {e}")
            return None
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get chat session by session_id"""
        try:
            return self.collection.find_one({"session_id": session_id})
        except Exception as e:
            print(f"Error getting chat session: {e}")
            return None
    
    def get_user_sessions(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get all sessions for a user"""
        try:
            cursor = self.collection.find(
                {"user_id": user_id}
            ).sort("updated_at", -1).limit(limit)
            return list(cursor)
        except Exception as e:
            print(f"Error getting user sessions: {e}")
            return []
    
    def add_message(self, session_id: str, message: ConversationMessage) -> bool:
        """Add message to conversation history"""
        try:
            result = self.collection.update_one(
                {"session_id": session_id},
                {
                    "$push": {"conversation_history": message.dict()},
                    "$set": {"updated_at": datetime.now()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error adding message: {e}")
            return False
    
    def update_learning_context(self, session_id: str, context: LearningContext) -> bool:
        """Update learning context for session"""
        try:
            result = self.collection.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "learning_context": context.dict(),
                        "updated_at": datetime.now()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating learning context: {e}")
            return False
    
    def update_session_analytics(self, session_id: str, analytics: SessionAnalytics) -> bool:
        """Update session analytics"""
        try:
            result = self.collection.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "session_analytics": analytics.dict(),
                        "updated_at": datetime.now()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating session analytics: {e}")
            return False
    
    def get_active_sessions(self, hours: int = 24) -> List[Dict]:
        """Get sessions active within specified hours"""
        try:
            from datetime import timedelta
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            cursor = self.collection.find(
                {"updated_at": {"$gte": cutoff_time}}
            ).sort("updated_at", -1)
            return list(cursor)
        except Exception as e:
            print(f"Error getting active sessions: {e}")
            return []
    
    def get_topic_sessions(self, topic: str, limit: int = 50) -> List[Dict]:
        """Get sessions focused on a specific physics topic"""
        try:
            cursor = self.collection.find(
                {"learning_context.current_topic": topic}
            ).limit(limit)
            return list(cursor)
        except Exception as e:
            print(f"Error getting topic sessions: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """Delete chat session"""
        try:
            result = self.collection.delete_one({"session_id": session_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation history for a session"""
        try:
            session = self.collection.find_one({"session_id": session_id})
            if session and "conversation_history" in session:
                # Return last 'limit' messages
                history = session["conversation_history"]
                return history[-limit:] if len(history) > limit else history
            return []
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
    
    def search_conversations(self, query: str, user_id: str = None) -> List[Dict]:
        """Search conversation content"""
        try:
            search_filter = {
                "conversation_history.content": {"$regex": query, "$options": "i"}
            }
            if user_id:
                search_filter["user_id"] = user_id
            
            cursor = self.collection.find(search_filter)
            return list(cursor)
        except Exception as e:
            print(f"Error searching conversations: {e}")
            return []

# Initialize physics chat session database
physics_chat_session_db = PhysicsChatSessionDB()