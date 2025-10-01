# Phase 7.2 API Quick Reference

## 📤 Materials Management

### Upload Material

```bash
POST /api/materials/upload
Headers: X-User-ID: <user_id>
Form Data:
  - file: <PDF/Image file>
  - title: <Material title>
  - material_type: <notes/textbook/paper>

Response: { success: true, id: <material_id>, processing_status: "completed" }
```

### List Materials

```bash
GET /api/materials/list?user_id=<user_id>
Response: { success: true, materials: [...] }
```

### Get Material

```bash
GET /api/materials/<material_id>?user_id=<user_id>
Response: { success: true, material: {...} }
```

### Delete Material

```bash
DELETE /api/materials/<material_id>
Headers: X-User-ID: <user_id>
Response: { success: true, message: "Material deleted successfully" }
```

### Re-process Material

```bash
POST /api/materials/<material_id>/process
Headers: X-User-ID: <user_id>
Response: { success: true, message: "Processing started" }
```

---

## 📚 Books Management

### Register Book

```bash
POST /api/books/add
Body: {
  "title": "Classical Mechanics",
  "author": "Herbert Goldstein",
  "edition": "3rd Edition",
  "subject_areas": ["mechanics", "classical_physics"],
  "source_url": "https://..."
}
Response: { book: {...} }
```

### Process Book

```bash
POST /api/books/process
Body: {
  "book_id": "<book_id>",
  "file_path": "/path/to/book.pdf",
  "dry_run": false
}
Response: { status: "processing_started", book_id: "<book_id>" }
```

### List Books

```bash
GET /api/books/list?limit=50
Response: { success: true, books: [...] }
```

### Get Book Recommendations

```bash
GET /api/books/recommend?topic=mechanics&difficulty=undergraduate&limit=5
Response: {
  success: true,
  recommendations: [...],
  topic: "mechanics",
  difficulty: "undergraduate"
}
```

### Select Preferred Book

```bash
POST /api/books/select
Body: {
  "session_id": "<session_id>",
  "book_id": "<book_id>"
}
Response: {
  success: true,
  session_id: "<session_id>",
  book_id: "<book_id>",
  book_title: "Classical Mechanics"
}
```

### Search Books

```bash
GET /api/books/search?q=quantum&limit=20
Response: {
  success: true,
  results: [...],
  query: "quantum",
  count: 10
}
```

### Get Book Content

```bash
GET /api/books/content/<book_id>?limit=50
Response: {
  success: true,
  book: {...},
  chunks: [...],
  total_chunks: 150
}
```

---

## 🔧 Python Code Examples

### Upload Material (Python)

```python
import requests

files = {'file': open('physics_notes.pdf', 'rb')}
data = {
    'title': 'My Physics Notes',
    'material_type': 'notes'
}
headers = {'X-User-ID': 'user123'}

response = requests.post(
    'http://localhost:5000/api/materials/upload',
    files=files,
    data=data,
    headers=headers
)
print(response.json())
```

### Get Book Recommendations (Python)

```python
import requests

response = requests.get(
    'http://localhost:5000/api/books/recommend',
    params={
        'topic': 'quantum_mechanics',
        'difficulty': 'graduate',
        'limit': 5
    }
)
recommendations = response.json()['recommendations']
for book in recommendations:
    print(f"{book['title']} by {book['author']}")
```

### Search Books (Python)

```python
import requests

response = requests.get(
    'http://localhost:5000/api/books/search',
    params={'q': 'relativity', 'limit': 10}
)
results = response.json()['results']
for book in results:
    print(f"📚 {book['title']} - {book.get('author', 'Unknown')}")
```

---

## 🧪 Testing Endpoints

### Test with curl

```bash
# Upload
curl -X POST http://localhost:5000/api/materials/upload \
  -H "X-User-ID: test_user" \
  -F "file=@test.pdf" \
  -F "title=Test Material"

# List
curl "http://localhost:5000/api/materials/list?user_id=test_user"

# Recommend
curl "http://localhost:5000/api/books/recommend?topic=mechanics&limit=5"

# Search
curl "http://localhost:5000/api/books/search?q=physics"
```

### Test with Python requests

```python
import requests

BASE_URL = "http://localhost:5000"

# Test upload
with open('test.pdf', 'rb') as f:
    resp = requests.post(
        f"{BASE_URL}/api/materials/upload",
        files={'file': f},
        data={'title': 'Test'},
        headers={'X-User-ID': 'test_user'}
    )
    print("Upload:", resp.json())

# Test list
resp = requests.get(
    f"{BASE_URL}/api/materials/list",
    params={'user_id': 'test_user'}
)
print("Materials:", resp.json())

# Test recommend
resp = requests.get(
    f"{BASE_URL}/api/books/recommend",
    params={'topic': 'mechanics', 'limit': 3}
)
print("Recommendations:", resp.json())
```

---

## 📊 Response Formats

### Success Response

```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed"
}
```

### Error Response

```json
{
  "success": false,
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

### Material Object

```json
{
  "id": "material_id",
  "user_id": "user123",
  "title": "Physics Notes",
  "material_type": "notes",
  "content": "Extracted text...",
  "upload_metadata": {
    "file_name": "notes.pdf",
    "file_type": ".pdf",
    "processing_status": "completed"
  },
  "created_at": "2025-10-01T12:00:00Z"
}
```

### Book Object

```json
{
  "id": "book_id",
  "title": "Classical Mechanics",
  "author": "Herbert Goldstein",
  "edition": "3rd Edition",
  "subject_areas": ["mechanics", "classical_physics"],
  "processing_status": "processed",
  "chunks_count": 150,
  "popularity_score": 0,
  "created_at": "2025-10-01T12:00:00Z"
}
```

---

## 🎯 Common Use Cases

### 1. Student Uploads Study Material

```python
# Upload PDF notes
response = upload_material(
    user_id="student123",
    file_path="quantum_notes.pdf",
    title="Quantum Mechanics Notes",
    material_type="notes"
)

# Material is automatically:
# - OCR processed
# - Chunked
# - Embedded
# - Indexed in vector DB
```

### 2. Get Personalized Book Recommendations

```python
# Get recommendations for specific topic
books = get_recommendations(
    topic="thermodynamics",
    difficulty="undergraduate",
    limit=5
)

# Returns books ranked by:
# - Subject area match
# - Difficulty level
# - Popularity score
```

### 3. Set Preferred Reference Book

```python
# Select preferred book for session
select_book(
    session_id="session123",
    book_id="book456"
)

# AI will prioritize this book when answering questions
```

### 4. Search for Specific Books

```python
# Search by keyword
results = search_books(
    query="einstein relativity",
    limit=10
)

# Searches in:
# - Title
# - Author
# - Subject areas
```

---

## 🔐 Authentication

All endpoints require user identification via:

- Header: `X-User-ID: <user_id>`, OR
- Query param: `?user_id=<user_id>`, OR
- Form data: `user_id=<user_id>`

---

## 📝 Notes

1. **File Size Limits:** Max 10MB per upload (configurable)
2. **Supported Formats:** PDF, PNG, JPG, JPEG, TIFF, TXT
3. **OCR Language:** English (can be configured)
4. **Processing Time:**
   - Upload: Immediate response
   - OCR: Background processing (check status)
   - Book processing: Async (status endpoint coming)
5. **Rate Limits:** None currently (add if needed)

---

**Quick Reference Version:** 1.0  
**Last Updated:** October 1, 2025  
**Phase:** 7.2 Complete ✅
