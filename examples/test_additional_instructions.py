"""
Test Additional Instructions Feature

This demonstrates how users can provide custom instructions to guide LLM generation.
"""

from app.models.schemas import TrialSpecInput, TrialPhase, TrialEndpoint, EndpointType
from app.services.generator import ProtocolTemplateGenerator

print("=" * 80)
print("TESTING ADDITIONAL INSTRUCTIONS FEATURE")
print("=" * 80)

# Test 1: Protocol WITHOUT additional instructions
print("\n[TEST 1] Lung Cancer Protocol - No Additional Instructions")
print("-" * 80)

spec_baseline = TrialSpecInput(
    sponsor="Test Pharma",
    title="NSCLC Immunotherapy Trial",
    indication="Non-Small Cell Lung Cancer",
    phase=TrialPhase.PHASE_2,
    design="randomized, double-blind, placebo-controlled",
    sample_size=200,
    duration_weeks=24,
    region="US",
    treatment_arms=["Experimental Drug", "Placebo"],
    inclusion_criteria=[],
    exclusion_criteria=[],
    key_endpoints=[
        TrialEndpoint(
            type=EndpointType.PRIMARY,
            name="Objective Response Rate",
            description="",
            measurement_timepoint="Week 24"
        )
    ]
    # No additional_instructions provided
)

gen = ProtocolTemplateGenerator(use_rag=True, use_llm=True)
protocol_baseline = gen.generate_structured_protocol(spec_baseline)

print("\nObjectives Generated:")
print(f"Primary: {protocol_baseline.objectives['primary'][:150]}...")
print(f"\nFirst 3 Inclusion Criteria:")
for i, criterion in enumerate(protocol_baseline.inclusion_criteria[:3], 1):
    print(f"{i}. {criterion}")

# Test 2: Protocol WITH additional instructions
print("\n\n[TEST 2] Lung Cancer Protocol - WITH Additional Instructions")
print("-" * 80)

spec_custom = TrialSpecInput(
    sponsor="Test Pharma",
    title="NSCLC Immunotherapy Trial",
    indication="Non-Small Cell Lung Cancer",
    phase=TrialPhase.PHASE_2,
    design="randomized, double-blind, placebo-controlled",
    sample_size=200,
    duration_weeks=24,
    region="US",
    treatment_arms=["Experimental Drug", "Placebo"],
    inclusion_criteria=[],
    exclusion_criteria=[],
    key_endpoints=[
        TrialEndpoint(
            type=EndpointType.PRIMARY,
            name="Objective Response Rate",
            description="",
            measurement_timepoint="Week 24"
        )
    ],
    additional_instructions="""
    IMPORTANT REQUIREMENTS:
    - This trial must include COVID-19 safety measures and remote monitoring options
    - Focus on elderly population (age 65+) with special attention to frailty assessment
    - Must include biomarker analysis for PD-L1 expression levels
    - Require prior chemotherapy exposure
    - Include quality of life assessments specifically for elderly patients
    - Mention telemedicine visits for safety monitoring
    """
)

protocol_custom = gen.generate_structured_protocol(spec_custom)

print("\nObjectives Generated:")
print(f"Primary: {protocol_custom.objectives['primary'][:150]}...")
print(f"\nFirst 5 Inclusion Criteria:")
for i, criterion in enumerate(protocol_custom.inclusion_criteria[:5], 1):
    print(f"{i}. {criterion}")

# Test 3: Dermatology with specific instructions
print("\n\n[TEST 3] Acne Trial - Custom Pediatric Instructions")
print("-" * 80)

spec_pediatric = TrialSpecInput(
    sponsor="Test Pharma",
    title="Pediatric Acne Treatment Trial",
    indication="Acne Vulgaris",
    phase=TrialPhase.PHASE_3,
    design="randomized, double-blind, vehicle-controlled",
    sample_size=150,
    duration_weeks=12,
    region="US",
    treatment_arms=["Investigational Gel", "Vehicle Gel"],
    inclusion_criteria=[],
    exclusion_criteria=[],
    key_endpoints=[
        TrialEndpoint(
            type=EndpointType.PRIMARY,
            name="Lesion Count Reduction",
            description="",
            measurement_timepoint="Week 12"
        )
    ],
    additional_instructions="""
    PEDIATRIC REQUIREMENTS:
    - Age range: 12-17 years only (adolescent population)
    - Require parental consent AND adolescent assent
    - Exclude patients using other acne medications within 2 weeks
    - Include standardized photography with consistent lighting
    - Add age-appropriate quality of life questionnaire (CADI or similar)
    - Mention school schedule accommodations for visits
    - Include patient education materials in simple language
    """
)

protocol_pediatric = gen.generate_structured_protocol(spec_pediatric)

print("\nFirst 5 Inclusion Criteria:")
for i, criterion in enumerate(protocol_pediatric.inclusion_criteria[:5], 1):
    print(f"{i}. {criterion}")

print("\nFirst 3 Exclusion Criteria:")
for i, criterion in enumerate(protocol_pediatric.exclusion_criteria[:3], 1):
    print(f"{i}. {criterion}")

# Analysis
print("\n" + "=" * 80)
print("ANALYSIS")
print("=" * 80)

print("\nDifferences Detected:")
print(f"✓ Baseline protocol has {len(protocol_baseline.inclusion_criteria)} inclusion criteria")
print(f"✓ Custom protocol has {len(protocol_custom.inclusion_criteria)} inclusion criteria")
print(f"✓ Pediatric protocol has {len(protocol_pediatric.inclusion_criteria)} inclusion criteria")

# Check for keywords from instructions
custom_criteria_text = " ".join(protocol_custom.inclusion_criteria).lower()
pediatric_criteria_text = " ".join(protocol_pediatric.inclusion_criteria).lower()

print("\nKeyword Detection in Custom Protocol:")
keywords_custom = ["covid", "elderly", "65", "biomarker", "pd-l1", "frailty", "telemedicine"]
found_custom = [kw for kw in keywords_custom if kw in custom_criteria_text]
print(f"  Found: {found_custom}")

print("\nKeyword Detection in Pediatric Protocol:")
keywords_pediatric = ["12", "17", "adolescent", "parental", "assent", "photography", "school"]
found_pediatric = [kw for kw in keywords_pediatric if kw in pediatric_criteria_text]
print(f"  Found: {found_pediatric}")

if found_custom and found_pediatric:
    print("\n✅ SUCCESS! Additional instructions are being incorporated into generated content!")
else:
    print("\n⚠ Check: Some keywords may not have been incorporated")

print("\n" + "=" * 80)
print("USAGE EXAMPLES")
print("=" * 80)
print("""
The additional_instructions field allows users to:

1. **Regulatory Requirements**: "Include FDA guidance for rare diseases"
2. **Population-Specific**: "Focus on geriatric population with age ≥75"
3. **COVID-19 Adaptations**: "Include remote monitoring and decentralized trial options"
4. **Biomarker Requirements**: "Require specific genetic mutation testing"
5. **Geographic Considerations**: "Adapt for Japanese regulatory requirements"
6. **Safety Focus**: "Emphasize cardiac safety monitoring"
7. **Prior Therapy**: "Require failure of at least 2 prior therapies"
8. **Technology**: "Include wearable device monitoring"

Simply add these instructions to the trial specification, and the LLM will
incorporate them into objectives, inclusion/exclusion criteria, and other sections.
""")
