"""
Phase 7.1 Setup and Testing Script
Initialize and test the Physics AI Tutor foundation components
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the path
sys.path.append('/home/itz_sensei/Documents/FypProject/backend')

async def test_database_connections():
    """Test MongoDB database connections and create indexes"""
    print("🔍 Testing database connections...")
    
    try:
        from models.physics_knowledge import physics_knowledge_db
        from models.response_evaluation import response_evaluation_db
        from models.physics_chat_session import physics_chat_session_db
        
        # Test physics knowledge database
        print("  📚 Testing physics knowledge database...")
        test_knowledge = {
            "content_type": "concept",
            "topic": "mechanics",
            "subtopic": "kinematics",
            "content": {
                "title": "Test Concept",
                "concept_explanation": "This is a test physics concept.",
                "difficulty_level": 1
            },
            "source_info": {
                "book_reference": "Test Book",
                "author_credibility": 5
            }
        }
        
        # Insert test data
        result = physics_knowledge_db.collection.insert_one(test_knowledge)
        if result.inserted_id:
            print("    ✅ Physics knowledge database connected successfully")
            # Clean up test data
            physics_knowledge_db.collection.delete_one({"_id": result.inserted_id})
        else:
            print("    ❌ Physics knowledge database connection failed")
        
        # Test response evaluation database
        print("  📊 Testing response evaluation database...")
        # Just test connection by counting documents
        count = response_evaluation_db.collection.count_documents({})
        print(f"    ✅ Response evaluation database connected (contains {count} evaluations)")
        
        # Test chat session database
        print("  💬 Testing chat session database...")
        count = physics_chat_session_db.collection.count_documents({})
        print(f"    ✅ Chat session database connected (contains {count} sessions)")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Database connection error: {e}")
        return False


async def test_ai_integration():
    """Test AI models and integration"""
    print("🤖 Testing AI integration...")
    
    try:
        # Check if API keys are configured
        gemini_key = os.getenv('GEMINI_API_KEY')
        if not gemini_key or gemini_key == 'your_gemini_api_key_here':
            print("    ⚠️  GEMINI_API_KEY not configured - AI features will not work")
            print("    💡 Please set your Gemini API key in .env file")
            return False
        
        from ai.physics_ai import physics_ai
        
        # Test question classification
        print("  🔍 Testing question classification...")
        test_question = "What is Newton's second law?"
        classification = await physics_ai.classify_question(test_question)
        
        if classification and 'category' in classification:
            print(f"    ✅ Question classification working: {classification.get('category')}")
        else:
            print("    ❌ Question classification failed")
            return False
        
        # Test basic response generation
        print("  💭 Testing AI response generation...")
        response = await physics_ai.generate_response(
            test_question, 
            response_length="short"
        )
        
        if response and 'content' in response and not response.get('error'):
            print("    ✅ AI response generation working")
            print(f"    📝 Sample response: {response['content'][:100]}...")
        else:
            print(f"    ❌ AI response generation failed: {response.get('error', 'Unknown error')}")
            return False
        
        # Test supervisor evaluation
        print("  🎯 Testing AI supervisor evaluation...")
        evaluation = await physics_ai.evaluate_response(
            test_question,
            response['content']
        )
        
        if evaluation and 'overall_score' in evaluation:
            print(f"    ✅ AI supervisor evaluation working (score: {evaluation['overall_score']})")
        else:
            print("    ❌ AI supervisor evaluation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"    ❌ AI integration error: {e}")
        return False


async def test_latex_rendering():
    """Test LaTeX equation rendering"""
    print("🧮 Testing LaTeX rendering...")
    
    try:
        from ai.latex_renderer import latex_renderer
        
        # Test equation extraction
        print("  📐 Testing equation extraction...")
        test_text = "The famous equation is $E = mc^2$ and the quadratic formula is $$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$"
        
        equations = latex_renderer.extract_latex_equations(test_text)
        if len(equations) == 2:
            print(f"    ✅ Equation extraction working (found {len(equations)} equations)")
        else:
            print(f"    ⚠️  Equation extraction found {len(equations)} equations (expected 2)")
        
        # Test LaTeX validation
        print("  ✅ Testing LaTeX validation...")
        validation = latex_renderer.validate_latex("E = mc^2")
        if validation['valid']:
            print("    ✅ LaTeX validation working")
        else:
            print("    ❌ LaTeX validation failed")
        
        # Test equation rendering
        print("  🎨 Testing equation rendering...")
        render_result = latex_renderer.render_equation_to_image("E = mc^2")
        if render_result['success']:
            print("    ✅ Equation rendering working")
        else:
            print(f"    ❌ Equation rendering failed: {render_result.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ LaTeX rendering error: {e}")
        return False


async def test_physics_tutor_service():
    """Test the main physics tutor service"""
    print("🎓 Testing Physics Tutor Service...")
    
    try:
        from ai.physics_tutor_service import physics_tutor_service
        
        # Test session creation
        print("  📚 Testing chat session creation...")
        session_result = await physics_tutor_service.create_chat_session(
            user_id="test_user_123",
            learning_context={
                "difficulty_preference": "intermediate",
                "response_length_preference": "short",
                "learning_goals": ["understand mechanics"]
            }
        )
        
        if session_result['success']:
            session_id = session_result['session_id']
            print(f"    ✅ Chat session created: {session_id}")
            
            # Test question processing
            print("  🤔 Testing question processing...")
            question_result = await physics_tutor_service.process_physics_question(
                session_id=session_id,
                user_question="Explain Newton's first law of motion",
                response_length="short"
            )
            
            if question_result['success']:
                print("    ✅ Question processing working")
                print(f"    📊 Quality score: {question_result.get('quality_score', 'N/A')}")
                print(f"    ⚡ Processing time: {question_result.get('processing_time', 0):.2f}s")
                
                # Test analytics
                print("  📈 Testing session analytics...")
                analytics = physics_tutor_service.get_session_analytics(session_id)
                if analytics['success']:
                    print("    ✅ Session analytics working")
                else:
                    print("    ❌ Session analytics failed")
                
            else:
                print(f"    ❌ Question processing failed: {question_result.get('error')}")
                return False
        else:
            print(f"    ❌ Chat session creation failed: {session_result.get('error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"    ❌ Physics tutor service error: {e}")
        return False


async def create_sample_knowledge_base():
    """Create sample physics knowledge base entries"""
    print("📖 Creating sample knowledge base...")
    
    try:
        from models.physics_knowledge import physics_knowledge_db, PhysicsKnowledge, Content, SourceInfo, VisualAids
        
        sample_entries = [
            {
                "content_type": "concept",
                "topic": "mechanics",
                "subtopic": "laws_of_motion",
                "content": Content(
                    title="Newton's First Law of Motion",
                    concept_explanation="An object at rest stays at rest and an object in motion stays in motion with the same speed and in the same direction unless acted upon by an unbalanced force.",
                    key_formulas=["F_net = 0 ⟹ a = 0"],
                    examples=["A book on a table", "A hockey puck sliding on ice"],
                    prerequisites=["Force", "Inertia"],
                    difficulty_level=2
                ),
                "source_info": SourceInfo(
                    book_reference="Halliday, Resnick & Walker",
                    chapter="Chapter 5 - Force and Motion",
                    page_numbers=[95, 96, 97],
                    author_credibility=9
                ),
                "visual_aids": VisualAids(
                    equations_latex=["\\vec{F}_{net} = 0", "\\vec{a} = 0"],
                    diagram_descriptions=["Free body diagram showing balanced forces"],
                    graph_suggestions=["Velocity vs time graph showing constant velocity"]
                )
            },
            {
                "content_type": "formula",
                "topic": "mechanics",
                "subtopic": "kinematics",
                "content": Content(
                    title="Kinematic Equations",
                    concept_explanation="Equations describing motion with constant acceleration",
                    mathematical_derivation=[
                        "Start with a = (v - v₀)/t",
                        "Solve for v: v = v₀ + at",
                        "Average velocity: v_avg = (v₀ + v)/2",
                        "Distance: s = v_avg × t = (v₀ + v)t/2",
                        "Substitute v: s = v₀t + ½at²"
                    ],
                    key_formulas=[
                        "v = v₀ + at",
                        "s = v₀t + ½at²", 
                        "v² = v₀² + 2as"
                    ],
                    examples=["Ball thrown vertically", "Car accelerating from rest"],
                    prerequisites=["Velocity", "Acceleration", "Displacement"],
                    difficulty_level=3
                ),
                "source_info": SourceInfo(
                    book_reference="Physics for Scientists and Engineers",
                    chapter="Chapter 2 - Motion in One Dimension",
                    page_numbers=[45, 46, 47, 48],
                    author_credibility=10
                ),
                "visual_aids": VisualAids(
                    equations_latex=[
                        "v = v_0 + at",
                        "s = v_0 t + \\frac{1}{2}at^2",
                        "v^2 = v_0^2 + 2as"
                    ],
                    diagram_descriptions=["Position vs time parabolic curve", "Velocity vs time linear relationship"],
                    graph_suggestions=["x-t graph", "v-t graph", "a-t graph"]
                )
            }
        ]
        
        created_count = 0
        for entry_data in sample_entries:
            knowledge = PhysicsKnowledge(**entry_data)
            result = physics_knowledge_db.insert_knowledge(knowledge)
            if result:
                created_count += 1
        
        print(f"    ✅ Created {created_count}/{len(sample_entries)} sample knowledge entries")
        return True
        
    except Exception as e:
        print(f"    ❌ Error creating sample knowledge base: {e}")
        return False


async def run_phase_7_1_setup():
    """Run complete Phase 7.1 setup and testing"""
    print("🚀 Starting Phase 7.1: Foundation & Knowledge Base Setup")
    print("=" * 60)
    
    # Check environment variables
    print("⚙️  Checking environment configuration...")
    required_vars = ['MONGODB_URI', 'GEMINI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith('your_'):
            missing_vars.append(var)
        else:
            print(f"    ✅ {var} configured")
    
    if missing_vars:
        print(f"    ⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("    💡 Please configure these in your .env file")
        print("    📄 See .env file for required format")
    
    print()
    
    # Run all tests
    test_results = []
    
    # Database tests
    db_result = await test_database_connections()
    test_results.append(("Database Connections", db_result))
    print()
    
    # AI integration tests (only if API key is configured)
    if 'GEMINI_API_KEY' not in missing_vars:
        ai_result = await test_ai_integration()
        test_results.append(("AI Integration", ai_result))
    else:
        print("🤖 Skipping AI integration tests (API key not configured)")
        test_results.append(("AI Integration", False))
    print()
    
    # LaTeX rendering tests
    latex_result = await test_latex_rendering()
    test_results.append(("LaTeX Rendering", latex_result))
    print()
    
    # Physics tutor service tests (only if AI is working)
    if 'GEMINI_API_KEY' not in missing_vars and test_results[-2][1]:  # AI integration passed
        service_result = await test_physics_tutor_service()
        test_results.append(("Physics Tutor Service", service_result))
    else:
        print("🎓 Skipping Physics Tutor Service tests (dependencies not ready)")
        test_results.append(("Physics Tutor Service", False))
    print()
    
    # Create sample knowledge base
    if test_results[0][1]:  # Database connection passed
        knowledge_result = await create_sample_knowledge_base()
        test_results.append(("Sample Knowledge Base", knowledge_result))
    else:
        print("📖 Skipping sample knowledge base creation (database not ready)")
        test_results.append(("Sample Knowledge Base", False))
    
    print()
    print("=" * 60)
    print("📊 PHASE 7.1 SETUP RESULTS")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed_tests += 1
    
    print()
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 Phase 7.1 setup completed successfully!")
        print("🔥 Ready to proceed to Phase 7.2!")
    elif passed_tests >= total_tests // 2:
        print("⚠️  Phase 7.1 partially completed")
        print("💡 Please address the failed tests before proceeding")
    else:
        print("❌ Phase 7.1 setup needs attention")
        print("🔧 Please fix configuration issues and try again")
    
    print()
    print("Next steps:")
    print("1. 🔑 Ensure all API keys are properly configured")
    print("2. 📚 Install required dependencies: pip install -r requirements.txt")
    print("3. 🗄️  Verify MongoDB Atlas connection and setup")
    print("4. 🧪 Run this script again to verify all tests pass")
    print("5. 📋 Proceed to Phase 7.2 implementation")


if __name__ == "__main__":
    # Run the setup
    asyncio.run(run_phase_7_1_setup())