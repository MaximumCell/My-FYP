"""Citation manager for formatting and returning citations for sources used
by the Physics AI Tutor.

This is a minimal implementation that can be extended to generate full
reference strings, include page/chunk pointers, and produce standardized
citation metadata.
"""
from typing import List, Dict, Any


def generate_citations(prioritized_sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Create a list of citation dicts from prioritized source dicts.

    Output citation shape:
      {
        'source_id': str,
        'source_type': 'user_material'|'preferred_book'|'knowledge_base'|'general',
        'title': str,
        'snippet': str,   # optional short excerpt
        'confidence': float
      }
    """
    citations = []
    for s in prioritized_sources or []:
        meta = s.get('meta') or {}
        title = s.get('title') or meta.get('title') or meta.get('name') or 'untitled'
        snippet = ''
        # Try to get a short snippet from known fields
        if isinstance(meta, dict):
            snippet = meta.get('content') or meta.get('excerpt') or meta.get('text') or ''
            if isinstance(snippet, str) and len(snippet) > 200:
                snippet = snippet[:197] + '...'

        citations.append({
            'source_id': str(s.get('id')) if s.get('id') is not None else title,
            'source_type': s.get('type', 'unknown'),
            'title': title,
            'snippet': snippet,
            'confidence': float(s.get('score', 0.0))
        })

    return citations
"""
Citation manager

Creates human-readable citations for sources used in AI responses and
returns structured citation metadata that can be attached to responses or
stored in evaluation records.
"""
from typing import List, Dict, Any
import datetime


def _format_book_citation(src: Dict[str, Any]) -> Dict[str, Any]:
    title = src.get('metadata', {}).get('title') or src.get('title') or 'Unknown Title'
    author = src.get('metadata', {}).get('author') or src.get('author') or 'Unknown Author'
    citation = f"{author}. {title}."
    return {
        'source_id': src.get('id'),
        'type': src.get('type', 'book'),
        'citation': citation,
        'confidence': float(src.get('score', 0.0)),
        'retrieved_at': datetime.datetime.utcnow().isoformat()
    }


def _format_user_material_citation(src: Dict[str, Any]) -> Dict[str, Any]:
    title = src.get('metadata', {}).get('title') or 'User Material'
    citation = f"User material: {title}"
    return {
        'source_id': src.get('id'),
        'type': 'user_material',
        'citation': citation,
        'confidence': float(src.get('score', 0.0)),
        'retrieved_at': datetime.datetime.utcnow().isoformat()
    }


def generate_citations(prioritized_sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate a list of structured citations from prioritized sources.

    The function is intentionally simple: it maps source entries to citation
    strings and attaches minimal metadata (confidence, id, timestamp). It can
    be extended to include page/chapter numbers, URLs, or standardized
    bibliographic formats (APA/MLA) later.
    """
    citations: List[Dict[str, Any]] = []
    for src in (prioritized_sources or []):
        try:
            t = src.get('type')
            if t == 'book':
                citations.append(_format_book_citation(src))
            elif t == 'user_material':
                citations.append(_format_user_material_citation(src))
            else:
                # Generic fallback
                citations.append({
                    'source_id': src.get('id'),
                    'type': src.get('type', 'other'),
                    'citation': src.get('metadata', {}).get('title') or str(src.get('id')),
                    'confidence': float(src.get('score', 0.0)),
                    'retrieved_at': datetime.datetime.utcnow().isoformat()
                })
        except Exception:
            # Non-fatal: skip malformed source
            continue

    return citations


__all__ = ['generate_citations']
"""
Citation manager: formats and returns citation strings and metadata
for retrieved chunks and sources.
"""
from typing import List, Dict, Any


def format_citation(source: Dict[str, Any]) -> Dict[str, Any]:
    """Create a human-readable citation from a source dict.

    Expected source fields: type (user_material/book/knowledge/web), title, author, chapter, page, url, score
    Returns a dict: { 'citation_text', 'source_id', 'confidence' }
    """
    stype = source.get('type', 'source')
    title = source.get('title') or source.get('metadata', {}).get('title') or 'Unknown Title'
    author = source.get('author') or source.get('metadata', {}).get('author')
    chapter = source.get('chapter') or source.get('metadata', {}).get('chapter')
    page = source.get('page') or source.get('metadata', {}).get('page')
    url = source.get('url') or source.get('metadata', {}).get('url')

    parts = []
    if author:
        parts.append(author)
    parts.append(title)
    if chapter:
        parts.append(f'chapter {chapter}')
    if page:
        parts.append(f'page {page}')
    if url:
        parts.append(url)

    citation_text = ', '.join(parts)

    return {
        'citation_text': citation_text,
        'source_id': source.get('id'),
        'confidence': float(source.get('score', 0.0))
    }


def generate_citations(sources: List[Dict[str, Any]], max_items: int = 5) -> List[Dict[str, Any]]:
    """Take prioritized sources and return a list of formatted citations (top N)."""
    # Normalize a variety of internal source shapes into a stable citation object
    citations: List[Dict[str, Any]] = []
    for s in (sources or [])[:max_items]:
        try:
            # Try common places for title / text
            title = None
            if isinstance(s, dict):
                title = s.get('title') or s.get('citation') or s.get('citation_text')
                meta = s.get('metadata') or s.get('meta') or {}
                if not title and isinstance(meta, dict):
                    title = meta.get('title') or meta.get('name') or meta.get('excerpt')

            if not title:
                title = str(s.get('id') if isinstance(s, dict) and s.get('id') is not None else 'Untitled')

            # Confidence/score (accept 'score', 'confidence' or 'similarity_score')
            conf = 0.0
            if isinstance(s, dict):
                conf = float(
                    s.get('score',
                          s.get('confidence',
                                s.get('similarity_score', 0.0))) or 0.0
                )

            # Author/reference info if available
            author = None
            reference = None
            source_type = None
            if isinstance(s, dict):
                source_type = s.get('type') or (s.get('metadata') or {}).get('type')
                meta = s.get('metadata') or {}
                author = s.get('author') or meta.get('author')
                reference = s.get('url') or meta.get('url') or meta.get('reference')

            citations.append({
                'source_type': source_type or 'unknown',
                'title': title,
                'author': author,
                'reference': reference,
                'confidence': conf
            })
        except Exception:
            # Skip malformed source
            continue

    return citations
