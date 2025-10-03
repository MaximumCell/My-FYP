#!/usr/bin/env python3
"""
Quick test script for physics diagram generation
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

async def test_diagram_generation():
    """Test the diagram generation feature"""
    print("🧪 Testing Physics Diagram Generation")
    print("=" * 60)
    
    # Test 1: Check if google-genai is installed
    print("\n1️⃣ Checking dependencies...")
    try:
        from google import genai
        from PIL import Image
        print("✅ google-genai: Installed")
        print("✅ Pillow: Installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\n📦 Please install:")
        print("   pip install google-genai Pillow")
        return False
    
    # Test 2: Check API key
    print("\n2️⃣ Checking API key...")
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        print(f"✅ API key found: {api_key[:10]}...")
    else:
        print("❌ GOOGLE_API_KEY not found in environment")
        print("   Set it with: export GOOGLE_API_KEY='your-key'")
        return False
    
    # Test 3: Check if EnhancedPhysicsAITutor has the method
    print("\n3️⃣ Checking EnhancedPhysicsAITutor...")
    try:
        from ai.enhanced_physics_tutor import EnhancedPhysicsAITutor
        tutor = EnhancedPhysicsAITutor()
        
        if hasattr(tutor, 'generate_physics_diagram'):
            print("✅ generate_physics_diagram method exists")
        else:
            print("❌ generate_physics_diagram method not found")
            return False
            
    except Exception as e:
        print(f"❌ Error loading tutor: {e}")
        return False
    
    # Test 4: Try to generate a simple diagram
    print("\n4️⃣ Generating test diagram...")
    try:
        result = await tutor.generate_physics_diagram(
            description="A simple force diagram showing weight and normal force on a box",
            diagram_type="force",
            style="educational"
        )
        
        if result.get('success'):
            print("✅ Diagram generated successfully!")
            print(f"📝 Explanation: {result['explanation'][:100]}...")
            print(f"💾 Saved to: {result.get('image_url', 'N/A')}")
            return True
        else:
            print(f"❌ Generation failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_diagram_generation())
    
    if success:
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("🚀 Diagram generation is ready to use!")
    else:
        print("\n" + "=" * 60)
        print("❌ TESTS FAILED")
        print("📋 Follow the instructions above to fix issues")
