"""Physics books blueprint for managing physics textbooks.

Endpoints:
- POST /api/books/add -> register basic book metadata
- POST /api/books/process -> trigger processing for a registered book; runs in a background thread
- GET /api/books/recommend -> recommend physics books for specific topics
- POST /api/books/select -> set preferred reference book for session
- GET /api/books/search -> search available physics textbooks
- GET /api/books/content/:id -> get book-specific physics content
- GET /api/books/list -> list all physics books
"""

from flask import Blueprint, request, jsonify, current_app
from threading import Thread
from datetime import datetime
import asyncio
import importlib.util
from pathlib import Path

# Try package imports first (works when repo root is on sys.path)
try:
    from backend.models import physics_books, physics_chat_session
    from backend.ai import book_ingest
    from backend.ai.embedding_service import get_embedding_service
    from backend.utils.database import get_database
except Exception:
    # Robust file-based fallback: load modules by path so the routes work when
    # running `python app.py` from the backend/ directory (no package context).
    base = Path(__file__).resolve().parent.parent

    # Load physics_books model
    pb_path = base / 'models' / 'physics_books.py'
    spec = importlib.util.spec_from_file_location('physics_books_local', str(pb_path))
    pb_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pb_mod)
    physics_books = pb_mod
    
    # Load physics_chat_session model (optional)
    try:
        pcs_path = base / 'models' / 'physics_chat_session.py'
        spec2 = importlib.util.spec_from_file_location('physics_chat_session_local', str(pcs_path))
        pcs_mod = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(pcs_mod)
        physics_chat_session = pcs_mod
    except Exception:
        physics_chat_session = None
    
    # Load book_ingest
    bi_path = base / 'ai' / 'book_ingest.py'
    spec3 = importlib.util.spec_from_file_location('book_ingest_local', str(bi_path))
    bi_mod = importlib.util.module_from_spec(spec3)
    spec3.loader.exec_module(bi_mod)
    book_ingest = bi_mod
    
    # Load embedding_service (optional)
    try:
        es_path = base / 'ai' / 'embedding_service.py'
        spec4 = importlib.util.spec_from_file_location('embedding_service_local', str(es_path))
        es_mod = importlib.util.module_from_spec(spec4)
        spec4.loader.exec_module(es_mod)
        get_embedding_service = getattr(es_mod, 'get_embedding_service')
    except Exception:
        get_embedding_service = None
    
    # Load database utils
    db_path = base / 'utils' / 'database.py'
    spec5 = importlib.util.spec_from_file_location('database_local', str(db_path))
    db_mod = importlib.util.module_from_spec(spec5)
    spec5.loader.exec_module(db_mod)
    get_database = getattr(db_mod, 'get_database')

bp = Blueprint("books", __name__, url_prefix="/api/books")


@bp.route("/add", methods=["POST"])
def add_book():
    """Create a minimal book record in MongoDB.

    Expected JSON: { title, author?, edition?, subject_areas?, source_url? }
    """
    data = request.json or {}
    title = data.get("title")
    if not title:
        return jsonify({"error": "title is required"}), 400

    db = get_database()
    book = physics_books.create_book(
        db,
        title=title,
        author=data.get("author"),
        edition=data.get("edition"),
        subject_areas=data.get("subject_areas") or [],
        source_url=data.get("source_url"),
    )
    return jsonify({"book": book}), 201


def _background_process_book(app, db, book_id, file_path, dry_run=True):
    with app.app_context():
        try:
            book_ingest.process_book(db, book_id, file_path, dry_run=dry_run)
        except Exception:
            current_app.logger.exception("book processing error")


@bp.route("/process", methods=["POST"])
def process_book_route():
    """Trigger book processing asynchronously."""
    data = request.json or {}
    book_id = data.get("book_id")
    file_path = data.get("file_path")
    dry_run = data.get("dry_run", True)

    if not book_id or not file_path:
        return jsonify({"error": "book_id and file_path required"}), 400

    db = get_database()
    app = current_app._get_current_object()
    t = Thread(target=_background_process_book, args=(app, db, book_id, file_path, dry_run), daemon=True)
    t.start()

    return jsonify({"status": "processing_started", "book_id": book_id}), 202


@bp.route("/list", methods=["GET"])
def list_books_route():
    """List all physics books."""
    try:
        db = get_database()
        limit = int(request.args.get("limit", 50))
        books = physics_books.list_books(db, limit=limit)
        
        # Convert ObjectId to string for JSON serialization
        for book in books:
            if '_id' in book:
                book['id'] = str(book['_id'])
                del book['_id']
        
        return jsonify({"success": True, "books": books}), 200
    except Exception as e:
        current_app.logger.exception("Failed to list books")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/recommend", methods=["GET"])
