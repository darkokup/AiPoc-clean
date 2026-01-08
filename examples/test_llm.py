"""Test LLM integration for protocol generation."""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_llm_availability():
    """Test if LLM service is available."""
    print("\n" + "="*60)
    print("TEST 1: LLM Availability")
    print("="*60)
    
    try:
        from app.services.llm_service import is_llm_available
        
        available = is_llm_available()
        if available:
            print("✅ LLM is configured and ready!")
        else:
            print("❌ LLM not available")
            print("\nTo enable LLM:")
            print("1. Get API key from https://platform.openai.com/")
            print("2. Create .env file with: OPENAI_API_KEY=sk-your-key")
            print("3. Run: pip install openai")
        
        assert available, "LLM is not available"
    except ImportError as e:
        print(f"❌ OpenAI package not installed: {e}")
        print("\nInstall with: pip install openai")
        assert False, "OpenAI package not installed"
    except Exception as e:
        print(f"❌ Error: {e}")
        assert False, f"LLM availability check failed: {e}"


def test_llm_objectives():
    """Test LLM objective generation."""
    print("\n" + "="*60)
    print("TEST 2: LLM Objective Generation")
    print("="*60)
    
    try:
        from app.services.llm_service import get_llm_service
        
        llm = get_llm_service()
        
        trial_spec = {
            "title": "Phase II Study of Novel Therapy in Type 2 Diabetes",
            "phase": "Phase II",
            "indication": "Type 2 Diabetes Mellitus",
            "design": "Randomized, double-blind, placebo-controlled"
        }
        
        print("\n📋 Trial Specification:")
        for key, value in trial_spec.items():
            print(f"  {key}: {value}")
        
        print("\n🤖 Calling OpenAI GPT-4o...")
        objectives = llm.generate_objectives(trial_spec)
        
        print("\n✅ Generated Objectives:")
        print(f"\n📍 Primary Objective:")
        print(f"  {objectives['primary']}")
        print(f"\n📍 Secondary Objective:")
        print(f"  {objectives['secondary']}")
        
        assert 'primary' in objectives, "Missing primary objective"
        assert 'secondary' in objectives, "Missing secondary objective"
        
    except ValueError as e:
        if "API key not configured" in str(e):
            print("❌ OpenAI API key not configured")
            print("\nSet OPENAI_API_KEY in .env file")
            assert False, "OpenAI API key not configured"
        raise
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Objective generation failed: {e}"


def test_llm_inclusion_criteria():
    """Test LLM inclusion criteria generation."""
    print("\n" + "="*60)
    print("TEST 3: LLM Inclusion Criteria Generation")
    print("="*60)
    
    try:
        from app.services.llm_service import get_llm_service
        
        llm = get_llm_service()
        
        trial_spec = {
            "phase": "Phase III",
            "indication": "Hypertension",
            "design": "Multicenter, randomized controlled trial"
        }
        
        print("\n📋 Trial Specification:")
        for key, value in trial_spec.items():
            print(f"  {key}: {value}")
        
        print("\n🤖 Calling OpenAI GPT-4o...")
        criteria = llm.generate_inclusion_criteria(trial_spec)
        
        print("\n✅ Generated Inclusion Criteria:")
        for i, criterion in enumerate(criteria, 1):
            print(f"  {i}. {criterion}")
        
        assert isinstance(criteria, list), "Criteria should be a list"
        assert len(criteria) > 0, "Should generate at least one criterion"
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Inclusion criteria generation failed: {e}"


def test_generator_with_llm():
    """Test full generator with LLM enabled."""
    print("\n" + "="*60)
    print("TEST 4: Protocol Generator with LLM")
    print("="*60)
    
    try:
        from app.services.generator import ProtocolTemplateGenerator
        from app.models.schemas import TrialSpecInput, TrialPhase, TrialEndpoint, EndpointType
        
        # Initialize generator with LLM enabled
        print("\n🔧 Initializing generator with LLM enabled...")
        generator = ProtocolTemplateGenerator(use_rag=True, use_llm=True)
        
        # Create trial spec
        spec = TrialSpecInput(
            title="Phase II Randomized Study of AI-Enhanced Oncology Treatment",
            sponsor="AI Research Institute",
            phase=TrialPhase.PHASE_2,
            indication="Advanced Non-Small Cell Lung Cancer",
            design="Randomized, open-label, two-arm",
            sample_size=120,
            duration_weeks=48,
            treatment_arms=["Experimental Therapy", "Standard of Care"],
            key_endpoints=[
                TrialEndpoint(
                    type=EndpointType.PRIMARY,
                    name="Objective Response Rate",
                    description="ORR by RECIST v1.1 at Week 24"
                ),
                TrialEndpoint(
                    type=EndpointType.SECONDARY,
                    name="Progression-Free Survival",
                    description="PFS from randomization to progression or death"
                )
            ],
            inclusion_criteria=[
                "Age ≥18 years",
                "Histologically confirmed NSCLC"
            ],
            exclusion_criteria=[
                "Prior systemic therapy for advanced disease",
                "Active brain metastases"
            ],
            region="US/EU"
        )
        
        print("\n📋 Generating protocol...")
        protocol = generator.generate_structured_protocol(spec)
        
        print("\n✅ Protocol Generated Successfully!")
        print(f"\n📄 Protocol ID: {protocol.protocol_id}")
        print(f"📝 Title: {protocol.title}")
        print(f"🏥 Sponsor: {protocol.sponsor}")
        print(f"📊 Phase: {protocol.phase}")
        
        print(f"\n🎯 Objectives:")
        print(f"  Primary: {protocol.objectives['primary'][:100]}...")
        print(f"  Secondary: {protocol.objectives['secondary'][:100]}...")
        
        assert protocol.protocol_id, "Protocol should have an ID"
        assert protocol.title, "Protocol should have a title"
        assert 'primary' in protocol.objectives, "Protocol should have primary objective"
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Protocol generation with LLM failed: {e}"


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 LLM INTEGRATION TEST SUITE")
    print("="*60)
    print("\nThis tests OpenAI LLM integration for AI-enhanced protocol generation.")
    
    results = []
    
    # Test 1: Check availability
    results.append(("LLM Availability", test_llm_availability()))
    
    if not results[0][1]:
        print("\n⚠️  LLM not available. Skipping remaining tests.")
        print("\nQuick Setup:")
        print("  1. pip install openai")
        print("  2. Create .env file with OPENAI_API_KEY=sk-...")
        print("  3. Run this test again")
        return
    
    # Test 2: Objectives
    results.append(("Objective Generation", test_llm_objectives()))
    
    # Test 3: Inclusion criteria
    results.append(("Inclusion Criteria", test_llm_inclusion_criteria()))
    
    # Test 4: Full generator
    results.append(("Full Protocol Generation", test_generator_with_llm()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\n🎯 Results: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! LLM integration is working perfectly!")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")


if __name__ == "__main__":
    main()
