"""
Test script for Phase 7.2: Source Management & Book System
Tests all endpoints for materials and books management
"""

import sys
import os
import asyncio
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir.parent))

# Test imports - use absolute imports
try:
    from backend.models import physics_books, materials, book_chunks
    from backend.ai import ocr_processor, content_extractor, source_prioritizer, citation_manager, book_ingest
    from backend.utils.database import get_database, init_database
    print("✅ All imports successful")
except ImportError:
    # Fallback to direct imports if backend is not a package
    try:
        import models.physics_books as physics_books
        import models.materials as materials
        import models.book_chunks as book_chunks
        import ai.ocr_processor as ocr_processor
        import ai.content_extractor as content_extractor
        import ai.source_prioritizer as source_prioritizer
        import ai.citation_manager as citation_manager
        import ai.book_ingest as book_ingest
        from utils.database import get_database, init_database
        print("✅ All imports successful (fallback)")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


def test_database_connection():
    """Test database connectivity"""
    print("\n📊 Testing Database Connection...")
    try:
        success = init_database()
        if success:
            db = get_database()
            collections = db.list_collection_names()
            print(f"✅ Database connected. Collections: {len(collections)}")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


def test_materials_model():
    """Test materials model functionality"""
    print("\n📄 Testing Materials Model...")
    try:
        # Test creating a material
        doc = {
            'user_id': 'test_user_123',
            'title': 'Test Physics Notes',
            'material_type': 'notes',
            'content': 'Newton\'s laws of motion govern the relationship between force and motion.',
            'upload_metadata': {
                'file_name': 'test_notes.txt',
                'file_type': '.txt',
                'processing_status': 'completed'
            }
        }
        
        material_id = materials.create_material(doc)
        print(f"✅ Material created with ID: {material_id}")
        
        # Test listing materials
        user_materials = materials.list_materials_for_user('test_user_123', limit=10)
        print(f"✅ Found {len(user_materials)} materials for test user")
        
        return True
    except Exception as e:
        print(f"❌ Materials model test failed: {e}")
        return False


def test_books_model():
    """Test physics books model functionality"""
    print("\n📚 Testing Physics Books Model...")
    try:
        db = get_database()
        
        # Test creating a book
        book = physics_books.create_book(
            db,
            title="Classical Mechanics",
            author="Herbert Goldstein",
            edition="3rd Edition",
            subject_areas=["mechanics", "classical_physics"],
            source_url="https://example.com/goldstein"
        )
        print(f"✅ Book created: {book.get('title')}")
        
        book_id = book['_id']
        
        # Test retrieving book
        retrieved_book = physics_books.get_book(db, book_id)
        print(f"✅ Book retrieved: {retrieved_book.get('title')}")
        
        # Test listing books
        all_books = physics_books.list_books(db, limit=10)
        print(f"✅ Found {len(all_books)} books")
        
        # Test updating book status
        physics_books.update_book_status(db, book_id, 'processed')
        updated_book = physics_books.get_book(db, book_id)
        print(f"✅ Book status updated to: {updated_book.get('processing_status')}")
        
        return True
    except Exception as e:
        print(f"❌ Books model test failed: {e}")
        return False


def test_ocr_processor():
    """Test OCR processor functionality"""
    print("\n🔍 Testing OCR Processor...")
    try:
        # Create a test text file
        test_file = Path('/tmp/test_physics.txt')
        test_file.write_text("F = ma\nNewton's Second Law of Motion")
        
        # Test OCR on text file
        result = ocr_processor.ocr_file(str(test_file))
        
        if 'text' in result and 'pages' in result:
            print(f"✅ OCR processed text file: {len(result['text'])} chars")
            print(f"   Pages extracted: {len(result['pages'])}")
            return True
        else:
            print("❌ OCR result missing expected fields")
            return False
    except Exception as e:
        print(f"❌ OCR processor test failed: {e}")
        return False


def test_content_extractor():
    """Test content extraction and chunking"""
    print("\n✂️ Testing Content Extractor...")
    try:
        # Test text chunking
        test_text = """
        Newton's laws of motion are three physical laws that describe the relationship 
        between the motion of an object and the forces acting on it. The first law states 
        that an object at rest stays at rest and an object in motion stays in motion with 
        the same speed and in the same direction unless acted upon by an unbalanced force.
        The second law states that the acceleration of an object depends on the mass of 
        the object and the amount of force applied. The third law states that for every 
        action there is an equal and opposite reaction.
        """
        
        chunks = content_extractor.chunk_text(test_text, max_tokens=50, overlap=10)
        print(f"✅ Text chunked into {len(chunks)} pieces")
        
        for i, chunk in enumerate(chunks[:2]):  # Show first 2 chunks
            print(f"   Chunk {i+1}: {chunk['words']} words, ID: {chunk['chunk_id'][:8]}...")
        
        return True
    except Exception as e:
        print(f"❌ Content extractor test failed: {e}")
        return False


