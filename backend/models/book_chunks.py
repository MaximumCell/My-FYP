from datetime import datetime
from typing import Dict, Any


def get_book_chunks_collection(db):
    return db.get_collection('book_chunks')


def insert_chunk(db, chunk: Dict[str, Any]) -> Any:
    coll = get_book_chunks_collection(db)
    # chunk should include: book_id, page, chunk_index, chunk_id, text, metadata, created_at
    chunk['created_at'] = datetime.utcnow()
    res = coll.insert_one(chunk)
    return res.inserted_id


def list_chunks_for_book(db, book_id, limit=100):
    coll = get_book_chunks_collection(db)
    return list(coll.find({'book_id': book_id}).sort('created_at', 1).limit(limit))
