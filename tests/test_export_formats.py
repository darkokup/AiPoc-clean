"""Tests for export formats (ODM, FHIR, CSV)."""
import pytest
from app.services.generator import ProtocolTemplateGenerator, CRFGenerator
from app.services.exporter import ProtocolExporter
from app.models.schemas import (
    TrialSpecInput, TrialPhase, TrialEndpoint, EndpointType, ExportFormat
)
import xml.etree.ElementTree as ET
import json
import csv
import io


class TestExportFormats:
    """Test suite for all export formats."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.generator = ProtocolTemplateGenerator(use_llm=False, use_rag=False)
        self.crf_generator = CRFGenerator()
        self.exporter = ProtocolExporter()
        
        self.spec = TrialSpecInput(
            sponsor="Test Pharma Inc",
            title="Hypertension Study",
            indication="Hypertension",
            phase=TrialPhase.PHASE_2,
            design="randomized, double-blind",
            sample_size=100,
            duration_weeks=12,
            key_endpoints=[
                TrialEndpoint(
                    type=EndpointType.PRIMARY,
                    name="Change in systolic BP"
                )
            ],
            inclusion_criteria=["Age 18-65", "Hypertension"],
            exclusion_criteria=["Severe hypertension"],
            region="North America"
        )
        
        self.protocol = self.generator.generate_structured_protocol(self.spec)
        self.crf = self.crf_generator.generate_crf_schema(self.spec, self.protocol)
    
    def test_odm_export_produces_output(self):
        """Test that ODM export produces output."""
        result = self.exporter.export(
            self.protocol,
            self.crf,
            ExportFormat.ODM_XML
        )
        
        assert result is not None
        assert 'content' in result
        assert len(result['content']) > 0
    
    def test_odm_export_valid_xml(self):
        """Test that ODM export produces valid XML."""
        result = self.exporter.export(
            self.protocol,
            self.crf,
            ExportFormat.ODM_XML
        )
        
        odm_xml = result['content']
        
        # Parse to verify valid XML
        root = ET.fromstring(odm_xml)
        assert root is not None
        assert 'ODM' in root.tag
    
    def test_odm_export_has_study_element(self):
        """Test that ODM export contains Study element."""
        result = self.exporter.export(
            self.protocol,
            self.crf,
            ExportFormat.ODM_XML
        )
        
        odm_xml = result['content']
        root = ET.fromstring(odm_xml)
        
        # Find Study element (namespace-aware)
        study = root.find(".//{*}Study")
        assert study is not None
    
    def test_odm_export_has_forms(self):
        """Test that ODM export contains FormDef elements."""
        result = self.exporter.export(
            self.protocol,
            self.crf,
            ExportFormat.ODM_XML
        )
        
        odm_xml = result['content']
        root = ET.fromstring(odm_xml)
        
        forms = root.findall(".//{*}FormDef")
        assert len(forms) > 0
    
    def test_fhir_export_produces_output(self):
        """Test that FHIR export produces output."""
        result = self.exporter.export(
            self.protocol,
            self.crf,
            ExportFormat.FHIR_JSON
        )
        
        assert result is not None
        assert 'content' in result
        assert len(result['content']) > 0
    
    def test_fhir_export_valid_json(self):
        """Test that FHIR export produces valid JSON."""
        result = self.exporter.export(
            self.protocol,
            self.crf,
            ExportFormat.FHIR_JSON
        )
        
        fhir_json = result['content']
        
        # Parse to verify valid JSON
        if isinstance(fhir_json, str):
            data = json.loads(fhir_json)
        else:
            data = fhir_json
        
        assert data is not None
        assert isinstance(data, dict)
    
    def test_fhir_export_has_resource_type(self):
        """Test that FHIR export has resourceType."""
        result = self.exporter.export(
            self.protocol,
            self.crf,
            ExportFormat.FHIR_JSON
        )
        
        fhir_json = result['content']
        
        if isinstance(fhir_json, str):
            data = json.loads(fhir_json)
        else:
            data = fhir_json
        
        assert 'resourceType' in data
        # FHIR export creates a Bundle containing ResearchStudy and Questionnaire resources
        assert data['resourceType'] in ['ResearchStudy', 'Bundle']
    
    def test_csv_export_produces_output(self):
        """Test that CSV export produces output."""
        result = self.exporter.export(
            self.protocol,
            self.crf,
            ExportFormat.CSV
        )
        
        assert result is not None
        assert 'content' in result
        assert len(result['content']) > 0
    
    def test_csv_export_valid_format(self):
        """Test that CSV export produces valid CSV."""
        result = self.exporter.export(
            self.protocol,
            self.crf,
            ExportFormat.CSV
        )
        
        csv_text = result['content']
        
        # Parse to verify valid CSV
        reader = csv.reader(io.StringIO(csv_text))
        rows = list(reader)
        
        assert len(rows) > 0
    
    def test_csv_export_has_headers(self):
        """Test that CSV export includes headers."""
        result = self.exporter.export(
            self.protocol,
            self.crf,
            ExportFormat.CSV
        )
        
        csv_text = result['content']
        
        reader = csv.DictReader(io.StringIO(csv_text))
        headers = reader.fieldnames
        
        assert headers is not None
        assert len(headers) > 0
    
    def test_export_with_protocol_only(self):
        """Test exporting protocol without CRF."""
        result = self.exporter.export(
            self.protocol,
            self.crf,
            ExportFormat.FHIR_JSON,
            include_protocol=True,
            include_crf=False
        )
        
        assert result is not None
        assert 'content' in result
    
    def test_export_with_crf_only(self):
        """Test exporting CRF without protocol."""
        result = self.exporter.export(
            self.protocol,
            self.crf,
            ExportFormat.CSV,
            include_protocol=False,
            include_crf=True
        )
        
        assert result is not None
        assert 'content' in result
    
    def test_export_minimal_protocol(self):
        """Test exporting minimal protocol."""
        spec = TrialSpecInput(
            sponsor="Minimal Pharma",
            title="Minimal Study",
            indication="Test",
            phase=TrialPhase.PHASE_1,
            design="open-label",
            sample_size=10,
            duration_weeks=2,
            key_endpoints=[
                TrialEndpoint(type=EndpointType.PRIMARY, name="Safety")
            ],
            inclusion_criteria=["Healthy"],
            exclusion_criteria=["Pregnant"],
            region="US"
        )
        
        protocol = self.generator.generate_structured_protocol(spec)
        crf = self.crf_generator.generate_crf_schema(spec, protocol)
        
        # Should not raise errors for any format
        odm_result = self.exporter.export(protocol, crf, ExportFormat.ODM_XML)
        fhir_result = self.exporter.export(protocol, crf, ExportFormat.FHIR_JSON)
        csv_result = self.exporter.export(protocol, crf, ExportFormat.CSV)
        
        assert odm_result is not None
        assert fhir_result is not None
        assert csv_result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
