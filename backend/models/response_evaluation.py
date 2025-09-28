"""
AI Response Quality Evaluation Model
Tracks AI supervisor evaluations and quality metrics
"""

from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

load_dotenv()

class UserQuery(BaseModel):
    original_question: str
    question_type: str  # "concept", "derivation", "problem_solving"
    difficulty_level: str  # "beginner", "intermediate", "advanced"
    topic: str

class AIResponse(BaseModel):
    response_content: str
    sources_used: List[str] = []
    response_length: str  # "short", "long"
    visual_aids_included: List[str] = []

class EvaluationCriteria(BaseModel):
    physics_accuracy: int = Field(ge=1, le=10)
    mathematical_correctness: int = Field(ge=1, le=10)
    explanation_clarity: int = Field(ge=1, le=10)
    completeness: int = Field(ge=1, le=10)
    educational_value: int = Field(ge=1, le=10)
    source_relevance: int = Field(ge=1, le=10)
    step_by_step_quality: int = Field(ge=1, le=10)  # for derivations

class DetailedFeedback(BaseModel):
    strengths: List[str] = []
    weaknesses: List[str] = []
    missing_elements: List[str] = []
    accuracy_issues: List[str] = []
    improvement_suggestions: List[str] = []

class SupervisorEvaluation(BaseModel):
    overall_score: float = Field(ge=1, le=10)
    evaluation_criteria: EvaluationCriteria
    detailed_feedback: DetailedFeedback
    supervisor_confidence: float = Field(ge=0, le=1)
    evaluation_model: str
    alternative_response_suggested: bool = False

class UserFeedback(BaseModel):
    user_rating: Optional[int] = Field(None, ge=1, le=5)
    user_comments: Optional[str] = None
    found_helpful: Optional[bool] = None
    reported_issues: List[str] = []

class EvaluationMetadata(BaseModel):
    evaluation_time: float  # seconds
    evaluation_timestamp: datetime = Field(default_factory=datetime.now)
    response_improvement_needed: bool = False
    flagged_for_review: bool = False

class ResponseEvaluation(BaseModel):
    user_id: str
    session_id: str
    message_id: str
    user_query: UserQuery
    ai_response: AIResponse
    supervisor_evaluation: SupervisorEvaluation
    user_feedback: UserFeedback = UserFeedback()
    evaluation_metadata: EvaluationMetadata
    created_at: datetime = Field(default_factory=datetime.now)

class ResponseEvaluationDB:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client.physicslab
        self.collection = self.db.response_evaluations
        
        # Create indexes for efficient querying
        self.create_indexes()
    
    def create_indexes(self):
        """Create database indexes for optimized querying"""
        try:
            # Indexes for common query patterns
            self.collection.create_index([("user_id", 1), ("created_at", -1)])
            self.collection.create_index([("session_id", 1)])
            self.collection.create_index([("user_query.topic", 1)])
            self.collection.create_index([("supervisor_evaluation.overall_score", -1)])
            self.collection.create_index([("evaluation_metadata.flagged_for_review", 1)])
            
            # Compound indexes for analytics
            self.collection.create_index([
                ("user_query.topic", 1),
                ("supervisor_evaluation.overall_score", -1)
            ])
            
            print("Response evaluation indexes created successfully")
        except Exception as e:
            print(f"Error creating evaluation indexes: {e}")
    
    def insert_evaluation(self, evaluation: ResponseEvaluation) -> str:
        """Insert new response evaluation"""
        try:
            evaluation_dict = evaluation.dict()
            result = self.collection.insert_one(evaluation_dict)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error inserting evaluation: {e}")
            return None
    
    def get_user_evaluations(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get evaluations for a specific user"""
        try:
            cursor = self.collection.find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(limit)
            return list(cursor)
        except Exception as e:
            print(f"Error getting user evaluations: {e}")
            return []
    
    def get_session_evaluations(self, session_id: str) -> List[Dict]:
        """Get all evaluations for a chat session"""
        try:
            cursor = self.collection.find({"session_id": session_id})
            return list(cursor)
        except Exception as e:
            print(f"Error getting session evaluations: {e}")
            return []
    
    def get_flagged_responses(self, limit: int = 50) -> List[Dict]:
        """Get responses flagged for review"""
        try:
            cursor = self.collection.find(
                {"evaluation_metadata.flagged_for_review": True}
            ).limit(limit)
            return list(cursor)
        except Exception as e:
            print(f"Error getting flagged responses: {e}")
            return []
    
    def get_low_quality_responses(self, threshold: float = 5.0, limit: int = 50) -> List[Dict]:
        """Get responses with quality scores below threshold"""
        try:
            cursor = self.collection.find(
                {"supervisor_evaluation.overall_score": {"$lt": threshold}}
            ).limit(limit)
            return list(cursor)
        except Exception as e:
            print(f"Error getting low quality responses: {e}")
            return []
    
    def update_user_feedback(self, evaluation_id: str, feedback: UserFeedback) -> bool:
        """Update user feedback for an evaluation"""
        try:
            result = self.collection.update_one(
                {"_id": evaluation_id},
                {"$set": {"user_feedback": feedback.dict()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating user feedback: {e}")
            return False
    
    def get_topic_analytics(self, topic: str, days: int = 30) -> Dict:
        """Get analytics for a specific physics topic"""
        try:
            from datetime import timedelta
            start_date = datetime.now() - timedelta(days=days)
            
            pipeline = [
                {
                    "$match": {
                        "user_query.topic": topic,
                        "created_at": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_responses": {"$sum": 1},
                        "avg_score": {"$avg": "$supervisor_evaluation.overall_score"},
                        "avg_physics_accuracy": {"$avg": "$supervisor_evaluation.evaluation_criteria.physics_accuracy"},
                        "avg_clarity": {"$avg": "$supervisor_evaluation.evaluation_criteria.explanation_clarity"},
                        "flagged_count": {
                            "$sum": {
                                "$cond": ["$evaluation_metadata.flagged_for_review", 1, 0]
                            }
                        }
                    }
                }
            ]
            
            result = list(self.collection.aggregate(pipeline))
            return result[0] if result else {}
        except Exception as e:
            print(f"Error getting topic analytics: {e}")
            return {}
    
    def get_quality_trends(self, days: int = 30) -> List[Dict]:
        """Get daily quality score trends"""
        try:
            from datetime import timedelta
            start_date = datetime.now() - timedelta(days=days)
            
            pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$created_at"
                            }
                        },
                        "avg_score": {"$avg": "$supervisor_evaluation.overall_score"},
                        "total_responses": {"$sum": 1},
                        "flagged_responses": {
                            "$sum": {
                                "$cond": ["$evaluation_metadata.flagged_for_review", 1, 0]
                            }
                        }
                    }
                },
                {
                    "$sort": {"_id": 1}
                }
            ]
            
            return list(self.collection.aggregate(pipeline))
        except Exception as e:
            print(f"Error getting quality trends: {e}")
            return []

# Initialize response evaluation database
response_evaluation_db = ResponseEvaluationDB()