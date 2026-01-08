"""
Comprehensive test for Additional Instructions feature.
Tests that custom instructions influence ALL LLM-generated sections:
- Objectives
- Inclusion Criteria
- Exclusion Criteria
- Study Design
- Visit Schedule
- Assessments
- CRF Forms
"""

import sys
import os

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.schemas import TrialSpecInput, TrialPhase, TrialEndpoint, EndpointType
from app.services.generator import ProtocolTemplateGenerator
from app.services.rag_service import RAGService


def test_with_custom_instructions():
    """Test protocol generation with comprehensive custom instructions."""
    
    print("\n" + "="*80)
    print("TEST: Lung Cancer Protocol with Comprehensive Custom Instructions")
    print("="*80)
    
    # Initialize services
    rag_service = RAGService()
    generator = ProtocolTemplateGenerator(use_llm=True, use_rag=True)
    
    # Comprehensive custom instructions
    custom_instructions = """
STUDY POPULATION & SAFETY:
- Target elderly population aged 65 and above only
- Require COVID-19 vaccination or recent negative test
- Include telemedicine visits for remote monitoring
- Allow home nursing visits for frail patients

BIOMARKERS & DIAGNOSTICS:
- Mandatory PD-L1 biomarker testing (TPS ≥50%)
- Include ctDNA blood testing for molecular monitoring
- Require baseline and serial tumor genomic profiling

DESIGN & ASSESSMENTS:
- Use virtual tumor board reviews for response assessment
- Include patient-reported outcomes (PRO-CTCAE) at every visit
- Add geriatric assessment tools (e.g., G8 screening, Charlson Comorbidity Index)
- Incorporate wearable devices for continuous vitals monitoring

CRF DATA COLLECTION:
- Capture detailed biomarker results and dates
- Include fields for telemedicine visit quality indicators
- Add geriatric-specific functional status measures
- Record wearable device data integration
"""
    
    spec = TrialSpecInput(
        sponsor="Elder Oncology Research Institute",
        title="A Phase II Study of Immunotherapy in Elderly NSCLC Patients",
        indication="Non-Small Cell Lung Cancer",
        phase=TrialPhase.PHASE_2,
        design="Single-arm, open-label",
        sample_size=80,
        duration_weeks=52,
        region="Global",
        inclusion_criteria=[
            "Age 65 years and older",
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
            ),
            TrialEndpoint(
                type=EndpointType.SECONDARY,
                name="Quality of Life",
                description="Patient-reported outcomes",
                measurement_timepoint="Every visit"
            )
        ],
        additional_instructions=custom_instructions
    )
    
    # Generate protocol
    print("\nGenerating protocol with custom instructions...\n")
    protocol = generator.generate_structured_protocol(spec)
    crf = generator.generate_crf_schema(spec, protocol)
    
    # Define keywords to check across sections
    keywords_to_check = {
        'elderly': ['elderly', '65 and above', 'geriatric', 'age 65', 'older adult'],
        'covid': ['COVID-19', 'COVID', 'vaccination', 'negative test'],
        'biomarker': ['PD-L1', 'biomarker', 'TPS', 'ctDNA', 'genomic'],
        'telemedicine': ['telemedicine', 'remote', 'virtual', 'home nursing'],
        'wearable': ['wearable', 'continuous monitoring', 'device'],
        'pro': ['patient-reported', 'PRO-CTCAE', 'quality of life'],
        'geriatric_assessment': ['geriatric assessment', 'G8', 'Charlson', 'functional status']
    }
    
    results = {}
    
    # Check Study Design
    print("\n" + "-"*80)
    print("STUDY DESIGN")
    print("-"*80)
    print(protocol.study_design)
    results['study_design'] = check_keywords(protocol.study_design, keywords_to_check)
    
    # Check Objectives
    print("\n" + "-"*80)
    print("OBJECTIVES")
    print("-"*80)
    obj_text = f"{protocol.objectives.get('primary', '')} {protocol.objectives.get('secondary', '')}"
    print(obj_text)
    results['objectives'] = check_keywords(obj_text, keywords_to_check)
    
    # Check Inclusion Criteria
    print("\n" + "-"*80)
    print("INCLUSION CRITERIA")
    print("-"*80)
    inclusion_text = "\n".join(protocol.inclusion_criteria)
    print(inclusion_text)
    results['inclusion_criteria'] = check_keywords(inclusion_text, keywords_to_check)
    
    # Check Exclusion Criteria
    print("\n" + "-"*80)
    print("EXCLUSION CRITERIA")
    print("-"*80)
    exclusion_text = "\n".join(protocol.exclusion_criteria)
    print(exclusion_text)
    results['exclusion_criteria'] = check_keywords(exclusion_text, keywords_to_check)
    
    # Check Visit Schedule
    print("\n" + "-"*80)
    print("VISIT SCHEDULE (First 5 visits)")
    print("-"*80)
    for visit in protocol.visit_schedule[:5]:
        print(f"  - {visit.get('visit_name', 'N/A')} (Week {visit.get('week', '?')}): {visit.get('window', '')}")
    visit_text = str(protocol.visit_schedule)
    results['visit_schedule'] = check_keywords(visit_text, keywords_to_check)
    
    # Check Assessments
    print("\n" + "-"*80)
    print("ASSESSMENTS")
    print("-"*80)
    for assessment in protocol.assessments[:8]:
        print(f"  - {assessment.get('name', 'N/A')}: {assessment.get('description', '')[:100]}")
    assessment_text = str(protocol.assessments)
    results['assessments'] = check_keywords(assessment_text, keywords_to_check)
    
    # Check CRF Forms
    if crf:
        print("\n" + "-"*80)
        print("CRF FORMS")
        print("-"*80)
        crf_text = ""
        for form in crf.forms[:10]:
            print(f"\n  Form: {form.form_name}")
            for field in form.fields[:5]:
                field_info = f"    - {field.field_label} ({field.data_type})"
                print(field_info)
                crf_text += field_info + " "
        results['crf_forms'] = check_keywords(crf_text, keywords_to_check)
    
    # Summary Report
    print("\n" + "="*80)
    print("SUMMARY: Keywords Found by Section")
    print("="*80)
    
    for section, findings in results.items():
        print(f"\n{section.upper().replace('_', ' ')}:")
        for category, keywords in findings.items():
            if keywords:
                print(f"  [+] {category}: {', '.join(keywords)}")
            else:
                print(f"  [-] {category}: Not found")
    
    # Overall assessment
    print("\n" + "="*80)
    print("OVERALL ASSESSMENT")
    print("="*80)
    
    total_categories = len(keywords_to_check)
    categories_found = {cat for findings in results.values() for cat, kw in findings.items() if kw}
    
    print(f"\nCategories found across all sections: {len(categories_found)}/{total_categories}")
    print(f"Sections that incorporated custom instructions: {len([r for r in results.values() if any(r.values())])}/{len(results)}")
    
    if len(categories_found) >= 5:
        print("\n[SUCCESS] Custom instructions were effectively incorporated!")
    else:
        print("\n[PARTIAL] Some custom instructions may not have been incorporated")
    
    return {'protocol': protocol, 'crf': crf}


