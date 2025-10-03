#!/usr/bin/env python3
"""
Test script for enhanced physics tutor optimizations
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from ai.enhanced_physics_tutor import EnhancedPhysicsAITutor

async def test_optimizations():
    """Test the optimizations"""
    print("🧪 Testing Enhanced Physics Tutor Optimizations")
    print("=" * 60)
    
    # Create tutor instance
    tutor = EnhancedPhysicsAITutor()
    
    # Test 1: Greeting should skip context retrieval
    print("\n1️⃣ Testing greeting detection (should skip retrieval)...")
    response1 = await tutor.ask_physics_question(
        question="hi",
        session_id="test_session_1"
    )
    print(f"✅ Response: {response1['answer'][:100]}...")
    print(f"📊 Context items used: {response1['context_items_used']} (should be 0)")
    
    # Test 2: Real physics question
    print("\n2️⃣ Testing real physics question with session...")
    response2 = await tutor.ask_physics_question(
        question="what is quantum coherence",
        session_id="test_session_1",
        difficulty_level="intermediate"
    )
    print(f"✅ Success: {response2['success']}")
    if response2['success']:
        print(f"📝 Answer preview: {response2['answer'][:150]}...")
        print(f"📊 Context items: {response2['context_items_used']}")
        print(f"⏱️ Processing time: {response2['response_metadata']['processing_time']:.3f}s")
    else:
        print(f"❌ Error: {response2.get('error')}")
    
    # Test 3: Follow-up question (should use session history)
    print("\n3️⃣ Testing follow-up with session context...")
    response3 = await tutor.ask_physics_question(
        question="can you explain more about that",
        session_id="test_session_1"
    )
    print(f"✅ Response generated")
    print(f"💾 Session has {len(tutor.session_history.get('test_session_1', []))} messages")
    
    # Test 4: Check statistics
    print("\n4️⃣ Checking tutor statistics...")
    stats = tutor.get_enhanced_stats()
    print(f"📈 Total queries: {stats['enhanced_tutor_stats']['total_enhanced_queries']}")
    print(f"📚 RAG queries: {stats['enhanced_tutor_stats']['rag_queries']}")
    print(f"⚡ Avg response time: {stats['enhanced_tutor_stats']['average_response_generation_time']:.3f}s")
    
    print("\n✅ All optimization tests completed!")

if __name__ == "__main__":
    asyncio.run(test_optimizations())
