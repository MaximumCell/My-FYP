"""
Content extraction and indexing utilities for Phase 7.2
----------------------------------------------------
This module provides:
- text chunking (by size and sentence boundaries)
- simple metadata extraction (page/chunk ids)
- embedding preparation using the project's embedding service
- helper to call the PhysicsVectorDatabase indexing pipeline

The implementation is intentionally minimal and synchronous-friendly so it
can be used in a background worker later. It provides an async API to match
the embedding and vector DB interfaces used elsewhere.
"""
import asyncio
import logging
import math
import re
import uuid
from typing import List, Dict, Any, Optional

from .embedding_service import embed_texts, get_embedding_service
from .vector_database_integration import PhysicsContent, PhysicsVectorDatabase

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _split_sentences(text: str) -> List[str]:
    # Very small heuristic sentence splitter that keeps physics punctuation
    # intact (periods after abbreviations are not handled exhaustively).
    parts = re.split(r'(?<=[\.\?!\n])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]


def chunk_text(text: str, max_tokens: int = 200, overlap: int = 20) -> List[Dict[str, Any]]:
    """
    Chunk text into pieces roughly bounded by max_tokens (approx words here)

    Returns list of dicts: { 'chunk_id', 'text', 'words', 'start_word', 'end_word' }
    """
    if not text or not text.strip():
        return []

    words = text.split()
    if len(words) <= max_tokens:
        return [{
            'chunk_id': str(uuid.uuid4()),
            'text': text.strip(),
            'words': len(words),
            'start_word': 0,
            'end_word': len(words) - 1
        }]

    chunks = []
    step = max_tokens - overlap
    for start in range(0, len(words), step):
        end = min(start + max_tokens, len(words))
        chunk_words = words[start:end]
        chunk_text = ' '.join(chunk_words)
        chunks.append({
            'chunk_id': str(uuid.uuid4()),
            'text': chunk_text,
            'words': len(chunk_words),
            'start_word': start,
            'end_word': end - 1
        })
        if end == len(words):
            break

    return chunks


async def embed_chunks(chunks: List[Dict[str, Any]], use_cache: bool = True) -> List[Dict[str, Any]]:
    """
    Compute embeddings for chunk list using the embedding service.

    Adds an 'embedding' field to each chunk dict and returns the list.
    """
    if not chunks:
        return []

    texts = [c['text'] for c in chunks]
    # Use batch embedding helper
    embedding_service = get_embedding_service()
    batch_result = await embedding_service.generate_batch_embeddings(texts, use_cache=use_cache)

    # Attach embeddings to chunks (match by index)
    results = []
    for i, c in enumerate(chunks):
        if i < len(batch_result.results):
            emb_res = batch_result.results[i]
            c_out = c.copy()
            c_out['embedding'] = emb_res.embedding if emb_res and not emb_res.error else []
            c_out['embedding_error'] = emb_res.error if emb_res and emb_res.error else None
            results.append(c_out)
        else:
            c_out = c.copy()
            c_out['embedding'] = []
            c_out['embedding_error'] = 'missing_result'
            results.append(c_out)

    return results


async def index_chunks(chunks: List[Dict[str, Any]],
                       collection_name: str = 'physics_knowledge',
                       qdrant_client=None) -> Dict[str, Any]:
    """
    Prepare PhysicsContent items and send them to the PhysicsVectorDatabase for indexing.
    Returns the result dict from add_physics_content.
    """
    if not chunks:
        return {'success': False, 'error': 'no_chunks'}

    # Construct items for vector DB
    items = []
    for chunk in chunks:
        item = {
            'id': chunk.get('chunk_id') or str(uuid.uuid4()),
            'title': chunk.get('title') or 'user_material_chunk',
            'content': chunk['text'],
            'topic': chunk.get('topic', 'user_material'),
            'subtopic': chunk.get('subtopic'),
            'difficulty_level': chunk.get('difficulty_level', 'intermediate'),
            'content_type': chunk.get('content_type', 'text_chunk'),
            'source': chunk.get('source'),
            'metadata': {
                'start_word': chunk.get('start_word'),
                'end_word': chunk.get('end_word')
            }
        }
        items.append(item)

    vector_db = PhysicsVectorDatabase(qdrant_client=qdrant_client, collection_name=collection_name)
    result = await vector_db.add_physics_content(items)
    return result


async def process_and_index_text(text: str,
                                 max_tokens: int = 200,
                                 overlap: int = 20,
                                 use_cache: bool = True,
                                 collection_name: str = 'physics_knowledge',
                                 qdrant_client=None) -> Dict[str, Any]:
    """
    Convenience routine to chunk text, embed chunks, and index them.
    Returns a combined processing result.
    """
    chunks = chunk_text(text, max_tokens=max_tokens, overlap=overlap)
    if not chunks:
        return {'success': False, 'error': 'empty_text'}

    embedded = await embed_chunks(chunks, use_cache=use_cache)

    # Merge embeddings into items for indexing
    for c in embedded:
        # attach any additional fields expected by indexer
        pass

    index_result = await index_chunks(embedded, collection_name=collection_name, qdrant_client=qdrant_client)
    return {
        'chunks_count': len(embedded),
        'index_result': index_result
    }


def simple_preview(text: str, max_chars: int = 120) -> str:
    """Return a short preview snippet for UI or citation snippets."""
    if not text:
        return ''
    return (text[:max_chars] + '...') if len(text) > max_chars else text
