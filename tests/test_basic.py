"""Simple test cases for the application."""
import pytest
from datetime import datetime
from app.models.schemas import (
    TrialSpecInput,
    TrialPhase,
    TrialEndpoint,
    EndpointType,
)
from app.services.generator import ProtocolTemplateGenerator, CRFGenerator
from app.services.validator import ClinicalRulesValidator


def test_trial_spec_validation():
    """Test trial specification model validation."""
    trial_spec = TrialSpecInput(
        sponsor="Test Pharma",
        title="Test Study",
        indication="Test Disease",
        phase=TrialPhase.PHASE_2,
        design="randomized, double-blind",
        sample_size=100,
        duration_weeks=12,
        key_endpoints=[
            TrialEndpoint(type=EndpointType.PRIMARY, name="Primary endpoint")
        ],
        inclusion_criteria=["Age 18-65", "Confirmed diagnosis"],
        exclusion_criteria=["Pregnancy"],
        region="US"
    )
    
    assert trial_spec.sponsor == "Test Pharma"
    assert trial_spec.sample_size == 100
    assert len(trial_spec.key_endpoints) == 1


def test_protocol_generation():
    """Test protocol generation."""
    generator = ProtocolTemplateGenerator()
    
    trial_spec = TrialSpecInput(
        sponsor="Test Pharma",
        title="Test Study",
        indication="Test Disease",
        phase=TrialPhase.PHASE_2,
        design="randomized, double-blind",
        sample_size=100,
        duration_weeks=12,
        key_endpoints=[
            TrialEndpoint(type=EndpointType.PRIMARY, name="Test endpoint")
        ],
        inclusion_criteria=["Age 18-65", "Confirmed diagnosis"],
        exclusion_criteria=["Pregnancy"],
        region="US"
    )
    
    protocol = generator.generate_structured_protocol(trial_spec)
    
    assert protocol.sponsor == "Test Pharma"
    assert protocol.sample_size == 100
    assert len(protocol.sections) > 0
    assert len(protocol.visit_schedule) >= 2  # At least screening and baseline


def test_crf_generation():
    """Test CRF schema generation."""
    protocol_generator = ProtocolTemplateGenerator()
    crf_generator = CRFGenerator()
    
    trial_spec = TrialSpecInput(
        sponsor="Test Pharma",
        title="Test Study",
        indication="Test Disease",
        phase=TrialPhase.PHASE_2,
        design="randomized, double-blind",
        sample_size=100,
        duration_weeks=12,
        key_endpoints=[
            TrialEndpoint(type=EndpointType.PRIMARY, name="Change in score at week 12")
        ],
        inclusion_criteria=["Age 18-65"],
        exclusion_criteria=["Pregnancy"],
        region="US"
    )
    
    protocol = protocol_generator.generate_structured_protocol(trial_spec)
    crf_schema = crf_generator.generate_crf_schema(trial_spec, protocol)
    
    assert len(crf_schema.forms) >= 3  # DM, VS, AE at minimum
    assert len(crf_schema.visits) >= 2
    assert crf_schema.cdash_compliance == True
    
    # Check that Demographics form exists
    dm_form = next((f for f in crf_schema.forms if f.form_id == "DM"), None)
    assert dm_form is not None
    assert len(dm_form.fields) > 0


def test_validation_rules():
    """Test clinical rules validation."""
    validator = ClinicalRulesValidator()
    
    # Valid spec
    valid_spec = TrialSpecInput(
        sponsor="Test Pharma",
        title="Test Study",
        indication="Test Disease",
        phase=TrialPhase.PHASE_2,
        design="randomized, double-blind",
        sample_size=100,
        duration_weeks=12,
        key_endpoints=[
            TrialEndpoint(type=EndpointType.PRIMARY, name="Primary endpoint")
        ],
        inclusion_criteria=["Age 18-65", "Confirmed diagnosis"],
        exclusion_criteria=["Pregnancy"],
        region="US"
    )
    
    result = validator.validate_trial_spec(valid_spec)
    assert result.valid == True
    
    # Invalid spec - too small sample size
    invalid_spec = TrialSpecInput(
        sponsor="Test Pharma",
        title="Test Study",
        indication="Test Disease",
        phase=TrialPhase.PHASE_3,
        design="randomized, double-blind",
        sample_size=20,  # Too small for Phase 3
        duration_weeks=12,
        key_endpoints=[
            TrialEndpoint(type=EndpointType.PRIMARY, name="Primary endpoint")
        ],
        inclusion_criteria=["Age 18-65"],
        exclusion_criteria=["Pregnancy"],
        region="US"
    )
    
    result = validator.validate_trial_spec(invalid_spec)
    assert len(result.warnings) > 0  # Should have warnings about sample size


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
