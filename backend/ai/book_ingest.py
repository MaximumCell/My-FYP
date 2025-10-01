"""Book ingestion pipeline skeleton.

Responsibilities:
- given a book record and a file path or URL, extract pages, OCR them, chunk text,
- produce embeddings and call the vector DB indexer with provenance (book_id, page, chunk)

This is a lightweight implementation meant to be replaced by a robust background worker later.
"""
from typing import List, Dict, Any, Optional
import os
from .content_extractor import chunk_text, embed_chunks, index_chunks
from ..models import physics_books
from ..models import book_chunks
from .ocr_processor import ocr_file
from .content_extractor import simple_preview
from ..models.book_chunks import insert_chunk, get_book_chunks_collection
from ..ai.vector_database_integration import PhysicsVectorDatabase
from datetime import datetime
import asyncio


def process_book(db, book_id, file_path: str, dry_run: bool = True) -> Dict[str, Any]:
    """Process a single book file. If dry_run=True, perform chunking and embedding steps but do not call external vector DB.

    Returns a summary dict.
    """
    # 1) Load book metadata
    book = physics_books.get_book(db, book_id)
    if not book:
        raise ValueError("book not found")

    # 2) Text extraction: support .txt and .pdf via OCR
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            full_text = f.read()
        pages = [{'page': 1, 'text': full_text}]
    elif ext == '.pdf' or ext in ['.png', '.jpg', '.jpeg', '.tiff']:
        # Use OCR processor to extract per-page text
        try:
            ocr_result = ocr_file(file_path)
            pages = ocr_result.get('pages', [])
            full_text = ocr_result.get('text', '')
        except Exception as e:
            # bubble up as processing error
            physics_books.update_book_status(db, book_id, 'failed')
            raise
    else:
        raise NotImplementedError('Unsupported file type for book ingestion')

    # 3) For each page, chunk and persist chunk provenance
    total_chunks = 0
    persisted_chunk_ids = []

    async def _embed_and_attach(chunks_for_page):
        # embed_chunks expects list of chunk dicts and is async
        try:
            embedded = await embed_chunks(chunks_for_page)
            return embedded
        except Exception:
            return [{'chunk_id': c['chunk_id'], 'embedding': None} for c in chunks_for_page]

    loop = asyncio.new_event_loop()
    try:
        for p in pages:
            page_num = p.get('page') or 1
            text = p.get('text', '') or ''
            page_chunks = chunk_text(text, max_tokens=400, overlap=64)
            if not page_chunks:
                continue

            # attach provenance fields and persist minimal chunk metadata before embedding
            for idx, ch in enumerate(page_chunks):
                chunk_doc = {
                    'book_id': book_id,
                    'page': page_num,
                    'chunk_index': idx,
                    'chunk_id': ch.get('chunk_id'),
                    'text': ch.get('text'),
                    'text_snippet': simple_preview(ch.get('text')),
                    'metadata': {
                        'start_word': ch.get('start_word'),
                        'end_word': ch.get('end_word')
                    }
                }
                try:
                    cid = insert_chunk(db, chunk_doc)
                    persisted_chunk_ids.append(cid)
                except Exception:
                    # Log but continue
                    pass

            # embed page chunks (run embedding in new event loop to avoid nested loop issues)
            try:
                embedded_chunks = loop.run_until_complete(_embed_and_attach(page_chunks))
            except Exception:
                embedded_chunks = []

            # Optionally, attach embeddings back to persisted chunk docs (best-effort)
            for ec in (embedded_chunks or []):
                # ec expected to include 'chunk_id' and 'embedding'
                try:
                    # Update chunk doc with embedding if available
                    if ec.get('embedding'):
                        coll = get_book_chunks_collection(db)
                        coll.update_one({'chunk_id': ec.get('chunk_id')}, {'$set': {'embedding': ec.get('embedding'), 'updated_at': datetime.utcnow()}})
                except Exception:
                    continue

            total_chunks += len(page_chunks)

    finally:
        try:
            loop.close()
        except Exception:
            pass

    # 4) Index chunks in vector DB (if not dry_run)
    if not dry_run:
        try:
            # gather latest persisted chunks for this book
            coll = get_book_chunks_collection(db)
            persisted = list(coll.find({'book_id': book_id}))
            # convert to indexable items
            index_items = []
            for pc in persisted:
                index_items.append({
                    'chunk_id': pc.get('chunk_id'),
                    'text': pc.get('text'),
                    'title': book.get('title'),
                    'source': {'type': 'book', 'book_id': book_id, 'page': pc.get('page'), 'chunk_index': pc.get('chunk_index')},
                    'start_word': pc.get('metadata', {}).get('start_word'),
                    'end_word': pc.get('metadata', {}).get('end_word')
                })
            # call indexer (best-effort)
            try:
                # use the project's vector DB helper
                vector_db = PhysicsVectorDatabase()
                # vector DB expects 'content' field; adapt
                to_index = []
                for it in index_items:
                    to_index.append({
                        'id': it.get('chunk_id'),
                        'title': it.get('title'),
                        'content': it.get('text'),
                        'source': it.get('source'),
                        'metadata': {'start_word': it.get('start_word'), 'end_word': it.get('end_word')}
                    })
                # run in asyncio loop
                try:
                    loop.run_until_complete(vector_db.add_physics_content(to_index))
                except Exception:
                    # swallowing errors from vector DB to keep pipeline robust
                    pass
            except Exception:
                pass
        except Exception:
            pass

    # 5) Update book metadata
    physics_books.update_book_status(db, book_id, 'processed' if not dry_run else 'processed-dryrun')
    physics_books_coll = physics_books.get_books_collection(db)
    physics_books_coll.update_one({'_id': book_id}, {'$set': {'chunks_count': total_chunks, 'updated_at': datetime.utcnow()}})

    return {
        'book_id': book_id,
        'chunks': total_chunks,
        'persisted_chunk_ids': persisted_chunk_ids,
        'dry_run': dry_run,
    }
