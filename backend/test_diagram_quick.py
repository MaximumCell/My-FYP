#!/usr/bin/env python3
"""
Quick test for diagram generation functionality
"""
import os
import asyncio
from pathlib import Path

# Set up path
import sys
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from ai.enhanced_physics_tutor import EnhancedPhysicsAITutor

async def test_diagram():
    """Test diagram generation"""
    print("🧪 Testing Diagram Generation\n")
    
    # Check API key (try both for compatibility)
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ API key not set in environment")
        print("   Set GEMINI_API_KEY or GOOGLE_API_KEY")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Initialize tutor
    print("\n🔄 Initializing Physics AI Tutor...")
    tutor = EnhancedPhysicsAITutor()
    print("✅ Tutor initialized")
    
    # Test diagram generation
    print("\n🎨 Generating electric field diagram...")
    result = await tutor.generate_physics_diagram(
        description="Electric field lines around a positive point charge",
        diagram_type="field",
        style="educational",
        include_labels=True
    )
    
    if result.get('success'):
        print("✅ Diagram generated successfully!")
        print(f"   - Type: {result.get('diagram_type')}")
        print(f"   - Style: {result.get('style')}")
        print(f"   - Has Base64: {bool(result.get('image_base64'))}")
        print(f"   - Image URL: {result.get('image_url')}")
        print(f"   - Explanation: {result.get('explanation', 'N/A')[:100]}...")
        
        # Check if file exists
        if result.get('image_url'):
            image_path = backend_dir / result['image_url'].replace('/static/', 'static/')
            if image_path.exists():
                print(f"✅ Image file saved: {image_path}")
                print(f"   - File size: {image_path.stat().st_size} bytes")
            else:
                print(f"⚠️  Image file not found: {image_path}")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    print("\n✨ Test complete!")

if __name__ == '__main__':
    asyncio.run(test_diagram())
