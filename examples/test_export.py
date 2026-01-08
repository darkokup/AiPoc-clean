"""Test export functionality."""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_export():
    print("=" * 60)
    print("Testing Export Functionality")
    print("=" * 60)
    
    # First, check if we have any protocols
    print("\n1. Checking for existing protocols...")
    response = requests.get(f"{BASE_URL}/api/v1/protocols")
    if response.status_code == 200:
        protocols = response.json()
        print(f"   Found {len(protocols['protocols'])} protocol(s)")
        
        if len(protocols['protocols']) == 0:
            print("\n   No protocols found. Generating one first...")
            
            # Generate a simple protocol
            trial_spec = {
                "sponsor": "Test Sponsor",
                "title": "Test Export Protocol",
                "indication": "Test Indication",
                "phase": "Phase 2",
                "design": "randomized, double-blind",
                "sample_size": 100,
                "duration_weeks": 24,
                "key_endpoints": [
                    {
                        "type": "primary",
                        "name": "Test Endpoint",
                        "description": "Test primary endpoint",
                        "measurement_timepoint": "Week 24"
                    }
                ],
                "inclusion_criteria": ["Age 18-75"],
                "exclusion_criteria": ["Prior therapy"],
                "region": "US"
            }
            
            gen_response = requests.post(
                f"{BASE_URL}/api/v1/generate",
                json=trial_spec
            )
            
            if gen_response.status_code == 201:
                result = gen_response.json()
                request_id = result["request_id"]
                print(f"   ✓ Generated protocol: {request_id}")
            else:
                print(f"   ✗ Failed to generate protocol: {gen_response.text}")
                return
        else:
            request_id = protocols['protocols'][0]['request_id']
            print(f"   Using existing protocol: {request_id}")
    else:
        print(f"   ✗ Error listing protocols: {response.text}")
        return
    
    # Test ODM export
    print(f"\n2. Testing ODM XML export...")
    odm_response = requests.post(
        f"{BASE_URL}/api/v1/export/odm",
        json={"request_id": request_id}
    )
    
    if odm_response.status_code == 200:
        odm_data = odm_response.json()
        odm_xml = odm_data.get("odm_xml", "")
        print(f"   ✓ ODM export successful")
        print(f"   Filename: {odm_data.get('filename')}")
        print(f"   Content length: {len(odm_xml)} characters")
        
        if len(odm_xml) > 0:
            print(f"   First 200 chars: {odm_xml[:200]}...")
            
            # Save to file
            with open(f"export_test_{request_id}_ODM.xml", "w", encoding="utf-8") as f:
                f.write(odm_xml)
            print(f"   Saved to: export_test_{request_id}_ODM.xml")
        else:
            print(f"   ⚠ ODM content is empty!")
    else:
        print(f"   ✗ ODM export failed: {odm_response.text}")
    
    # Test FHIR export
    print(f"\n3. Testing FHIR JSON export...")
    fhir_response = requests.post(
        f"{BASE_URL}/api/v1/export/fhir",
        json={"request_id": request_id}
    )
    
    if fhir_response.status_code == 200:
        fhir_data = fhir_response.json()
        fhir_bundle = fhir_data.get("fhir_bundle", {})
        print(f"   ✓ FHIR export successful")
        print(f"   Filename: {fhir_data.get('filename')}")
        
        if isinstance(fhir_bundle, dict):
            print(f"   Resource type: {fhir_bundle.get('resourceType')}")
            print(f"   Number of resources: {len(fhir_bundle.get('entry', []))}")
            
            # Save to file
            with open(f"export_test_{request_id}_FHIR.json", "w", encoding="utf-8") as f:
                json.dump(fhir_bundle, f, indent=2)
            print(f"   Saved to: export_test_{request_id}_FHIR.json")
        else:
            print(f"   ⚠ FHIR bundle has unexpected format: {type(fhir_bundle)}")
            print(f"   Content: {fhir_bundle}")
    else:
        print(f"   ✗ FHIR export failed: {fhir_response.text}")
    
    # Test CSV export
    print(f"\n4. Testing CSV export...")
    csv_response = requests.post(
        f"{BASE_URL}/api/v1/export/csv",
        json={"request_id": request_id}
    )
    
    if csv_response.status_code == 200:
        csv_data = csv_response.json()
        csv_content = csv_data.get("csv_content", "")
        print(f"   ✓ CSV export successful")
        print(f"   Filename: {csv_data.get('filename')}")
        print(f"   Content length: {len(csv_content)} characters")
        
        if len(csv_content) > 0:
            # Save to file
            with open(f"export_test_{request_id}.csv", "w", encoding="utf-8") as f:
                f.write(csv_content)
            print(f"   Saved to: export_test_{request_id}.csv")
        else:
            print(f"   ⚠ CSV content is empty!")
    else:
        print(f"   ✗ CSV export failed: {csv_response.text}")
    
    print("\n" + "=" * 60)
    print("Export test complete!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_export()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
