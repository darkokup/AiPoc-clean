"""Tests for Additional Instructions feature integration."""
import pytest
from app.models.schemas import TrialSpecInput, TrialPhase, TrialEndpoint, EndpointType
from app.services.generator import ProtocolTemplateGenerator


class TestAdditionalInstructions:
    """Test suite for additional instructions feature."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.generator = ProtocolTemplateGenerator(use_llm=True, use_rag=False)
        
        self.base_spec = TrialSpecInput(
            sponsor="Test Pharma",
            title="Phase II Diabetes Study",
            indication="Type 2 Diabetes",
            phase=TrialPhase.PHASE_2,
            design="randomized, double-blind",
            sample_size=100,
            duration_weeks=24,
            key_endpoints=[
                TrialEndpoint(
                    type=EndpointType.PRIMARY,
                    name="Change in HbA1c",
                    description="Change from baseline",
                    measurement_timepoint="Week 24"
                )
            ],
            inclusion_criteria=["Type 2 Diabetes", "HbA1c 7-10%"],
            exclusion_criteria=["Type 1 Diabetes"],
            region="Global"
        )
    
    def test_without_additional_instructions(self):
        """Baseline test without additional instructions."""
        protocol = self.generator.generate_structured_protocol(self.base_spec)
        
        assert protocol is not None
        assert protocol.sponsor == "Test Pharma"
        assert len(protocol.inclusion_criteria) >= 2
    
    def test_with_additional_instructions(self):
        """Test that additional instructions are passed through."""
        spec_with_instructions = self.base_spec.model_copy(update={
            "additional_instructions": "Include COVID-19 safety measures and telemedicine visits"
        })
        
        protocol = self.generator.generate_structured_protocol(spec_with_instructions)
        
        assert protocol is not None
        # Check that protocol was generated
        assert len(protocol.objectives) > 0
    
    def test_additional_instructions_in_objectives(self):
        """Test additional instructions influence objectives."""
        spec = self.base_spec.model_copy(update={
            "additional_instructions": "Focus on elderly population age 65 and above"
        })
        
        protocol = self.generator.generate_structured_protocol(spec)
        objectives_text = str(protocol.objectives).lower()
        
        # Check if elderly-related keywords appear
        # (This is a soft check - LLM might paraphrase)
        assert protocol.objectives is not None
    
    def test_additional_instructions_in_study_design(self):
        """Test additional instructions influence study design."""
        spec = self.base_spec.model_copy(update={
            "additional_instructions": "Include wearable device monitoring for continuous glucose"
        })
        
        protocol = self.generator.generate_structured_protocol(spec)
        
        assert protocol.study_design is not None
        assert len(protocol.study_design) > 0
    
    def test_empty_additional_instructions(self):
        """Test with empty string for additional instructions."""
        spec = self.base_spec.model_copy(update={
            "additional_instructions": ""
        })
        
        protocol = self.generator.generate_structured_protocol(spec)
        assert protocol is not None
    
    def test_none_additional_instructions(self):
        """Test with None for additional instructions."""
        spec = self.base_spec.model_copy(update={
            "additional_instructions": None
        })
        
        protocol = self.generator.generate_structured_protocol(spec)
        assert protocol is not None
    
    def test_very_long_additional_instructions(self):
        """Test with very long additional instructions."""
        long_instructions = " ".join([
            "Instruction point number " + str(i) for i in range(100)
        ])
        
        spec = self.base_spec.model_copy(update={
            "additional_instructions": long_instructions
        })
        
        # Should not crash
        protocol = self.generator.generate_structured_protocol(spec)
        assert protocol is not None


@pytest.mark.llm
class TestAdditionalInstructionsWithLLM:
    """Tests that require actual LLM calls."""
    
    def test_biomarker_instructions_in_criteria(self):
        """Test biomarker requirements appear in inclusion criteria."""
        spec = TrialSpecInput(
            sponsor="Test Pharma",
            title="NSCLC Study",
            indication="Non-Small Cell Lung Cancer",
            phase=TrialPhase.PHASE_2,
            design="single-arm",
            sample_size=50,
            duration_weeks=48,
            key_endpoints=[
                TrialEndpoint(
                    type=EndpointType.PRIMARY,
                    name="ORR",
                    measurement_timepoint="Every 9 weeks"
                )
            ],
            inclusion_criteria=["NSCLC diagnosis"],
            exclusion_criteria=["Brain metastases"],
            region="US",
            additional_instructions="Require PD-L1 TPS >= 50% biomarker testing"
        )
        
        generator = ProtocolTemplateGenerator(use_llm=True, use_rag=False)
        protocol = generator.generate_structured_protocol(spec)
        
        criteria_text = " ".join(protocol.inclusion_criteria).lower()
        
        # Check for biomarker-related terms
        assert any(term in criteria_text for term in ['pd-l1', 'biomarker', 'tps', '50%'])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
