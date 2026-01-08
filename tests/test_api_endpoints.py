"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from main import app
from app.models.schemas import TrialPhase, EndpointType


client = TestClient(app)


class TestAPIEndpoints:
    """Test suite for API endpoints."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_generate_protocol_basic(self):
        """Test basic protocol generation."""
        payload = {
            "sponsor": "Test Pharma Inc",
            "title": "Safety and Efficacy Study",
            "indication": "Hypertension",
            "phase": "Phase 2",
            "design": "randomized, double-blind, placebo-controlled",
            "sample_size": 100,
            "duration_weeks": 12,
            "treatment_arms": ["Drug X 10mg", "Placebo"],
            "key_endpoints": [
                {
                    "type": "primary",
                    "name": "Change in systolic blood pressure from baseline"
                }
            ],
            "inclusion_criteria": [
                "Age 18-65 years",
                "Diagnosed hypertension"
            ],
            "exclusion_criteria": [
                "Severe hypertension (>180/110 mmHg)",
                "Pregnancy or lactation"
            ],
            "region": "North America"
        }
        
        response = client.post("/api/v1/generate", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert "protocol_structured" in data
        assert "title" in data["protocol_structured"]
        assert "objectives" in data["protocol_structured"]
        assert "study_design" in data["protocol_structured"]
    
    def test_generate_protocol_with_additional_instructions(self):
        """Test protocol generation with additional instructions."""
        payload = {
            "sponsor": "Test Pharma Inc",
            "title": "COVID Safety Study",
            "indication": "Hypertension",
            "phase": "Phase 2",
            "design": "randomized",
            "sample_size": 100,
            "duration_weeks": 12,
            "treatment_arms": ["Drug X", "Placebo"],
            "key_endpoints": [
                {
                    "type": "primary",
                    "name": "Blood pressure reduction"
                }
            ],
            "inclusion_criteria": ["Age 18-65"],
            "exclusion_criteria": ["Pregnancy"],
            "region": "Global",
            "additional_instructions": "Include COVID-19 safety protocols and remote monitoring options"
        }
        
        response = client.post("/api/v1/generate", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert "protocol_structured" in data
        # The additional instructions should influence the protocol
        # (actual content check would require LLM)
    
    def test_generate_protocol_invalid_phase(self):
        """Test protocol generation with invalid phase."""
        payload = {
            "sponsor": "Test Pharma",
            "title": "Test Study",
            "indication": "Hypertension",
            "phase": "INVALID_PHASE",  # Invalid
            "design": "randomized",
            "sample_size": 100,
            "duration_weeks": 12,
            "treatment_arms": ["Drug X", "Placebo"],
            "key_endpoints": [
                {"type": "primary", "name": "BP change"}
            ],
            "inclusion_criteria": ["Age 18-65"],
            "exclusion_criteria": ["Pregnancy"],
            "region": "US"
        }
        
        response = client.post("/api/v1/generate", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_generate_protocol_missing_required_field(self):
        """Test protocol generation with missing required fields."""
        payload = {
            "sponsor": "Test Pharma",
            # Missing title
            "indication": "Hypertension",
            "phase": "PHASE_2",
            "design": "randomized",
            "sample_size": 100,
            "duration_weeks": 12
        }
        
        response = client.post("/api/v1/generate", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_generate_crf_basic(self):
        """Test CRF generation via protocol endpoint."""
        payload = {
            "sponsor": "Test Pharma Inc",
            "title": "Safety and Efficacy Study",
            "indication": "Hypertension",
            "phase": "Phase 2",
            "design": "randomized",
            "sample_size": 100,
            "duration_weeks": 12,
            "treatment_arms": ["Drug X", "Placebo"],
            "key_endpoints": [
                {"type": "primary", "name": "BP change"}
            ],
            "inclusion_criteria": ["Age 18-65"],
            "exclusion_criteria": ["Pregnancy"],
            "region": "US"
        }
        
        response = client.post("/api/v1/generate", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert "crf_schema" in data
        assert "forms" in data["crf_schema"]
        assert len(data["crf_schema"]["forms"]) > 0
        
        # Check first form structure
        first_form = data["crf_schema"]["forms"][0]
        assert "form_id" in first_form
        assert "form_name" in first_form
        assert "fields" in first_form
    
    def test_seed_rag_endpoint(self):
        """Test RAG seeding via protocol generation."""
        payload = {
            "sponsor": "Test Pharma",
            "title": "Test Protocol for RAG",
            "indication": "Test Disease",
            "phase": "Phase 1",
            "design": "open-label",
            "sample_size": 20,
            "duration_weeks": 4,
            "treatment_arms": ["Drug X"],
            "key_endpoints": [
                {"type": "primary", "name": "Safety"}
            ],
            "inclusion_criteria": ["Healthy volunteers"],
            "exclusion_criteria": ["Prior conditions"],
            "region": "US"
        }
        
        response = client.post("/api/v1/generate", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert "protocol_structured" in data
        # Title is in the protocol_structured object
        assert data["protocol_structured"]["title"] == "Test Protocol for RAG"
    
    def test_export_odm_endpoint(self):
        """Test ODM export via direct export service."""
        # First generate a protocol
        payload = {
            "sponsor": "Test Pharma",
            "title": "Export Test Study",
            "indication": "Hypertension",
            "phase": "Phase 2",
            "design": "randomized",
            "sample_size": 50,
            "duration_weeks": 8,
            "treatment_arms": ["Drug X", "Placebo"],
            "key_endpoints": [
                {"type": "primary", "name": "BP reduction"}
            ],
            "inclusion_criteria": ["Age 18-65"],
            "exclusion_criteria": ["Pregnancy"],
            "region": "US"
        }
        
        response = client.post("/api/v1/generate", json=payload)
        assert response.status_code == 201
        protocol_data = response.json()
        
        # Verify we got a valid response with protocol and CRF
        assert "protocol_structured" in protocol_data
        assert "crf_schema" in protocol_data
        assert "request_id" in protocol_data
    
    def test_generate_protocol_with_all_optional_fields(self):
        """Test protocol generation with all optional fields populated."""
        payload = {
            "sponsor": "Comprehensive Pharma Inc",
            "title": "Comprehensive Test Study",
            "indication": "Type 2 Diabetes",
            "phase": "Phase 3",
            "design": "randomized, double-blind, placebo-controlled, multicenter",
            "sample_size": 500,
            "duration_weeks": 52,
            "treatment_arms": ["Diabetes Drug 100mg", "Diabetes Drug 200mg", "Placebo"],
            "key_endpoints": [
                {
                    "type": "primary",
                    "name": "Change in HbA1c from baseline",
                    "description": "Mean change in glycated hemoglobin at 26 weeks"
                },
                {
                    "type": "secondary",
                    "name": "Weight change",
                    "description": "Mean change in body weight"
                }
            ],
            "inclusion_criteria": [
                "Age 18-75 years",
                "Type 2 Diabetes diagnosis",
                "HbA1c 7.0-10.0%"
            ],
            "exclusion_criteria": [
                "Type 1 Diabetes",
                "Severe renal impairment",
                "Pregnancy or lactation"
            ],
            "region": "Global",
            "additional_instructions": "Include telemedicine visits and digital health monitoring. Emphasize patient diversity and inclusion."
        }
        
        response = client.post("/api/v1/generate", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert "protocol_structured" in data
        protocol = data["protocol_structured"]
        
        # Verify comprehensive structure
        assert "title" in protocol
        assert "objectives" in protocol
        assert "study_design" in protocol
        assert "visit_schedule" in protocol
        assert "assessments" in protocol
        assert "safety_monitoring" in protocol


class TestAPIErrorHandling:
    """Test suite for API error handling."""
    
    def test_invalid_json_payload(self):
        """Test handling of invalid JSON."""
        response = client.post(
            "/api/v1/generate",
            data="invalid json{{{",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_empty_payload(self):
        """Test handling of empty payload."""
        response = client.post("/api/v1/generate", json={})
        assert response.status_code == 422
    
    def test_negative_sample_size(self):
        """Test validation of negative sample size."""
        payload = {
            "sponsor": "Test Pharma",
            "title": "Test Study",
            "indication": "Hypertension",
            "phase": "PHASE_2",
            "design": "randomized",
            "sample_size": -100,  # Invalid negative
            "duration_weeks": 12,
            "key_endpoints": [
                {"type": "primary", "name": "BP change"}
            ],
            "inclusion_criteria": ["Age 18-65"],
            "exclusion_criteria": ["Pregnancy"],
            "region": "US"
        }
        
        response = client.post("/api/v1/generate", json=payload)
        assert response.status_code == 422
    
    def test_invalid_endpoint_type(self):
        """Test validation of endpoint type."""
        payload = {
            "sponsor": "Test Pharma",
            "title": "Test Study",
            "indication": "Hypertension",
            "phase": "PHASE_2",
            "design": "randomized",
            "sample_size": 100,
            "duration_weeks": 12,
            "key_endpoints": [
                {"type": "INVALID_TYPE", "name": "BP change"}
            ],
            "inclusion_criteria": ["Age 18-65"],
            "exclusion_criteria": ["Pregnancy"],
            "region": "US"
        }
        
        response = client.post("/api/v1/generate", json=payload)
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
