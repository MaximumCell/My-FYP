from datetime import datetime
from typing import Optional, Dict, Any
from pymongo.collection import Collection

# Helper functions for physics_books collection

def get_books_collection(db) -> Collection:
    return db.get_collection("physics_books")


def create_book(db, title: str, author: Optional[str] = None, edition: Optional[str] = None, subject_areas: Optional[list] = None, source_url: Optional[str] = None) -> Dict[str, Any]:
    coll = get_books_collection(db)
    doc = {
        "title": title,
        "author": author or "",
        "edition": edition or "",
        "subject_areas": subject_areas or [],
        "source_url": source_url,
        "processing_status": "registered",
        "chunks_count": 0,
        "popularity_score": 0,
        "embedding": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    res = coll.insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc


def get_book(db, book_id):
    coll = get_books_collection(db)
    return coll.find_one({"_id": book_id})


def list_books(db, limit: int = 50):
    coll = get_books_collection(db)
    return list(coll.find().sort("created_at", -1).limit(limit))


def update_book_status(db, book_id, status: str):
    coll = get_books_collection(db)
    coll.update_one({"_id": book_id}, {"$set": {"processing_status": status, "updated_at": datetime.utcnow()}})
