"""
Content extraction and indexing utilities for Phase 7.2
----------------------------------------------------
T    # ✅ NEW: Create Qdrant client if not provided
    if qdrant_client is None:
        try:
            import os
            from qdrant_client import QdrantClient as QClient
            
            qdrant_url = os.getenv('QDRANT_URL', 'https://my-fyp-hcom.onrender.com')
            qdrant_api_key = os.getenv('QDRANT_API_KEY', '')
            
            qdrant_client = QClient(qdrant_url, qdrant_api_key)
            logger.info(f"✅ Created Qdrant client for {qdrant_url}")
        except Exception as e:
            logger.warning(f"⚠️  Could not create Qdrant client: {e}")ovides:
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

    # Create Qdrant client if not provided
    if qdrant_client is None:
        try:
            import os
            from qdrant_client import QdrantClient as QClient
            
            qdrant_url = os.getenv('QDRANT_URL', 'https://my-fyp-hcom.onrender.com')
            qdrant_api_key = os.getenv('QDRANT_API_KEY', '')
            
            qdrant_client = QClient(qdrant_url, qdrant_api_key)
            logger.info(f"✅ Created Qdrant client for {qdrant_url}")
        except Exception as e:
            logger.warning(f"⚠️ Could not create Qdrant client: {e}")
            # Continue without Qdrant client - will store locally only

    # Construct items for vector DB
    items = []
    for chunk in chunks:
        # Get user_id and other metadata from chunk
        chunk_metadata = chunk.get('metadata', {})
        
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
                'end_word': chunk.get('end_word'),
                'user_id': chunk_metadata.get('user_id', ''),
                'material_id': chunk_metadata.get('material_id', '')
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
                                 qdrant_client=None,
                                 material_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience routine to chunk text, embed chunks, and index them.
    
    Args:
        text: Text content to index
        max_tokens: Maximum tokens per chunk
        overlap: Overlap between chunks
        use_cache: Whether to use embedding cache
        collection_name: Qdrant collection name
        qdrant_client: Optional Qdrant client
        material_metadata: Optional metadata about the source material
            {
                'title': str,
                'material_type': str,
                'user_id': str,
                'file_name': str,
                ...
            }
    
    Returns a combined processing result.
    """
    chunks = chunk_text(text, max_tokens=max_tokens, overlap=overlap)
    if not chunks:
        return {'success': False, 'error': 'empty_text'}

    embedded = await embed_chunks(chunks, use_cache=use_cache)

    # Enhance chunks with material metadata if provided
    if material_metadata:
        title = material_metadata.get('title', 'user_material')
        material_type = material_metadata.get('material_type', 'notes')
        file_name = material_metadata.get('file_name', '')
        user_id = material_metadata.get('user_id', '')
        material_id = material_metadata.get('material_id', '')
        
        for c in embedded:
            c['title'] = title
            c['topic'] = f"{material_type}_{title.lower().replace(' ', '_')}"
            c['content_type'] = 'uploaded_material'
            c['source'] = file_name or title
            # Store user_id and material_id in metadata for filtering
            if not c.get('metadata'):
                c['metadata'] = {}
            c['metadata']['user_id'] = user_id
            c['metadata']['material_id'] = material_id
            # Store original metadata for later reference
            c['material_metadata'] = material_metadata

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