def check_keywords(text: str, keyword_groups: dict) -> dict:
    """Check which keywords from each group appear in the text."""
    text_lower = text.lower()
    results = {}
    
    for category, keywords in keyword_groups.items():
        found = [kw for kw in keywords if kw.lower() in text_lower]
        results[category] = found
    
    return results


def test_baseline_comparison():
    """Generate baseline protocol without additional instructions for comparison."""
    
    print("\n" + "="*80)
    print("BASELINE: Lung Cancer Protocol WITHOUT Custom Instructions")
    print("="*80)
    
    rag_service = RAGService()
    generator = ProtocolTemplateGenerator(use_llm=True, use_rag=True)
    
    spec = TrialSpecInput(
        sponsor="Standard Oncology Group",
        title="A Phase II Study of Immunotherapy in NSCLC Patients",
        indication="Non-Small Cell Lung Cancer",
        phase=TrialPhase.PHASE_2,
        design="Single-arm, open-label",
        sample_size=80,
        duration_weeks=52,
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
        additional_instructions=None  # No custom instructions
    )
    
    protocol = generator.generate_structured_protocol(spec)
    
    print("\nStudy Design (baseline):")
    print(protocol.study_design)
    
    print("\nInclusion Criteria (baseline):")
    for criterion in protocol.inclusion_criteria[:5]:
        print(f"  - {criterion}")
    
    print("\nAssessments (baseline):")
    for assessment in protocol.assessments[:5]:
        print(f"  - {assessment.get('name', 'N/A')}")
    
    return protocol


if __name__ == "__main__":
    print("\n" + "="*80)
    print("COMPREHENSIVE ADDITIONAL INSTRUCTIONS TEST")
    print("Testing: Objectives, Criteria, Design, Visits, Assessments, CRF Forms")
    print("="*80)
    
    # Run baseline first (synchronous)
    test_baseline_comparison()
    
    # Run with custom instructions (synchronous)
    test_with_custom_instructions()
