"""Test script for RAG (Retrieval-Augmented Generation) functionality."""
import requests
import json
import sys
import pytest


BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="module")
def generated_request_id():
    """Fixture to generate a protocol and return its request_id for other tests."""
    # Generate a test protocol
    spec = {
        "sponsor": "Test Pharma Inc",
        "title": "Test Protocol for RAG Integration",
        "indication": "Test Indication",
        "phase": "Phase 2",
        "design": "Randomized, Double-blind, Placebo-controlled",
        "sample_size": 100,
        "duration_weeks": 24,
        "region": "US",
        "key_endpoints": [
            {
                "type": "primary",
                "name": "Test Primary Endpoint",
                "description": "Change from baseline",
                "measurement_timepoint": "Week 24"
            }
        ],
        "inclusion_criteria": ["Age 18-65 years", "Confirmed diagnosis"],
        "exclusion_criteria": ["Pregnant or breastfeeding", "Active infection"]
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/generate", json=spec)
    if response.status_code == 201:
        result = response.json()
        return result['request_id']
    return None


def test_rag_seed():
    """Test seeding the RAG database with sample protocols."""
    print("\n=== Testing RAG Database Seeding ===")
    
    response = requests.post(f"{BASE_URL}/api/v1/rag/seed")
    
    print(f"Status: {response.status_code}")
    assert response.status_code == 200, f"Seeding failed: {response.text}"
    
    result = response.json()
    print(f"✓ Added: {result['added']} protocols")
    print(f"✓ Failed: {result['failed']} protocols")
    print(f"✓ Total examples: {result['total_examples']}")
    print(f"\nSeeded protocols:")
    for protocol in result['seeded_protocols']:
        print(f"  - {protocol['doc_id']}: {protocol['phase']} in {protocol['indication']}")
    
    assert result['total_examples'] > 0, "No protocols were seeded"


def test_rag_stats():
    """Test getting RAG database statistics."""
    print("\n=== Testing RAG Statistics ===")
    
    response = requests.get(f"{BASE_URL}/api/v1/rag/stats")
    
    print(f"Status: {response.status_code}")
    assert response.status_code == 200, f"Stats request failed: {response.text}"
    
    result = response.json()
    print(f"Total examples: {result['total_examples']}")
    print(f"\nBy Phase:")
    for phase, count in result['by_phase'].items():
        print(f"  {phase}: {count}")
    print(f"\nBy Indication:")
    for indication, count in result['by_indication'].items():
        print(f"  {indication}: {count}")
    
    assert 'total_examples' in result, "Response missing total_examples"
    assert 'by_phase' in result, "Response missing by_phase"
    assert 'by_indication' in result, "Response missing by_indication"


def test_rag_search():
    """Test searching for similar protocols."""
    print("\n=== Testing RAG Search ===")
    
    # Create a trial spec similar to rheumatology
    trial_spec = {
        "sponsor": "Test Sponsor",
        "title": "Phase II Study in Autoimmune Disease",
        "indication": "Rheumatoid Arthritis",
        "phase": "Phase 2",
        "design": "randomized, double-blind, placebo-controlled",
        "sample_size": 150,
        "duration_weeks": 24,
        "key_endpoints": [
            {
                "type": "primary",
                "name": "ACR20 response rate"
            }
        ],
        "inclusion_criteria": ["Age 18-75", "Active RA"],
        "exclusion_criteria": ["Prior biologic use"],
        "region": "US/EU"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/rag/search",
        json=trial_spec,
        params={"n_results": 3}
    )
    
    print(f"Status: {response.status_code}")
    assert response.status_code == 200, f"Search failed: {response.text}"
    
    result = response.json()
    print(f"Query: {result['query_summary']['phase']} in {result['query_summary']['indication']}")
    print(f"Found: {result['found']} similar protocol(s)\n")
    
    for i, protocol in enumerate(result['similar_protocols'], 1):
        print(f"{i}. {protocol['rag_doc_id']}")
        print(f"   Similarity: {protocol['similarity_score']:.1%}")
        summary = protocol['trial_spec_summary']
        print(f"   {summary['phase']} in {summary['indication']}")
        print(f"   Sample Size: {summary['sample_size']}, Duration: {summary['duration_weeks']} weeks")
    
    assert 'similar_protocols' in result, "Response missing similar_protocols"
    assert result['found'] >= 0, "Invalid found count"


def test_rag_enhanced_generation():
    """Test protocol generation with RAG enhancement."""
    print("\n=== Testing RAG-Enhanced Protocol Generation ===")
    
    # Create a trial spec
    trial_spec = {
        "sponsor": "Diabetes Research Inc",
        "title": "Phase II Study of Novel GLP-1 Agonist",
        "indication": "Type 2 Diabetes",
        "phase": "Phase 2",
        "design": "randomized, double-blind, placebo-controlled",
        "sample_size": 120,
        "duration_weeks": 26,
        "key_endpoints": [
            {
                "type": "primary",
                "name": "Change in HbA1c at week 26"
            }
        ],
        "inclusion_criteria": ["Age 18-75", "T2DM diagnosis"],
        "exclusion_criteria": ["Type 1 diabetes"],
        "region": "US"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/generate",
        json=trial_spec
    )
    
    print(f"Status: {response.status_code}")
    assert response.status_code == 201, f"Generation failed: {response.text}"
    
    result = response.json()
    print(f"✓ Generated protocol: {result['protocol_structured']['protocol_id']}")
    print(f"✓ Generation method: {result['generation_method']}")
    print(f"✓ Templates used: {', '.join(result['templates_used'])}")
    print(f"✓ Validation status: {result['validation_status']}")
    print(f"✓ Overall confidence: {result['overall_confidence']:.2f}")
    
    # Check if RAG context is in the narrative
    if "REFERENCE CONTEXT" in result['protocol_text']:
        print("\n✓ RAG context included in protocol narrative!")
    
    assert 'request_id' in result, "Response missing request_id"
    assert 'protocol_structured' in result, "Response missing protocol_structured"


def test_add_to_rag(generated_request_id):
    """Test adding a generated protocol to RAG database."""
    print("\n=== Testing Add Protocol to RAG ===")
    
    if not generated_request_id:
        pytest.skip("No request_id available from protocol generation")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/rag/add-example",
        params={"request_id": generated_request_id}
    )
    
    print(f"Status: {response.status_code}")
    assert response.status_code == 200, f"Add to RAG failed: {response.text}"
    
    result = response.json()
    print(f"✓ Added to RAG database")
    print(f"✓ RAG document ID: {result['rag_doc_id']}")
    print(f"✓ Total examples: {result['total_examples']}")
    
    assert 'rag_doc_id' in result, "Response missing rag_doc_id"
    assert 'total_examples' in result, "Response missing total_examples"