def recommend_books():
    """Recommend physics books for specific topics.
    
    Query params:
    - topic: physics topic (e.g., "mechanics", "thermodynamics")
    - difficulty: difficulty level (e.g., "undergraduate", "graduate")
    - limit: number of recommendations (default 5)
    """
    try:
        db = get_database()
        topic = request.args.get("topic")
        difficulty = request.args.get("difficulty")
        limit = int(request.args.get("limit", 5))
        
        coll = physics_books.get_books_collection(db)
        
        # Build query based on parameters
        query = {}
        if topic:
            query["subject_areas"] = {"$in": [topic]}
        if difficulty:
            query["difficulty_level"] = difficulty
        
        # Find matching books, sort by popularity
        books = list(coll.find(query).sort("popularity_score", -1).limit(limit))
        
        # Convert ObjectId to string
        for book in books:
            if '_id' in book:
                book['id'] = str(book['_id'])
                del book['_id']
        
        return jsonify({
            "success": True, 
            "recommendations": books,
            "topic": topic,
            "difficulty": difficulty
        }), 200
    except Exception as e:
        current_app.logger.exception("Book recommendation failed")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/select", methods=["POST"])
def select_preferred_book():
    """Set preferred reference book for a physics chat session.
    
    Expected JSON: { "session_id": str, "book_id": str }
    """
    try:
        data = request.json or {}
        session_id = data.get("session_id")
        book_id = data.get("book_id")
        
        if not session_id or not book_id:
            return jsonify({"success": False, "error": "session_id and book_id required"}), 400
        
        db = get_database()
        
        # Verify book exists
        book = physics_books.get_book(db, book_id)
        if not book:
            return jsonify({"success": False, "error": "Book not found"}), 404
        
        # Update session with preferred book
        sessions_coll = db.get_collection("physics_chat_sessions")
        result = sessions_coll.update_one(
            {"session_id": session_id},
            {
                "$addToSet": {"learning_context.preferred_books": book_id},
                "$set": {"updated_at": datetime.utcnow()}
            },
            upsert=True
        )
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "book_id": book_id,
            "book_title": book.get("title")
        }), 200
    except Exception as e:
        current_app.logger.exception("Failed to select preferred book")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/search", methods=["GET"])
def search_books():
    """Search available physics textbooks.
    
    Query params:
    - q: search query (searches in title, author, subject_areas)
    - limit: number of results (default 20)
    """
    try:
        db = get_database()
        query_text = request.args.get("q", "")
        limit = int(request.args.get("limit", 20))
        
        if not query_text:
            return jsonify({"success": False, "error": "Query parameter 'q' is required"}), 400
        
        coll = physics_books.get_books_collection(db)
        
        # Text search across title, author, and subject areas
        search_query = {
            "$or": [
                {"title": {"$regex": query_text, "$options": "i"}},
                {"author": {"$regex": query_text, "$options": "i"}},
                {"subject_areas": {"$regex": query_text, "$options": "i"}}
            ]
        }
        
        books = list(coll.find(search_query).sort("popularity_score", -1).limit(limit))
        
        # Convert ObjectId to string
        for book in books:
            if '_id' in book:
                book['id'] = str(book['_id'])
                del book['_id']
        
        return jsonify({
            "success": True,
            "results": books,
            "query": query_text,
            "count": len(books)
        }), 200
    except Exception as e:
        current_app.logger.exception("Book search failed")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/content/<book_id>", methods=["GET"])
def get_book_content(book_id):
    """Get book-specific physics content (chunks).
    
    Query params:
    - limit: number of chunks to return (default 50)
    """
    try:
        db = get_database()
        limit = int(request.args.get("limit", 50))
        
        # Get book metadata
        book = physics_books.get_book(db, book_id)
        if not book:
            return jsonify({"success": False, "error": "Book not found"}), 404
        
        # Load book_chunks module
        try:
            from backend.models import book_chunks
        except Exception:
            base = Path(__file__).resolve().parent.parent
            bc_path = base / 'models' / 'book_chunks.py'
            spec = importlib.util.spec_from_file_location('book_chunks_local', str(bc_path))
            bc_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(bc_mod)
            book_chunks = bc_mod
        
        # Get book chunks
        chunks = book_chunks.list_chunks_for_book(db, book_id, limit=limit)
        
        # Convert ObjectId to string
        for chunk in chunks:
            if '_id' in chunk:
                chunk['id'] = str(chunk['_id'])
                del chunk['_id']
        
        # Prepare book info
        book_info = {
            "id": str(book['_id']),
            "title": book.get("title"),
            "author": book.get("author"),
            "edition": book.get("edition"),
            "chunks_count": book.get("chunks_count", 0)
        }
        if '_id' in book:
            del book['_id']
        
        return jsonify({
            "success": True,
            "book": book_info,
            "chunks": chunks,
            "total_chunks": book.get("chunks_count", 0)
        }), 200
    except Exception as e:
        current_app.logger.exception("Failed to get book content")
        return jsonify({"success": False, "error": str(e)}), 500
