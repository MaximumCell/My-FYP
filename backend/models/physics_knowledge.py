"""
Physics Knowledge Base Model
Stores structured physics concepts, derivations, formulas, and examples
"""

from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

load_dotenv()

class VisualAids(BaseModel):
    equations_latex: List[str] = []
    diagram_descriptions: List[str] = []
    graph_suggestions: List[str] = []

class Content(BaseModel):
    title: str
    concept_explanation: str
    mathematical_derivation: List[str] = []
    key_formulas: List[str] = []
    examples: List[str] = []
    prerequisites: List[str] = []
    difficulty_level: int = Field(ge=1, le=5)  # 1-5 scale

class SourceInfo(BaseModel):
    book_reference: str
    chapter: Optional[str] = None
    page_numbers: List[int] = []
    author_credibility: int = Field(ge=1, le=10)  # 1-10 scale

class PhysicsKnowledge(BaseModel):
    content_type: str  # "concept", "derivation", "formula", "example"
    topic: str  # "mechanics", "thermodynamics", "electromagnetism"
    subtopic: Optional[str] = None
    content: Content
    source_info: SourceInfo
    embedding: List[float] = []  # Vector embedding
    visual_aids: VisualAids = VisualAids()
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class PhysicsKnowledgeDB:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client.physicslab
        self.collection = self.db.physics_knowledge
        
        # Create indexes for efficient querying
        self.create_indexes()
    
    def create_indexes(self):
        """Create database indexes for optimized querying"""
        try:
            # Text index for content search
            self.collection.create_index([
                ("content.title", "text"),
                ("content.concept_explanation", "text"),
                ("topic", "text"),
                ("subtopic", "text")
            ])
            
            # Compound indexes for common queries
            self.collection.create_index([("topic", 1), ("content_type", 1)])
            self.collection.create_index([("content.difficulty_level", 1)])
            self.collection.create_index([("source_info.book_reference", 1)])
            
            # Vector search index (requires MongoDB Atlas)
            # This would be configured through MongoDB Atlas UI for vector search
            print("Database indexes created successfully")
        except Exception as e:
            print(f"Error creating indexes: {e}")
    
    def insert_knowledge(self, knowledge: PhysicsKnowledge) -> str:
        """Insert new physics knowledge into database"""
        try:
            knowledge_dict = knowledge.dict()
            result = self.collection.insert_one(knowledge_dict)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error inserting knowledge: {e}")
            return None
    
    def find_by_topic(self, topic: str, limit: int = 20) -> List[Dict]:
        """Find knowledge by physics topic"""
        try:
            cursor = self.collection.find({"topic": topic}).limit(limit)
            return list(cursor)
        except Exception as e:
            print(f"Error finding by topic: {e}")
            return []
    
    def search_content(self, query: str, limit: int = 10) -> List[Dict]:
        """Full-text search across physics content"""
        try:
            cursor = self.collection.find(
                {"$text": {"$search": query}}
            ).limit(limit)
            return list(cursor)
        except Exception as e:
            print(f"Error searching content: {e}")
            return []
    
    def find_by_difficulty(self, min_level: int, max_level: int, topic: str = None) -> List[Dict]:
        """Find knowledge by difficulty level range"""
        try:
            query = {
                "content.difficulty_level": {"$gte": min_level, "$lte": max_level}
            }
            if topic:
                query["topic"] = topic
            
            cursor = self.collection.find(query)
            return list(cursor)
        except Exception as e:
            print(f"Error finding by difficulty: {e}")
            return []
    
    def vector_search(self, query_vector: List[float], limit: int = 10) -> List[Dict]:
        """
        Vector similarity search (requires MongoDB Atlas Vector Search)
        This is a placeholder - actual implementation depends on Atlas setup
        """
        try:
            # This would use MongoDB Atlas Vector Search aggregation pipeline
            # For now, returning regular search as fallback
            return self.collection.find().limit(limit)
        except Exception as e:
            print(f"Error in vector search: {e}")
            return []
    
    def update_knowledge(self, knowledge_id: str, updates: Dict) -> bool:
        """Update existing knowledge entry"""
        try:
            updates["updated_at"] = datetime.now()
            result = self.collection.update_one(
                {"_id": knowledge_id},
                {"$set": updates}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating knowledge: {e}")
            return False
    
    def delete_knowledge(self, knowledge_id: str) -> bool:
        """Delete knowledge entry"""
        try:
            result = self.collection.delete_one({"_id": knowledge_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting knowledge: {e}")
            return False

# Initialize physics knowledge database
physics_knowledge_db = PhysicsKnowledgeDB()