def test_list_examples():
    """Test listing all RAG examples."""
    print("\n=== Testing List RAG Examples ===")
    
    response = requests.get(f"{BASE_URL}/api/v1/rag/examples")
    
    print(f"Status: {response.status_code}")
    assert response.status_code == 200, f"List examples failed: {response.text}"
    
    result = response.json()
    print(f"Total examples: {result['total_count']}\n")
    
    for example in result['examples'][:5]:  # Show first 5
        metadata = example['metadata']
        print(f"- {example['id']}")
        print(f"  {metadata.get('phase')}: {metadata.get('indication')}")
    
    if result['total_count'] > 5:
        print(f"  ... and {result['total_count'] - 5} more")
    
    assert 'examples' in result, "Response missing examples"
    assert 'total_count' in result, "Response missing total_count"


def run_all_rag_tests():
    """Run all RAG tests in sequence (for command-line use)."""
    print("=" * 60)
    print("RAG (Retrieval-Augmented Generation) - Test Suite")
    print("=" * 60)
    print("Note: Use 'pytest' for proper test execution.")
    print("      This function is for manual command-line testing only.")
    print("=" * 60)
    
    tests = [
        ("Seed RAG Database", test_rag_seed),
        ("Get RAG Statistics", test_rag_stats),
        ("Search Similar Protocols", test_rag_search),
        ("List RAG Examples", test_list_examples),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, bool(result)))
        except Exception as e:
            print(f"\n✗ {name} failed with error: {e}")
            results.append((name, False))
    
    # Test RAG-enhanced generation
    try:
        result = test_rag_enhanced_generation()
        if result:
            results.append(("RAG-Enhanced Generation", True))
            
            # Test adding to RAG
            print("\n=== Testing Add Protocol to RAG ===")
            response = requests.post(
                f"{BASE_URL}/api/v1/rag/add-example",
                params={"request_id": result}
            )
            if response.status_code == 200:
                rag_result = response.json()
                print(f"✓ Added to RAG database")
                print(f"✓ Total examples: {rag_result['total_examples']}")
                results.append(("Add Generated Protocol to RAG", True))
            else:
                print(f"✗ Error: {response.text}")
                results.append(("Add Generated Protocol to RAG", False))
        else:
            results.append(("RAG-Enhanced Generation", False))
    except Exception as e:
        print(f"\n✗ Generation failed: {e}")
        results.append(("RAG-Enhanced Generation", False))
    
    print("\n" + "=" * 60)
    print("RAG Test Results Summary")
    print("=" * 60)
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "seed":
            test_rag_seed()
        elif command == "stats":
            test_rag_stats()
        elif command == "search":
            test_rag_search()
        elif command == "generate":
            test_rag_enhanced_generation()
        elif command == "list":
            test_list_examples()
        elif command == "all":
            run_all_rag_tests()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: seed, stats, search, generate, list, all")
    else:
        run_all_rag_tests()
