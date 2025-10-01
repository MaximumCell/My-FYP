# Phase 7.3 API Quick Reference

## Physics Advanced Endpoints

Base URL: `http://localhost:5000/api/physics`

---

## 1. Enhanced Physics Question

**POST** `/api/physics/ask`

Ask a physics question with all advanced features (derivations, adaptations, follow-ups).

### Request

```json
{
  "question": "Explain Newton's second law",
  "user_id": "user123",
  "session_id": "session_456", // optional
  "preferences": {
    "length": "short|medium|long", // optional, default: medium
    "level": "beginner|intermediate|advanced" // optional, default: intermediate
  }
}
```

### Response

```json
{
  "success": true,
  "response": {
    "content": "Explanation text...",
    "formatted": "Formatted with steps if derivation...",
    "steps": [...],
    "complexity_level": "intermediate",
    "response_length": "medium"
  },
  "metadata": {
    "topic": "mechanics",
    "query_type": "concept",
    "sources_used": 3,
    "quality_score": 8.0,
    "key_concepts": ["force", "mass", "acceleration"]
  },
  "learning_aids": {
    "follow_up_questions": [
      "How does this apply to rotational motion?",
      "What happens in non-inertial reference frames?"
    ],
    "prerequisites": ["basic_physics", "algebra"],
    "key_equations": ["F = ma"]
  },
  "citations": [...],
  "session_id": "session_456",
  "timestamp": "2025-10-01T12:00:00"
}
```

---

## 2. Quick Ask (Fast Mode)

**POST** `/api/physics/quick-ask`

Get a quick answer without advanced features (faster response).

### Request

```json
{
  "question": "What is momentum?",
  "length": "short|medium|long" // optional, default: medium
}
```

### Response

```json
{
  "success": true,
  "answer": "Momentum is the product of mass and velocity...",
  "classification": {
    "category": "concept_explanation",
    "topic": "mechanics"
  },
  "context_items_used": 3
}
```

---

## 3. Step-by-Step Derivation

**POST** `/api/physics/derivation`

Request a complete derivation with steps.

### Request

```json
{
  "concept": "conservation of energy",
  "user_id": "user123",
  "level": "beginner|intermediate|advanced" // optional, default: intermediate
}
```

### Response

```json
{
  "success": true,
  "response": {
    "content": "Full derivation...",
    "steps": [
      { "step_number": 1, "content": "Start with work-energy theorem..." },
      { "step_number": 2, "content": "Integrate force over distance..." },
      { "step_number": 3, "content": "Apply boundary conditions..." }
    ],
    "complexity_level": "intermediate"
  },
  "learning_aids": {
    "prerequisites": ["calculus", "classical_mechanics"],
    "key_equations": ["W = ∫F·dx", "KE = ½mv²"]
  }
}
```

---

## 4. Explain Concept at Level

**POST** `/api/physics/explain`

Get explanation tailored to specific difficulty level.

### Request

```json
{
  "concept": "quantum superposition",
  "level": "beginner|intermediate|advanced"
}
```

### Response

```json
{
  "success": true,
  "response": {
    "content": "Level-appropriate explanation...",
    "complexity_level": "beginner"
  },
  "learning_aids": {
    "follow_up_questions": [
      "How does this relate to wave-particle duality?",
      "What is the classical limit?"
    ]
  }
}
```

---

## 5. Get Statistics

**GET** `/api/physics/stats`

Get tutor performance statistics.

### Response

```json
{
  "success": true,
  "statistics": {
    "enhanced_tutor_stats": {
      "total_enhanced_queries": 150,
      "rag_queries": 120,
      "average_context_relevance": 0.85
    }
  }
}
```

---

## Response Length Modes

### Short (~150 words)

- Key concept (2-3 sentences)
- Essential formula
- One example
- Quick next step

### Medium (Standard)

- Balanced explanation
- Mathematical details
- Examples
- Related concepts

### Long (Comprehensive)

- Full context
- Complete derivation
- Multiple examples
- Applications
- Common misconceptions

---

## Complexity Levels

### Beginner

- Simplified language
- Reduced mathematical notation
- Basic concepts
- Analogies and examples

### Intermediate

- Standard technical terms
- Full equations
- Moderate depth
- Balanced rigor

### Advanced

- Full technical depth
- Mathematical rigor
- Advanced considerations
- Formal treatments

---

## Learning Aids Provided

### Follow-up Questions

- Context-aware suggestions
- Topic-specific questions
- Learning path recommendations

### Prerequisites

- Foundation topics needed
- Suggested learning order
- Background knowledge

### Key Equations

- Extracted LaTeX formulas
- Important relationships
- Mathematical expressions

---

## Error Responses

```json
{
  "success": false,
  "error": "Error description",
  "fallback": "Basic response mode activated"
}
```

---

## cURL Examples

### Enhanced Question

```bash
curl -X POST http://localhost:5000/api/physics/ask \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user123" \
  -d '{
    "question": "Derive kinetic energy formula",
    "preferences": {
      "length": "medium",
      "level": "intermediate"
    }
  }'
```

### Quick Ask

```bash
curl -X POST http://localhost:5000/api/physics/quick-ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is electric field?",
    "length": "short"
  }'
```

### Derivation

```bash
curl -X POST http://localhost:5000/api/physics/derivation \
  -H "Content-Type: application/json" \
  -d '{
    "concept": "Schrodinger equation",
    "user_id": "user123",
    "level": "advanced"
  }'
```

### Explain

```bash
curl -X POST http://localhost:5000/api/physics/explain \
  -H "Content-Type: application/json" \
  -d '{
    "concept": "entropy",
    "level": "beginner"
  }'
```

---

## Python Examples

```python
import requests

BASE_URL = "http://localhost:5000/api/physics"

# Enhanced question
response = requests.post(f"{BASE_URL}/ask", json={
    "question": "Explain momentum conservation",
    "user_id": "user123",
    "preferences": {
        "length": "medium",
        "level": "intermediate"
    }
})
result = response.json()

# Print response
print(result['response']['content'])
print("\nFollow-up questions:")
for q in result['learning_aids']['follow_up_questions']:
    print(f"  - {q}")

# Quick ask
response = requests.post(f"{BASE_URL}/quick-ask", json={
    "question": "What is force?",
    "length": "short"
})
print(response.json()['answer'])

# Request derivation
response = requests.post(f"{BASE_URL}/derivation", json={
    "concept": "wave equation",
    "level": "advanced"
})
steps = response.json()['response']['steps']
for step in steps:
    print(f"Step {step['step_number']}: {step['content']}")
```

---

## Integration with Phase 7.2

The Phase 7.3 endpoints automatically use:

- ✅ User-uploaded materials (Phase 7.2)
- ✅ Physics books database (Phase 7.2)
- ✅ Source prioritization (Phase 7.2)
- ✅ Citation generation (Phase 7.2)

Simply provide `user_id` and `session_id` to access personalized content!

---

**Version:** 1.0  
**Last Updated:** October 1, 2025  
**Status:** Production Ready ✅
