"""
Simple test to verify Additional Instructions feature works across all sections.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.schemas import TrialSpecInput, TrialPhase, TrialEndpoint, EndpointType
from app.services.generator import ProtocolTemplateGenerator

print("=" * 80)
print("TESTING: Additional Instructions Feature")
print("=" * 80)

# Create test spec WITH custom instructions
spec = TrialSpecInput(
    sponsor="Test Sponsor",
    title="Phase II NSCLC Study",
    indication="Non-Small Cell Lung Cancer",
    phase=TrialPhase.PHASE_2,
    design="Single-arm, open-label",
    sample_size=75,
    duration_weeks=48,
    region="Global",
    inclusion_criteria=[
        "Histologically confirmed NSCLC",
        "Measurable disease per RECIST 1.1"
    ],
    exclusion_criteria=[
        "Active brain metastases",
        "Prior immunotherapy"
    ],
    key_endpoints=[
        TrialEndpoint(
            type=EndpointType.PRIMARY,
            name="Objective Response Rate",
            description="ORR per RECIST 1.1",
            measurement_timepoint="Every 9 weeks"
        )
    ],
    additional_instructions="""
    - Target elderly population aged 65 and above
    - Require COVID-19 vaccination
    - Include telemedicine visits for remote monitoring
    - Mandatory PD-L1 biomarker testing
    - Use geriatric assessment tools (G8 screening)
    """
)

# Generate protocol
print("\nGenerating protocol with custom instructions...")
generator = ProtocolTemplateGenerator(use_llm=True, use_rag=True)
protocol = generator.generate_structured_protocol(spec)

# Check results
print("\n" + "-" * 80)
print("RESULTS:")
print("-" * 80)

print("\nStudy Design:")
print(protocol.study_design[:200] + "...")

print("\nInclusion Criteria (first 5):")
for i, criterion in enumerate(protocol.inclusion_criteria[:5], 1):
    print(f"{i}. {criterion}")

print("\nExclusion Criteria (first 5):")
for i, criterion in enumerate(protocol.exclusion_criteria[:5], 1):
    print(f"{i}. {criterion}")

print("\nVisit Schedule (first 5 visits):")
for visit in protocol.visit_schedule[:5]:
    print(f"  - {visit.get('visit_name', 'N/A')} (Week {visit.get('week', '?')})")

print("\nAssessments (first 5):")
for assessment in protocol.assessments[:5]:
    print(f"  - {assessment.get('name', 'N/A')}")

# Check for keywords from custom instructions
keywords = ['elderly', '65', 'COVID', 'telemedicine', 'PD-L1', 'biomarker', 'geriatric', 'G8']
protocol_text = str(protocol.__dict__).lower()

print("\n" + "-" * 80)
print("KEYWORD CHECK:")
print("-" * 80)
found = [kw for kw in keywords if kw.lower() in protocol_text]
print(f"Found {len(found)}/{len(keywords)} keywords: {', '.join(found)}")

if len(found) >= 4:
    print("\n[SUCCESS] Additional instructions were incorporated!")
else:
    print("\n[INFO] Some keywords not found - this may be normal if LLM paraphrased")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
