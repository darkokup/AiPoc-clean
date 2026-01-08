"""Test script for API endpoints."""
import requests
import json
import sys
import pytest
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="module")
def generated_request_id():
    """Fixture to generate a protocol and return its request_id for export tests."""
    trial_spec = {
        "sponsor": "Test Sponsor",
        "title": "Test Clinical Trial Protocol",
        "indication": "Type 2 Diabetes Mellitus",
        "phase": "Phase 2",
        "design": "randomized, double-blind, placebo-controlled",
        "sample_size": 100,
        "duration_weeks": 24,
        "region": "US",
        "key_endpoints": [
            {
                "type": "primary",
                "name": "Change in HbA1c from baseline at Week 24"
            }
        ],
        "inclusion_criteria": ["Age 18-75 years", "Type 2 diabetes diagnosis"],
        "exclusion_criteria": ["Type 1 diabetes", "Pregnant or nursing"],
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/generate", json=trial_spec)
    if response.status_code == 201:
        result = response.json()
        return result['request_id']
    return None


def load_example_request() -> Dict[str, Any]:
    """Load example trial specification."""
    with open("examples/example_request.json", "r") as f:
        return json.load(f)


def test_health_check():
    """Test health check endpoint."""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200, f"Health check failed: {response.text}"


def test_validate():
    """Test validation endpoint."""
    print("\n=== Testing Validation ===")
    trial_spec = load_example_request()
    
    response = requests.post(
        f"{BASE_URL}/api/v1/validate",
        json=trial_spec,
    )
    
    print(f"Status: {response.status_code}")
    assert response.status_code == 200, f"Validation failed: {response.text}"
    
    result = response.json()
    print(f"Valid: {result['valid']}")
    print(f"Errors: {result['errors']}")
    print(f"Warnings: {result['warnings']}")
    print(f"Rules Checked: {len(result['rules_checked'])}")
    
    assert 'valid' in result, "Response missing valid field"
    assert 'errors' in result, "Response missing errors field"


def test_generate():
    """Test protocol generation endpoint."""
    print("\n=== Testing Protocol Generation ===")
    trial_spec = load_example_request()
    
    response = requests.post(
        f"{BASE_URL}/api/v1/generate",
        json=trial_spec,
    )
    
    print(f"Status: {response.status_code}")
    assert response.status_code == 201, f"Generation failed: {response.text}"
    
    result = response.json()
    print(f"Request ID: {result['request_id']}")
    print(f"Protocol ID: {result['protocol_structured']['protocol_id']}")
    print(f"Validation Status: {result['validation_status']}")
    print(f"Overall Confidence: {result['overall_confidence']:.2f}")
    print(f"Number of CRF Forms: {len(result['crf_schema']['forms'])}")
    print(f"Number of Visits: {len(result['crf_schema']['visits'])}")
    
    # Save request_id for export test
    with open("examples/last_request_id.txt", "w") as f:
        f.write(result['request_id'])
    
    # Save full response
    with open("examples/example_response.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
    
    print("\n✓ Full response saved to examples/example_response.json")
    
    assert 'request_id' in result, "Response missing request_id"
    assert 'protocol_structured' in result, "Response missing protocol_structured"


def test_export(generated_request_id):
    """Test export endpoint."""
    print("\n=== Testing Export ===")
    
    if not generated_request_id:
        pytest.skip("No request_id available from protocol generation")
    
    request_id = generated_request_id
    
    # Test ODM XML export
    print("\n--- ODM XML Export ---")
    response = requests.post(
        f"{BASE_URL}/api/v1/export",
        json={
            "request_id": request_id,
            "format": "odm_xml",
            "include_crf": True,
            "include_protocol": True,
        },
    )
    
    assert response.status_code == 200, f"ODM export failed: {response.text}"
    
    result = response.json()
    print(f"Format: {result['format']}")
    print(f"Filename: {result['filename']}")
    
    # Save ODM XML
    with open(f"examples/{result['filename']}", "w") as f:
        f.write(result['content'])
    print(f"✓ Saved to examples/{result['filename']}")
    
    # Test FHIR JSON export
    print("\n--- FHIR JSON Export ---")
    response = requests.post(
        f"{BASE_URL}/api/v1/export",
        json={
            "request_id": request_id,
            "format": "fhir_json",
            "include_crf": True,
            "include_protocol": True,
        },
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Format: {result['format']}")
        print(f"Filename: {result['filename']}")
        
        # Save FHIR JSON
        with open(f"examples/{result['filename']}", "w") as f:
            f.write(result['content'])
        print(f"✓ Saved to examples/{result['filename']}")
    
    # Test CSV export
    print("\n--- CSV Export ---")
    response = requests.post(
        f"{BASE_URL}/api/v1/export",
        json={
            "request_id": request_id,
            "format": "csv",
            "include_crf": True,
            "include_protocol": False,
        },
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Format: {result['format']}")
        print(f"Filename: {result['filename']}")
        
        # Save CSV
        with open(f"examples/{result['filename']}", "w") as f:
            f.write(result['content'])
        print(f"✓ Saved to examples/{result['filename']}")
    
    assert 'format' in result, "Response missing format field"
    assert 'filename' in result, "Response missing filename field"


def test_list_protocols():
    """Test list protocols endpoint."""
    print("\n=== Testing List Protocols ===")
    response = requests.get(f"{BASE_URL}/api/v1/protocols")
    
    print(f"Status: {response.status_code}")
    assert response.status_code == 200, f"List protocols failed: {response.text}"
    
    result = response.json()
    print(f"Total Protocols: {result['count']}")
    for protocol in result['protocols']:
        print(f"  - {protocol['request_id']}: {protocol['title']} ({protocol['phase']})")
    
    assert 'count' in result, "Response missing count field"
    assert 'protocols' in result, "Response missing protocols field"


def run_all_tests():
    """Run all tests in sequence."""
    print("=" * 60)
    print("Clinical Trial Protocol Generator API - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Validation", test_validate),
        ("Protocol Generation", test_generate),
        ("Export", test_export),
        ("List Protocols", test_list_protocols),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ {name} failed with error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
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
        
        if command == "health":
            test_health_check()
        elif command == "validate":
            test_validate()
        elif command == "generate":
            test_generate()
        elif command == "export":
            test_export()
        elif command == "list":
            test_list_protocols()
        elif command == "all":
            run_all_tests()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: health, validate, generate, export, list, all")
    else:
        run_all_tests()
