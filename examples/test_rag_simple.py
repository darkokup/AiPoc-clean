"""Simple RAG test - direct service test without API."""
import sys
sys.path.insert(0, 'f:/CodeTests/AiPoc')

from app.services.rag_service import RAGService
from app.services.sample_protocols import SAMPLE_PROTOCOLS
from datetime import datetime

print("=" * 60)
print("RAG Direct Service Test (No API Required)")
print("=" * 60)

print("\n1. Initializing RAG Service...")
try:
    rag = RAGService()
    print("✓ RAG Service initialized")
except Exception as e:
    print(f"✗ Error initializing RAG: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n2. Adding sample protocols to vector database...")
print("   (First run will download ~80MB embedding model)")
print("   This may take 2-5 minutes on first run...")

added = 0
for i, trial_spec in enumerate(SAMPLE_PROTOCOLS, 1):
    try:
        indication = trial_spec.indication
        phase = trial_spec.phase.value if hasattr(trial_spec.phase, 'value') else str(trial_spec.phase)
        
        print(f"\n   Adding protocol {i}/5: {indication} ({phase})")
        
        # Create a minimal protocol object as a mock Pydantic model
        from types import SimpleNamespace
        minimal_protocol = SimpleNamespace(
            protocol_id=f"SAMPLE-{i:03d}",
            model_dump_json=lambda default=None: f'{{"protocol_id":"SAMPLE-{i:03d}","title":"{trial_spec.title}"}}'
        )
        
        doc_id = rag.add_protocol_example(trial_spec, minimal_protocol)
        print(f"   ✓ Added with ID: {doc_id}")
        added += 1
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()

print(f"\n3. Successfully added {added}/{len(SAMPLE_PROTOCOLS)} protocols")

print("\n4. Getting statistics...")
try:
    # RAGService uses collection.count() not rag.count()
    count = rag.collection.count()
    print(f"   Total examples: {count}")
    print(f"   Database path: {rag.db_path}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n5. Testing similarity search...")
try:
    from app.models.schemas import TrialSpecInput, TrialPhase, TrialEndpoint, EndpointType
    
    test_spec = TrialSpecInput(
        sponsor="Test Sponsor",
        title="Test RA Study",
        indication="Rheumatoid Arthritis",
        phase=TrialPhase.PHASE_2,
        design="randomized, double-blind",
        sample_size=100,
        duration_weeks=24,
        key_endpoints=[TrialEndpoint(
            type=EndpointType.PRIMARY,
            name="ACR20",
            description="American College of Rheumatology 20% improvement",
            measurement_timepoint="Week 24"
        )],
        inclusion_criteria=["Age 18-75", "Active RA"],
        exclusion_criteria=["Prior biologic use"],
        region="US"
    )
    
    print(f"   Searching for protocols similar to: Phase 2 RA study")
    similar = rag.retrieve_similar_protocols(test_spec, n_results=3)
    
    print(f"\n   Found {len(similar)} similar protocols:")
    for result in similar:
        print(f"   - {result['metadata']['indication']} ({result['metadata']['phase']})")
        print(f"     Similarity: {result['similarity_score']:.2f}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✓ RAG Service Test Complete!")
print("=" * 60)
print("\nNow you can start the API server with: python main.py")
print("And test the API endpoints with: python examples/test_rag.py all")
