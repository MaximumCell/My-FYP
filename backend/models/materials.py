from datetime import datetime
from typing import Optional, Dict, Any
from utils.database import get_database


def materials_collection():
    db = get_database()
    return db.get_collection('user_materials')


def create_material(doc: Dict[str, Any]) -> str:
    col = materials_collection()
    doc.setdefault('created_at', datetime.utcnow())
    res = col.insert_one(doc)
    return str(res.inserted_id)


def list_materials_for_user(user_id: str, limit: int = 50):
    col = materials_collection()
    docs = list(col.find({'user_id': user_id}).sort('created_at', -1).limit(limit))
    # convert ObjectId to str for id if present
    for d in docs:
        if '_id' in d:
            d['id'] = str(d['_id'])
            del d['_id']
    return docs
