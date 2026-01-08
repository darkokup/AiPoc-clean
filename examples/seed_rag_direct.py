"""Direct RAG database seeding - bypasses API server."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.rag_service import get_rag_service
from app.services.sample_protocols import SAMPLE_PROTOCOLS
from app.services.generator import ProtocolTemplateGenerator


def seed_database_directly():
    """Seed the RAG database directly without needing API server."""
    print("\n" + "="*60)
    print("DIRECT RAG DATABASE SEEDING")
    print("="*60)
    
    print("\n📦 Initializing services...")
    rag_service = get_rag_service()
    generator = ProtocolTemplateGenerator(use_rag=False, use_llm=False)  # Use template-only mode for seeding
    
    print(f"\n📊 Current database stats:")
    count = rag_service.get_count()
    print(f"   Total examples: {count}")
    
    print(f"\n🌱 Seeding {len(SAMPLE_PROTOCOLS)} sample protocols...")
    
    added = 0
    failed = 0
    
    for i, trial_spec in enumerate(SAMPLE_PROTOCOLS, 1):
        try:
            # Generate a protocol using the trial spec
            print(f"   🔄 {i:2d}. Generating {trial_spec.phase.value} protocol for {trial_spec.indication[:30]}...")
            protocol = generator.generate_structured_protocol(trial_spec)
            
            # Add to RAG
            doc_id = rag_service.add_protocol_example(trial_spec, protocol)
            
            print(f"      ✅ {trial_spec.phase.value:12s} | {trial_spec.indication[:40]:<40s} | {doc_id}")
            added += 1
            
        except Exception as e:
            print(f"      ❌ {trial_spec.phase.value:12s} | {trial_spec.indication[:40]:<40s}")
            print(f"         Error: {str(e)[:80]}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print(f"\n📊 Seeding complete:")
    print(f"   ✅ Added: {added}")
    print(f"   ❌ Failed: {failed}")
    
    # Get updated stats
    print(f"\n📈 Updated database stats:")
    count = rag_service.get_count()
    print(f"   Total examples: {count}")
    
    print("\n" + "="*60)
    print("✅ DATABASE SEEDING COMPLETE!")
    print("="*60)
    
    return added, failed


def test_search():
    """Test searching the newly seeded database."""
    print("\n" + "="*60)
    print("TESTING RAG SEARCH")
    print("="*60)
    
    rag_service = get_rag_service()
    
    # Test search for oncology protocols
    print("\n🔍 Searching for oncology protocols...")
    
    from app.models.schemas import TrialSpecInput, TrialPhase, TrialEndpoint, EndpointType
    
    test_spec = TrialSpecInput(
        sponsor="Test",
        title="Cancer immunotherapy trial",
        indication="Lung Cancer",
        phase=TrialPhase.PHASE_3,
        design="randomized controlled trial",
        sample_size=200,
        duration_weeks=52,
        key_endpoints=[
            TrialEndpoint(
                type=EndpointType.PRIMARY,
                name="Overall Survival"
            )
        ],
        inclusion_criteria=["Age >= 18"],
        exclusion_criteria=["Active infection"],
        region="Global"
    )
    
    results = rag_service.retrieve_similar_protocols(test_spec, n_results=3)
    
    print(f"\n📋 Found {len(results)} similar protocols:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Document: {result.get('doc_id', 'Unknown')}")
        print(f"   Similarity: {result.get('distance', 'N/A')}")
        if 'metadata' in result:
            meta = result['metadata']
            print(f"   Phase: {meta.get('phase', 'N/A')}")
            print(f"   Indication: {meta.get('indication', 'N/A')}")
            print(f"   Sample Size: {meta.get('sample_size', 'N/A')}")
    
    print("\n" + "="*60)
    print("✅ SEARCH TEST COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    # Seed the database
    added, failed = seed_database_directly()
    
    if added > 0:
        # Test search functionality
        test_search()
    
    print(f"\n🎉 Success! Added {added} protocols to RAG database.")
    print(f"💡 The RAG system now has {added} diverse clinical trial examples.")
    print(f"\n📍 Database location: ./vector_db/")
