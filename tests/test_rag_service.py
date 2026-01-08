"""Tests for RAG Service."""
import pytest
import tempfile
import shutil
from pathlib import Path
from app.services.rag_service import RAGService
from app.models.schemas import TrialSpecInput, TrialPhase, TrialEndpoint, EndpointType
from app.services.generator import ProtocolTemplateGenerator


class TestRAGService:
    """Test suite for RAG service."""
    
    def setup_method(self):
        """Create temporary database for testing."""
        self.temp_dir = tempfile.mkdtemp()
        # Note: You'd need to modify RAGService to accept custom path
        # For now, this is a template
        
    def teardown_method(self):
        """Clean up temporary database."""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_add_protocol_to_rag(self):
        """Test adding a protocol to RAG database."""
        from app.services.rag_service import get_rag_service
        
        rag_service = get_rag_service()
        initial_count = rag_service.get_count()
        
        spec = TrialSpecInput(
            sponsor="Test Pharma",
            title="Test Study",
            indication="Hypertension",
            phase=TrialPhase.PHASE_2,
            design="randomized",
            sample_size=100,
            duration_weeks=12,
            key_endpoints=[
                TrialEndpoint(type=EndpointType.PRIMARY, name="Blood pressure change")
            ],
            inclusion_criteria=["Hypertension"],
            exclusion_criteria=["Severe hypertension"],
            region="US"
        )
        
        generator = ProtocolTemplateGenerator(use_llm=False, use_rag=False)
        protocol = generator.generate_structured_protocol(spec)
        
        doc_id = rag_service.add_protocol_example(spec, protocol)
        
        assert doc_id is not None
        assert doc_id.startswith("protocol_")
        assert rag_service.get_count() == initial_count + 1
        
        # Clean up
        rag_service.delete_protocol(doc_id)
    
    def test_retrieve_similar_protocols(self):
        """Test retrieving similar protocols."""
        from app.services.rag_service import get_rag_service
        
        rag_service = get_rag_service()
        
        # Add a test protocol first
        spec = TrialSpecInput(
            sponsor="Test Pharma",
            title="Diabetes Study",
            indication="Type 2 Diabetes",
            phase=TrialPhase.PHASE_2,
            design="randomized",
            sample_size=100,
            duration_weeks=24,
            key_endpoints=[
                TrialEndpoint(type=EndpointType.PRIMARY, name="HbA1c change")
            ],
            inclusion_criteria=["Type 2 Diabetes"],
            exclusion_criteria=["Type 1 Diabetes"],
            region="US"
        )
        
        generator = ProtocolTemplateGenerator(use_llm=False, use_rag=False)
        protocol = generator.generate_structured_protocol(spec)
        doc_id = rag_service.add_protocol_example(spec, protocol)
        
        # Now search for similar
        search_spec = TrialSpecInput(
            sponsor="Another Pharma",
            title="Another Diabetes Study",
            indication="Type 2 Diabetes",
            phase=TrialPhase.PHASE_2,
            design="open-label",
            sample_size=80,
            duration_weeks=20,
            key_endpoints=[
                TrialEndpoint(type=EndpointType.PRIMARY, name="Glucose control")
            ],
            inclusion_criteria=["Diabetes"],
            exclusion_criteria=["Pregnancy"],
            region="EU"
        )
        
        similar = rag_service.retrieve_similar_protocols(search_spec, n_results=3)
        
        assert len(similar) > 0
        assert similar[0]['metadata']['indication'] == "Type 2 Diabetes"
        
        # Clean up
        rag_service.delete_protocol(doc_id)
    
    def test_get_protocol_by_id(self):
        """Test retrieving specific protocol by ID."""
        from app.services.rag_service import get_rag_service
        
        rag_service = get_rag_service()
        
        spec = TrialSpecInput(
            sponsor="Test Pharma",
            title="Cancer Study",
            indication="Breast Cancer",
            phase=TrialPhase.PHASE_3,
            design="randomized",
            sample_size=500,
            duration_weeks=52,
            key_endpoints=[
                TrialEndpoint(type=EndpointType.PRIMARY, name="Overall survival")
            ],
            inclusion_criteria=["Breast cancer"],
            exclusion_criteria=["Prior chemotherapy"],
            region="Global"
        )
        
        generator = ProtocolTemplateGenerator(use_llm=False, use_rag=False)
        protocol = generator.generate_structured_protocol(spec)
        doc_id = rag_service.add_protocol_example(spec, protocol)
        
        # Retrieve it
        retrieved = rag_service.get_protocol_by_id(doc_id)
        
        assert retrieved is not None
        assert retrieved['id'] == doc_id
        assert retrieved['metadata']['indication'] == "Breast Cancer"
        assert retrieved['trial_spec']['sample_size'] == 500
        
        # Clean up
        rag_service.delete_protocol(doc_id)
    
    def test_delete_protocol(self):
        """Test deleting a protocol."""
        from app.services.rag_service import get_rag_service
        
        rag_service = get_rag_service()
        initial_count = rag_service.get_count()
        
        spec = TrialSpecInput(
            sponsor="Test Pharma",
            title="Temp Study",
            indication="Test Disease",
            phase=TrialPhase.PHASE_1,
            design="open-label",
            sample_size=20,
            duration_weeks=4,
            key_endpoints=[
                TrialEndpoint(type=EndpointType.PRIMARY, name="Safety")
            ],
            inclusion_criteria=["Healthy"],
            exclusion_criteria=["Pregnant"],
            region="US"
        )
        
        generator = ProtocolTemplateGenerator(use_llm=False, use_rag=False)
        protocol = generator.generate_structured_protocol(spec)
        doc_id = rag_service.add_protocol_example(spec, protocol)
        
        # Delete it
        success = rag_service.delete_protocol(doc_id)
        
        assert success == True
        assert rag_service.get_count() == initial_count
        
        # Try to retrieve deleted protocol
        retrieved = rag_service.get_protocol_by_id(doc_id)
        assert retrieved is None
    
    def test_search_text_creation(self):
        """Test search text creation from trial spec."""
        from app.services.rag_service import get_rag_service
        
        rag_service = get_rag_service()
        
        spec = TrialSpecInput(
            sponsor="Test Pharma",
            title="COPD Study",
            indication="Chronic Obstructive Pulmonary Disease",
            phase=TrialPhase.PHASE_2,
            design="randomized, double-blind",
            sample_size=200,
            duration_weeks=24,
            key_endpoints=[
                TrialEndpoint(
                    type=EndpointType.PRIMARY,
                    name="FEV1 improvement",
                    description="Forced expiratory volume"
                )
            ],
            inclusion_criteria=["COPD diagnosis", "FEV1 < 70%"],
            exclusion_criteria=["Asthma"],
            region="North America"
        )
        
        search_text = rag_service._create_search_text(spec)
        
        assert "Phase 2" in search_text or "PHASE_2" in search_text
        assert "Chronic Obstructive Pulmonary Disease" in search_text
        assert "200" in search_text
        assert "24 weeks" in search_text
        assert "FEV1" in search_text or "primary" in search_text.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
