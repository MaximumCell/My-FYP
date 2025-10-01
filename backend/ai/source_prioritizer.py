"""Source prioritization utilities (cleaned).

Single deterministic prioritizer used by the physics tutor to rank candidate
sources. Keeps things simple and easy to unit-test.
"""
from typing import List, Dict, Any


def prioritize_sources(user_materials: List[Dict[str, Any]],
                       preferred_books: List[Dict[str, Any]],
                       knowledge_results: List[Dict[str, Any]],
                       general_sources: List[Dict[str, Any]] = None,
                       top_k: int = 50) -> List[Dict[str, Any]]:
    """Return an ordered list of sources by priority.

    Priority order:
      1. user_materials
      2. preferred_books
      3. knowledge_results
      4. general_sources

    Each returned item is a dict with: 'id', 'type', 'score', 'metadata'.
    """
    candidates: List[Dict[str, Any]] = []

    for m in (user_materials or []):
        candidates.append({
            'id': m.get('_id') or m.get('id'),
            'type': 'user_material',
            'score': float(m.get('priority', 1.0)),
            'metadata': {'title': m.get('title'), 'snippet': (m.get('content') or '')[:300]}
        })

    for b in (preferred_books or []):
        # book can be an id or dict
        if isinstance(b, dict):
            bid = b.get('id') or b.get('_id') or b.get('book_id')
            title = b.get('title')
        else:
            bid = str(b)
            title = str(b)
        candidates.append({
            'id': bid,
            'type': 'book',
            'score': float((b.get('priority') if isinstance(b, dict) else 0.8) or 0.8),
            'metadata': {'title': title}
        })

    for k in (knowledge_results or []):
        score = float(k.get('score') or k.get('similarity') or 0.5)
        candidates.append({
            'id': k.get('id') or k.get('_id'),
            'type': 'knowledge',
            'score': score,
            'metadata': {'title': k.get('title') or k.get('doc_title'), 'snippet': (k.get('text') or '')[:300]}
        })

    for g in (general_sources or []):
        candidates.append({
            'id': g.get('id') or g.get('_id'),
            'type': g.get('type', 'general'),
            'score': float(g.get('score', 0.1)),
            'metadata': {'title': g.get('title'), 'snippet': (g.get('snippet') or '')[:300]}
        })

    # sort by score then type priority
    type_priority = {'user_material': 4, 'book': 3, 'knowledge': 2, 'general': 1}

    def sort_key(item: Dict[str, Any]):
        return (type_priority.get(item.get('type'), 0), item.get('score', 0.0))

    candidates.sort(key=sort_key, reverse=True)
    # deduplicate preserving first occurrence
    seen = set()
    out = []
    for c in candidates:
        cid = c.get('id') or c.get('metadata', {}).get('title')
        if cid in seen:
            continue
        seen.add(cid)
        out.append(c)
        if len(out) >= top_k:
            break

    return out