async def test_embedding_and_indexing():
    """Test embedding generation and indexing"""
    print("\n🔢 Testing Embedding and Indexing...")
    try:
        # Test embedding chunks
        test_chunks = [
            {
                'chunk_id': 'test_chunk_1',
                'text': 'F = ma is Newton\'s second law of motion',
                'words': 8,
                'start_word': 0,
                'end_word': 7
            },
            {
                'chunk_id': 'test_chunk_2',
                'text': 'Energy cannot be created or destroyed',
                'words': 7,
                'start_word': 0,
                'end_word': 6
            }
        ]
        
        embedded_chunks = await content_extractor.embed_chunks(test_chunks, use_cache=False)
        
        if embedded_chunks and len(embedded_chunks) > 0:
            print(f"✅ Embedded {len(embedded_chunks)} chunks")
            for chunk in embedded_chunks[:2]:
                emb_len = len(chunk.get('embedding', []))
                error = chunk.get('embedding_error')
                if emb_len > 0:
                    print(f"   Chunk {chunk['chunk_id']}: {emb_len}-dim embedding")
                else:
                    print(f"   Chunk {chunk['chunk_id']}: Error - {error}")
            return True
        else:
            print("❌ No embeddings generated")
            return False
    except Exception as e:
        print(f"❌ Embedding test failed: {e}")
        return False


def test_source_prioritizer():
    """Test source prioritization algorithm"""
    print("\n🎯 Testing Source Prioritizer...")
    try:
        # Mock sources
        user_materials = [
            {'_id': 'mat1', 'title': 'My Notes', 'content': 'Personal notes', 'priority': 1.0}
        ]
        preferred_books = [
            {'id': 'book1', 'title': 'Classical Mechanics', 'priority': 0.8}
        ]
        knowledge_results = [
            {'id': 'kb1', 'title': 'Physics Knowledge', 'score': 0.75, 'text': 'Some physics content'}
        ]
        general_sources = [
            {'id': 'gen1', 'title': 'General Source', 'score': 0.3}
        ]
        
        prioritized = source_prioritizer.prioritize_sources(
            user_materials, 
            preferred_books, 
            knowledge_results, 
            general_sources,
            top_k=10
        )
        
        print(f"✅ Prioritized {len(prioritized)} sources")
        for i, source in enumerate(prioritized[:3]):
            print(f"   {i+1}. Type: {source['type']}, Score: {source['score']:.2f}")
        
        # Verify priority order
        expected_order = ['user_material', 'book', 'knowledge', 'general']
        actual_order = [s['type'] for s in prioritized]
        
        if actual_order == expected_order[:len(actual_order)]:
            print("✅ Sources correctly prioritized by type")
            return True
        else:
            print(f"❌ Unexpected priority order: {actual_order}")
            return False
    except Exception as e:
        print(f"❌ Source prioritizer test failed: {e}")
        return False


def test_citation_manager():
    """Test citation generation"""
    print("\n📝 Testing Citation Manager...")
    try:
        # Mock prioritized sources
        sources = [
            {
                'id': 'book1',
                'type': 'book',
                'score': 0.9,
                'metadata': {
                    'title': 'Classical Mechanics',
                    'author': 'Herbert Goldstein'
                }
            },
            {
                'id': 'mat1',
                'type': 'user_material',
                'score': 0.95,
                'metadata': {
                    'title': 'Personal Physics Notes'
                }
            }
        ]
        
        citations = citation_manager.generate_citations(sources)
        
        print(f"✅ Generated {len(citations)} citations")
        for citation in citations:
            print(f"   - {citation.get('citation_text', citation.get('citation', 'N/A'))}")
        
        return True
    except Exception as e:
        print(f"❌ Citation manager test failed: {e}")
        return False


def test_book_chunks_model():
    """Test book chunks model"""
    print("\n📦 Testing Book Chunks Model...")
    try:
        db = get_database()
        
        # Create a test book first
        book = physics_books.create_book(
            db,
            title="Test Book for Chunks",
            author="Test Author"
        )
        book_id = book['_id']
        
        # Insert test chunks
        chunk1 = {
            'book_id': book_id,
            'page': 1,
            'chunk_index': 0,
            'chunk_id': 'test_chunk_001',
            'text': 'This is test chunk 1',
            'text_snippet': 'This is test...',
            'metadata': {'start_word': 0, 'end_word': 5}
        }
        
        chunk_id = book_chunks.insert_chunk(db, chunk1)
        print(f"✅ Chunk inserted with ID: {chunk_id}")
        
        # List chunks for book
        chunks = book_chunks.list_chunks_for_book(db, book_id, limit=10)
        print(f"✅ Found {len(chunks)} chunks for book")
        
        return True
    except Exception as e:
        print(f"❌ Book chunks test failed: {e}")
        return False


def run_all_tests():
    """Run all Phase 7.2 tests"""
    print("=" * 70)
    print("🧪 PHASE 7.2 TEST SUITE: Source Management & Book System")
    print("=" * 70)
    
    results = []
    
    # Database tests
    results.append(("Database Connection", test_database_connection()))
    
    # Model tests
    results.append(("Materials Model", test_materials_model()))
    results.append(("Books Model", test_books_model()))
    results.append(("Book Chunks Model", test_book_chunks_model()))
    
    # Processing tests
    results.append(("OCR Processor", test_ocr_processor()))
    results.append(("Content Extractor", test_content_extractor()))
    
    # Async tests
    print("\n🔄 Running async tests...")
    loop = asyncio.get_event_loop()
    results.append(("Embedding & Indexing", loop.run_until_complete(test_embedding_and_indexing())))
    
    # Algorithm tests
    results.append(("Source Prioritizer", test_source_prioritizer()))
    results.append(("Citation Manager", test_citation_manager()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
