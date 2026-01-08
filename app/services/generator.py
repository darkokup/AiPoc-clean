"""Template-based protocol and CRF generator with RAG and LLM support."""
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
from app.models.schemas import (
    TrialSpecInput,
    ProtocolStructured,
    ProtocolSection,
    CRFSchema,
    CRFForm,
    CRFField,
    VisitDefinition,
)


class ProtocolTemplateGenerator:
    """Generates protocol content using templates, RAG, and LLM."""
    
    def __init__(self, use_rag: bool = True, use_llm: bool = True):
        """
        Initialize the generator with standard templates.
        
        Args:
            use_rag: Whether to use RAG for retrieval-augmented generation
            use_llm: Whether to use LLM for enhanced content generation
        """
        self.templates = self._load_templates()
        self.use_rag = use_rag
        self.use_llm = use_llm
        self.rag_service = None
        self.llm_service = None
        
        # Initialize RAG
        if use_rag:
            try:
                from app.services.rag_service import get_rag_service
                self.rag_service = get_rag_service()
                print("✓ RAG enabled for protocol generation")
            except Exception as e:
                print(f"⚠ RAG initialization failed: {e}. Falling back to template-only mode.")
                self.use_rag = False
        
        # Initialize LLM
        if use_llm:
            try:
                from app.services.llm_service import get_llm_service
                self.llm_service = get_llm_service()
                print("✓ LLM enabled for AI-enhanced protocol generation")
            except Exception as e:
                print(f"⚠ LLM initialization failed: {e}. Falling back to template-only mode.")
                self.use_llm = False
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load protocol section templates."""
        return {
            "synopsis": """
Study Synopsis

Title: {title}
Sponsor: {sponsor}
Phase: {phase}
Indication: {indication}

Study Design: This is a {design} study evaluating {indication}.
Sample Size: Approximately {sample_size} participants will be enrolled.
Study Duration: {duration_weeks} weeks.
""",
            "objectives": {
                "primary": "To evaluate the efficacy of the study intervention in patients with {indication}.",
                "secondary": "To assess the safety and tolerability of the study intervention.",
            },
            "background": """
Background and Rationale

{indication} is a significant health concern requiring effective therapeutic interventions.
This study aims to evaluate {title} with the goal of demonstrating clinical benefit.
""",
        }
    
    def generate_protocol_narrative(self, spec: TrialSpecInput) -> str:
        """Generate human-readable protocol narrative with RAG enhancement."""
        sections = []
        
        # Get similar protocols if RAG is enabled
        rag_context = ""
        if self.use_rag and self.rag_service:
            try:
                similar_protocols = self.rag_service.retrieve_similar_protocols(spec, n_results=2)
                if similar_protocols:
                    rag_context = self._generate_rag_context(similar_protocols)
                    sections.append(f"<!-- RAG Context: Found {len(similar_protocols)} similar protocol(s) -->")
            except Exception as e:
                print(f"⚠ RAG retrieval error: {e}")
        
        # Title Page
        sections.append(f"CLINICAL TRIAL PROTOCOL\n\n{spec.title}\n")
        sections.append(f"Protocol Version: 1.0")
        sections.append(f"Sponsor: {spec.sponsor}")
        sections.append(f"Date: {datetime.now().strftime('%Y-%m-%d')}\n")
        
        # Add RAG insights if available
        if rag_context:
            sections.append("\n" + rag_context + "\n")
        
        # Synopsis
        synopsis = self.templates["synopsis"].format(
            title=spec.title,
            sponsor=spec.sponsor,
            phase=spec.phase.value,
            indication=spec.indication,
            design=spec.design,
            sample_size=spec.sample_size,
            duration_weeks=spec.duration_weeks,
        )
        sections.append(synopsis)
        
        # Background
        background = spec.background if spec.background else self.templates["background"].format(
            indication=spec.indication,
            title=spec.title
        )
        sections.append(background)
        
        # Objectives and Endpoints
        sections.append("\nStudy Objectives and Endpoints\n")
        sections.append("\nPrimary Objective:")
        sections.append(self.templates["objectives"]["primary"].format(indication=spec.indication))
        
        sections.append("\n\nEndpoints:")
        for endpoint in spec.key_endpoints:
            sections.append(f"- {endpoint.type.value.upper()}: {endpoint.name}")
        
        # Study Design
        sections.append(f"\n\nStudy Design\n")
        sections.append(f"This is a {spec.design} study.")
        if spec.treatment_arms:
            sections.append(f"\nTreatment Arms:")
            for i, arm in enumerate(spec.treatment_arms, 1):
                sections.append(f"  {i}. {arm}")
        
        # Study Population
        sections.append(f"\n\nStudy Population\n")
        sections.append(f"Target enrollment: {spec.sample_size} participants")
        if spec.age_range:
            sections.append(f"Age range: {spec.age_range}")
        
        sections.append("\nInclusion Criteria:")
        for i, criterion in enumerate(spec.inclusion_criteria, 1):
            sections.append(f"  {i}. {criterion}")
        
        sections.append("\nExclusion Criteria:")
        for i, criterion in enumerate(spec.exclusion_criteria, 1):
            sections.append(f"  {i}. {criterion}")
        
        # Study Duration
        sections.append(f"\n\nStudy Duration and Schedule\n")
        sections.append(f"Total study duration: {spec.duration_weeks} weeks per participant")
        
        # Statistical Considerations
        sections.append(f"\n\nStatistical Considerations\n")
        sections.append(f"Sample Size: {spec.sample_size} participants")
        sections.append("Statistical analysis will be performed on the intent-to-treat (ITT) population.")
        
        # Safety Monitoring
        sections.append("\n\nSafety Monitoring\n")
        sections.append("Adverse events will be monitored throughout the study and graded according to CTCAE v5.0.")
        sections.append("A Data Safety Monitoring Board (DSMB) will review safety data periodically.")
        
        return "\n".join(sections)
    
    def generate_structured_protocol(self, spec: TrialSpecInput) -> ProtocolStructured:
        """Generate structured protocol JSON with RAG enhancement."""
        protocol_id = f"PROT-{uuid.uuid4().hex[:8].upper()}"
        
        # Track what was enhanced by LLM
        llm_enhanced_sections = []
        
        # Get similar protocols for enhanced generation
        similar_protocols = []
        generation_method = "template_based"
        templates_used = ["standard_protocol_v1"]
        
        if self.use_rag and self.rag_service:
            try:
                similar_protocols = self.rag_service.retrieve_similar_protocols(spec, n_results=3)
                if similar_protocols:
                    generation_method = "rag_enhanced"
                    templates_used.append("rag_retrieved_examples")
                    print(f"✓ Using {len(similar_protocols)} similar protocol(s) for enhanced generation")
            except Exception as e:
                print(f"⚠ RAG retrieval error: {e}")
        
        # Track if LLM is being used
        if self.use_llm and self.llm_service:
            generation_method = "llm_enhanced" if similar_protocols else "llm_only"
        
        # Generate objectives (enhanced with RAG if available)
        objectives = self._generate_objectives(spec, similar_protocols)
        if self.use_llm and self.llm_service:
            llm_enhanced_sections.append("objectives")
        
        # Generate inclusion criteria (enhanced with LLM if available)
        inclusion_criteria = self._generate_inclusion_criteria(spec, similar_protocols)
        if self.use_llm and self.llm_service:
            llm_enhanced_sections.append("inclusion_criteria")
        
        # Generate exclusion criteria (enhanced with LLM if available)
        exclusion_criteria = self._generate_exclusion_criteria(spec, similar_protocols)
        if self.use_llm and self.llm_service:
            llm_enhanced_sections.append("exclusion_criteria")
        
        # Generate enhanced study design (enhanced with LLM if available)
        study_design = self._generate_study_design(spec, similar_protocols)
        if self.use_llm and self.llm_service:
            llm_enhanced_sections.append("study_design")
        
        # Format endpoints (enhanced with LLM if available)
        endpoints = self._generate_endpoints(spec, similar_protocols)
        if self.use_llm and self.llm_service:
            llm_enhanced_sections.append("endpoints")
        
        # Generate visit schedule (indication-specific if LLM available)
        visit_schedule = self._generate_visit_schedule(spec, similar_protocols)
        if self.use_llm and self.llm_service:
            llm_enhanced_sections.append("visit_schedule")
        
        # Generate assessments (indication-specific if LLM available)
        assessments = self._generate_assessments(spec, similar_protocols)
        if self.use_llm and self.llm_service:
            llm_enhanced_sections.append("assessments")
        
        # Statistical plan
        statistical_plan = {
            "sample_size": spec.sample_size,
            "power": 0.80,
            "alpha": 0.05,
            "analysis_populations": ["ITT", "Per Protocol", "Safety"],
            "primary_analysis": "ANCOVA adjusting for baseline",
        }
        
        # Safety monitoring
        safety_monitoring = {
            "ae_reporting": "CTCAE v5.0",
            "dsmb": True,
            "interim_analyses": ["25%", "50%", "75%"],
        }
        
        # Generate narrative sections
        sections = self._generate_protocol_sections(spec, objectives, similar_protocols)
        
        # Calculate average RAG similarity if protocols were retrieved
        rag_avg_similarity = None
        if similar_protocols:
            similarities = [p.get('similarity_score', 0) for p in similar_protocols if p.get('similarity_score') is not None]
            if similarities:
                rag_avg_similarity = sum(similarities) / len(similarities)
        
        return ProtocolStructured(
            protocol_id=protocol_id,
            version="1.0",
            generated_at=datetime.now(),
            sponsor=spec.sponsor,
            title=spec.title,
            short_title=spec.short_title or spec.title[:50],
            phase=spec.phase.value,
            indication=spec.indication,
            study_design=study_design,
            sample_size=spec.sample_size,
            duration_weeks=spec.duration_weeks,
            treatment_arms=spec.treatment_arms or ["Intervention", "Control"],
            objectives=objectives,
            endpoints=endpoints,
            inclusion_criteria=inclusion_criteria,
            exclusion_criteria=exclusion_criteria,
            visit_schedule=visit_schedule,
            assessments=assessments,
            statistical_plan=statistical_plan,
            safety_monitoring=safety_monitoring,
            sections=sections,
            generation_method=generation_method,
            rag_protocols_used=len(similar_protocols) if similar_protocols else None,
            rag_avg_similarity=rag_avg_similarity,
            llm_enhanced_sections=llm_enhanced_sections if llm_enhanced_sections else None,
        )
    
    def _generate_objectives(
        self,
        spec: TrialSpecInput,
        similar_protocols: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Generate objectives, enhanced with LLM if available."""
        
        # Use LLM if available
        if self.use_llm and self.llm_service:
            try:
                trial_spec_dict = {
                    "title": spec.title,
                    "phase": spec.phase.value,
                    "indication": spec.indication,
                    "design": spec.design,
                }
                objectives = self.llm_service.generate_objectives(
                    trial_spec=trial_spec_dict,
                    rag_context=similar_protocols,
                    additional_instructions=spec.additional_instructions
                )
                print("✓ Objectives generated using LLM")
                return objectives
            except Exception as e:
                print(f"⚠ LLM objective generation failed: {e}. Using template fallback.")
        
        # Template fallback
        objectives = {
            "primary": self.templates["objectives"]["primary"].format(indication=spec.indication),
            "secondary": self.templates["objectives"]["secondary"],
        }
        
        # Enhance with similar protocol objectives if available (template mode)
        if similar_protocols:
            # Extract objectives from similar protocols for context
            similar_objectives = []
            for protocol in similar_protocols[:2]:
                if 'protocol' in protocol and 'objectives' in protocol['protocol']:
                    similar_objectives.append(protocol['protocol']['objectives'])
            
            # In template mode, we keep the base template
            # LLM mode would blend these examples
        
        return objectives
    
    def _generate_inclusion_criteria(
        self,
        spec: TrialSpecInput,
        similar_protocols: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate inclusion criteria, enhanced with LLM if available."""
        
        # Use LLM if available
        if self.use_llm and self.llm_service:
            try:
                trial_spec_dict = {
                    "phase": spec.phase.value,
                    "indication": spec.indication,
                    "design": spec.design,
                }
                criteria = self.llm_service.generate_inclusion_criteria(
                    trial_spec=trial_spec_dict,
                    rag_context=similar_protocols,
                    additional_instructions=spec.additional_instructions
                )
                print("✓ Inclusion criteria generated using LLM")
                return criteria
            except Exception as e:
                print(f"⚠ LLM inclusion criteria generation failed: {e}. Using input fallback.")
        
        # Fallback to user input or generic template
        if spec.inclusion_criteria:
            return spec.inclusion_criteria
        
        # Generic template fallback
        return [
            f"Adults aged 18-75 years with confirmed {spec.indication}",
            "Willing and able to provide informed consent",
            "Adequate organ function as defined by laboratory values",
        ]
    
    def _generate_exclusion_criteria(
        self,
        spec: TrialSpecInput,
        similar_protocols: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate exclusion criteria, enhanced with LLM if available."""
        
        # Use LLM if available
        if self.use_llm and self.llm_service:
            try:
                trial_spec_dict = {
                    "phase": spec.phase.value,
                    "indication": spec.indication,
                    "design": spec.design,
                }
                criteria = self.llm_service.generate_exclusion_criteria(
                    trial_spec=trial_spec_dict,
                    rag_context=similar_protocols,
                    additional_instructions=spec.additional_instructions
                )
                print("✓ Exclusion criteria generated using LLM")
                return criteria
            except Exception as e:
                print(f"⚠ LLM exclusion criteria generation failed: {e}. Using input fallback.")
        
        # Fallback to user input or generic template
        if spec.exclusion_criteria:
            return spec.exclusion_criteria
        
        # Generic template fallback
        return [
            "Pregnant or breastfeeding women",
            "Known hypersensitivity to study drug or excipients",
            "Severe comorbid conditions that would interfere with study participation",
        ]
    
    def _generate_study_design(
        self,
        spec: TrialSpecInput,
        similar_protocols: List[Dict[str, Any]]
    ) -> str:
        """Generate enhanced study design description."""
        
        # Use LLM if available to enhance the design description
        if self.use_llm and self.llm_service:
            try:
                # Build context from similar protocols
                rag_design_examples = ""
                if similar_protocols:
                    rag_design_examples = "\n\nSimilar Study Designs:\n"
                    for i, protocol in enumerate(similar_protocols[:2], 1):
                        metadata = protocol.get('metadata', {})
                        design = metadata.get('design', 'N/A')
                        rag_design_examples += f"{i}. {design}\n"
                
                # Add user instructions if provided
                user_instructions = ""
                if spec.additional_instructions:
                    user_instructions = f"\n\n## ADDITIONAL USER INSTRUCTIONS:\n{spec.additional_instructions}\n"
                
                prompt = f"""You are an expert clinical trial protocol writer specializing in {spec.indication}. Generate a detailed, professional study design description that is SPECIFIC to this indication.

Trial Specification:
- Phase: {spec.phase.value}
- Indication: {spec.indication}
- Basic Design: {spec.design}
- Sample Size: {spec.sample_size}
- Duration: {spec.duration_weeks} weeks
- Treatment Arms: {', '.join(spec.treatment_arms or ['Intervention', 'Control'])}
{rag_design_examples}{user_instructions}

CRITICAL: Make this design description SPECIFIC to {spec.indication}. Include:
1. Standard study type elements (randomized, controlled, blinding)
2. Indication-specific design features (e.g., for cancer: response criteria, for dermatology: lesion assessment, for diabetes: glycemic control monitoring)
3. Treatment groups/arms with indication-relevant details
4. Any unique design elements typical for {spec.indication} trials
5. Specific assessment or measurement approaches used in {spec.indication} studies

Generate 2-4 sentences that would make it CLEAR this is for {spec.indication} and not another disease.
Return ONLY the design description, no additional commentary."""

                response = self.llm_service.client.chat.completions.create(
                    model=self.llm_service.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=300,
                )
                
                enhanced_design = response.choices[0].message.content.strip()
                print("✓ Study design enhanced using LLM")
                return enhanced_design
                
            except Exception as e:
                print(f"⚠ LLM study design enhancement failed: {e}. Using input fallback.")
        
        # Fallback to basic input description
        return spec.design
    
    def _generate_endpoints(
        self,
        spec: TrialSpecInput,
        similar_protocols: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate enhanced endpoint descriptions."""
        
        endpoints = []
        
        for ep in spec.key_endpoints:
            endpoint_dict = {
                "type": ep.type.value,
                "name": ep.name,
                "description": ep.description,
                "timepoint": ep.measurement_timepoint,
            }
            
            # Enhance description with LLM if available and description is generic
            if self.use_llm and self.llm_service and (not ep.description or len(ep.description) < 50):
                try:
                    # Build context from similar endpoints
                    rag_endpoint_examples = ""
                    if similar_protocols:
                        rag_endpoint_examples = "\n\nSimilar Endpoint Examples:\n"
                        for i, protocol in enumerate(similar_protocols[:2], 1):
                            if 'protocol' in protocol and 'endpoints' in protocol['protocol']:
                                endpoints_list = protocol['protocol']['endpoints']
                                for similar_ep in endpoints_list[:2]:
                                    if similar_ep.get('type') == ep.type.value:
                                        rag_endpoint_examples += f"- {similar_ep.get('name', 'N/A')}: {similar_ep.get('description', 'N/A')}\n"
                    
                    prompt = f"""You are an expert clinical trial protocol writer. Generate a detailed, professional endpoint description.

Endpoint Information:
- Type: {ep.type.value}
- Name: {ep.name}
- Indication: {spec.indication}
- Timepoint: {ep.measurement_timepoint}
{rag_endpoint_examples}

Generate a clear, specific endpoint description (1-2 sentences) that explains:
1. What is being measured
2. How it will be assessed
3. Clinical relevance

Return ONLY the endpoint description, no additional commentary."""

                    response = self.llm_service.client.chat.completions.create(
                        model=self.llm_service.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        max_tokens=200,
                    )
                    
                    enhanced_description = response.choices[0].message.content.strip()
                    endpoint_dict["description"] = enhanced_description
                    
                except Exception as e:
                    print(f"⚠ LLM endpoint enhancement failed: {e}. Using original.")
            
            endpoints.append(endpoint_dict)
        
        if endpoints:
            print(f"✓ Generated {len(endpoints)} endpoint(s)")
        
        return endpoints
    
    def _generate_visit_schedule(
        self,
        spec: TrialSpecInput,
        similar_protocols: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate visit schedule, enhanced with LLM for indication-specific timing."""
        
        # Use LLM for indication-specific visit timing if available
        if self.use_llm and self.llm_service:
            try:
                # Build context from similar protocols
                rag_visit_examples = ""
                if similar_protocols:
                    rag_visit_examples = "\n\nSimilar Protocol Visit Schedules:\n"
                    for i, protocol in enumerate(similar_protocols[:2], 1):
                        if 'protocol' in protocol and 'visit_schedule' in protocol['protocol']:
                            visits = protocol['protocol']['visit_schedule']
                            visit_summary = [f"Week {v.get('week', '?')}" for v in visits[:5]]
                            rag_visit_examples += f"{i}. Visits at: {', '.join(visit_summary)}\n"
                
                # Add user instructions if provided
                user_instructions = ""
                if spec.additional_instructions:
                    user_instructions = f"\n\n## ADDITIONAL USER INSTRUCTIONS:\n{spec.additional_instructions}\n"
                
                prompt = f"""You are an expert clinical trial protocol writer specializing in {spec.indication}. Generate a visit schedule appropriate for this trial.

Trial Specification:
- Phase: {spec.phase.value}
- Indication: {spec.indication}
- Duration: {spec.duration_weeks} weeks
- Sample Size: {spec.sample_size}
{rag_visit_examples}{user_instructions}

Generate a visit schedule with appropriate timing for {spec.indication} studies. Return ONLY a JSON array of visit objects.
Each visit should have: visit_id, visit_name, week, window.

Example format:
[
  {{"visit_id": "V0", "visit_name": "Screening", "week": -1, "window": "±3 days"}},
  {{"visit_id": "V1", "visit_name": "Baseline", "week": 0, "window": "Day 1"}},
  {{"visit_id": "V2", "visit_name": "Week 4", "week": 4, "window": "±7 days"}}
]

CRITICAL: Make timing appropriate for {spec.indication}:
- Cancer trials: Often every 3-4 weeks for tumor assessments
- Dermatology: Often every 2-4 weeks for skin assessments
- Metabolic: Often every 4-8 weeks for lab work
- Generate visits from Screening through Week {spec.duration_weeks}

Return ONLY the JSON array, no other text."""

                response = self.llm_service.client.chat.completions.create(
                    model=self.llm_service.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=800,
                )
                
                llm_response = response.choices[0].message.content.strip()
                
                # Try to parse JSON from response
                import json
                import re
                
                # Extract JSON array from response
                json_match = re.search(r'\[.*\]', llm_response, re.DOTALL)
                if json_match:
                    visits = json.loads(json_match.group())
                    print(f"✓ Generated {len(visits)} indication-specific visits using LLM")
                    return visits
                else:
                    print("⚠ Could not parse LLM visit schedule. Using template.")
                    
            except Exception as e:
                print(f"⚠ LLM visit schedule generation failed: {e}. Using template.")
        
        # Fallback: Generic visit schedule
        visits = []
        
        # Screening
        visits.append({
            "visit_id": "V0",
            "visit_name": "Screening",
            "week": -1,
            "window": "±3 days",
        })
        
        # Baseline
        visits.append({
            "visit_id": "V1",
            "visit_name": "Baseline/Day 1",
            "week": 0,
            "window": "Day 1",
        })
        
        # Follow-up visits (every 4 weeks as example)
        visit_num = 2
        for week in range(4, spec.duration_weeks + 1, 4):
            visits.append({
                "visit_id": f"V{visit_num}",
                "visit_name": f"Week {week}",
                "week": week,
                "window": "±7 days",
            })
            visit_num += 1
        
        # End of study
        if spec.duration_weeks not in [v["week"] for v in visits]:
            visits.append({
                "visit_id": f"V{visit_num}",
                "visit_name": f"End of Study (Week {spec.duration_weeks})",
                "week": spec.duration_weeks,
                "window": "±7 days",
            })
        
        return visits
    
    def _generate_assessments(
        self,
        spec: TrialSpecInput,
        similar_protocols: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate assessments, enhanced with LLM for indication-specific evaluations."""
        
        # Use LLM for indication-specific assessments if available
        if self.use_llm and self.llm_service:
            try:
                # Build context from similar protocols
                rag_assessment_examples = ""
                if similar_protocols:
                    rag_assessment_examples = "\n\nCommon Assessments in Similar Protocols:\n"
                    for i, protocol in enumerate(similar_protocols[:2], 1):
                        if 'protocol' in protocol and 'assessments' in protocol['protocol']:
                            assessments_list = protocol['protocol']['assessments']
                            assessment_names = [a.get('name', 'N/A') for a in assessments_list[:4]]
                            rag_assessment_examples += f"{i}. {', '.join(assessment_names)}\n"
                
                # Add user instructions if provided
                user_instructions = ""
                if spec.additional_instructions:
                    user_instructions = f"\n\n## ADDITIONAL USER INSTRUCTIONS:\n{spec.additional_instructions}\n"
                
                prompt = f"""You are an expert clinical trial protocol writer specializing in {spec.indication}. Generate appropriate clinical assessments.

Trial Specification:
- Phase: {spec.phase.value}
- Indication: {spec.indication}
- Duration: {spec.duration_weeks} weeks
{rag_assessment_examples}{user_instructions}

Generate assessments appropriate for {spec.indication} trials. Include:
1. Standard assessments (Demographics, Vital Signs, Adverse Events, Labs)
2. Indication-specific assessments (e.g., for cancer: tumor imaging, RECIST; for dermatology: lesion counts, photography; for diabetes: HbA1c, glucose)

Return ONLY a JSON array of assessment objects.
Each assessment should have: assessment_id, name, description, timing.

Example format:
[
  {{"assessment_id": "DEMO", "name": "Demographics", "description": "Participant demographics", "timing": ["Screening"]}},
  {{"assessment_id": "TUMOR", "name": "Tumor Assessment", "description": "CT/MRI per RECIST 1.1", "timing": ["Baseline", "Week 8", "Week 16"]}}
]

CRITICAL: Make assessments SPECIFIC to {spec.indication}. 
Return ONLY the JSON array, no other text."""

                response = self.llm_service.client.chat.completions.create(
                    model=self.llm_service.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=1000,
                )
                
                llm_response = response.choices[0].message.content.strip()
                
                # Try to parse JSON from response
                import json
                import re
                
                # Extract JSON array from response
                json_match = re.search(r'\[.*\]', llm_response, re.DOTALL)
                if json_match:
                    assessments = json.loads(json_match.group())
                    print(f"✓ Generated {len(assessments)} indication-specific assessments using LLM")
                    return assessments
                else:
                    print("⚠ Could not parse LLM assessments. Using template.")
                    
            except Exception as e:
                print(f"⚠ LLM assessment generation failed: {e}. Using template.")
        
        # Fallback: Generic assessments
        assessments = [
            {
                "assessment_id": "DEMO",
                "name": "Demographics",
                "description": "Participant demographics and baseline characteristics",
                "timing": ["Screening"],
            },
            {
                "assessment_id": "VITAL",
                "name": "Vital Signs",
                "description": "Blood pressure, heart rate, temperature, respiratory rate",
                "timing": ["All visits"],
            },
            {
                "assessment_id": "AE",
                "name": "Adverse Events",
                "description": "Assessment of adverse events",
                "timing": ["All visits"],
            },
            {
                "assessment_id": "LAB",
                "name": "Laboratory Tests",
                "description": "Hematology, chemistry, urinalysis",
                "timing": ["Screening", "Week 4", "Week 12", "End of Study"],
            },
        ]
        
        # Add endpoint-specific assessments
        for endpoint in spec.key_endpoints:
            if "score" in endpoint.name.lower():
                assessments.append({
                    "assessment_id": f"SCORE_{len(assessments)}",
                    "name": "Clinical Score Assessment",
                    "description": endpoint.name,
                    "timing": ["Baseline", "All follow-up visits"],
                })
        
        return assessments
    
    def _generate_protocol_sections(
        self,
        spec: TrialSpecInput,
        objectives: Dict[str, Any],
        similar_protocols: List[Dict[str, Any]]
    ) -> List[ProtocolSection]:
        """Generate structured protocol sections with enhanced content."""
        sections = []
        
        # Synopsis - Use LLM enhancement if available
        synopsis_content = self.templates["synopsis"].format(
            title=spec.title,
            sponsor=spec.sponsor,
            phase=spec.phase.value,
            indication=spec.indication,
            design=spec.design,
            sample_size=spec.sample_size,
            duration_weeks=spec.duration_weeks,
        )
        
        sections.append(ProtocolSection(
            section_id="1.0",
            title="Synopsis",
            content=synopsis_content,
            confidence_score=1.0,
            provenance="template_with_user_input",
        ))
        
        # Study Objectives - Use LLM-generated objectives
        objectives_content = f"""Primary Objective:
{objectives.get('primary', 'Not specified')}

Secondary Objectives:
{objectives.get('secondary', 'Not specified')}"""
        
        sections.append(ProtocolSection(
            section_id="2.0",
            title="Study Objectives",
            content=objectives_content,
            confidence_score=0.95,
            provenance="llm_generated" if self.use_llm and self.llm_service else "template",
        ))
        
        return sections
    
    def _generate_rag_context(self, similar_protocols: List[Dict[str, Any]]) -> str:
        """Generate context summary from similar protocols."""
        if not similar_protocols:
            return ""
        
        context_parts = ["REFERENCE CONTEXT FROM SIMILAR PROTOCOLS:\n"]
        
        for i, protocol in enumerate(similar_protocols[:2], 1):
            metadata = protocol.get('metadata', {})
            score = protocol.get('similarity_score', 0)
            
            context_parts.append(
                f"\nSimilar Protocol {i} (Similarity: {score:.1%}):\n"
                f"- Phase: {metadata.get('phase', 'N/A')}\n"
                f"- Indication: {metadata.get('indication', 'N/A')}\n"
                f"- Design: {metadata.get('design', 'N/A')}\n"
                f"- Sample Size: {metadata.get('sample_size', 'N/A')}\n"
                f"- Duration: {metadata.get('duration_weeks', 'N/A')} weeks"
            )
        
        context_parts.append("\n" + "="*60 + "\n")
        
        return "\n".join(context_parts)


class CRFGenerator:
    """Generates CRF schemas based on protocol."""
    
    def __init__(self):
        """Initialize CRF generator with optional LLM support."""
        from app.services.llm_service import LLMService
        from config import settings
        
        self.llm_service = None
        if settings.openai_api_key:
            try:
                self.llm_service = LLMService()
                print("✓ LLM enabled for CRF generation")
            except Exception as e:
                print(f"⚠ LLM initialization failed: {e}. CRF will use templates only.")
    
    def generate_crf_schema(self, spec: TrialSpecInput, protocol: ProtocolStructured) -> CRFSchema:
        """Generate complete CRF schema based on protocol assessments."""
        # Generate forms based on protocol assessments (indication-specific)
        forms = self._generate_forms_from_assessments(spec, protocol)
        visits = self._generate_visit_definitions(protocol.visit_schedule)
        
        return CRFSchema(
            study_id=protocol.protocol_id,
            version="1.0",
            generated_at=datetime.now(),
            forms=forms,
            visits=visits,
            cdash_compliance=True,
            sdtm_mappings={
                "SUBJID": "usubjid",
                "VISITNUM": "visitnum",
                "VISIT": "visit",
            },
        )
    
    def _generate_forms_from_assessments(
        self,
        spec: TrialSpecInput,
        protocol: ProtocolStructured
    ) -> List[CRFForm]:
        """Generate CRF forms based on protocol assessments."""
        forms = []
        
        # Always include standard forms first
        forms.extend(self._generate_standard_forms(spec))
        
        # Generate indication-specific forms based on assessments
        for assessment in protocol.assessments:
            assessment_id = assessment.get('assessment_id', '')
            assessment_name = assessment.get('name', '')
            
            # Skip if already in standard forms
            if assessment_id in ['DEMO', 'VITAL', 'AE', 'LAB']:
                continue
            
            # Generate form for this assessment
            form = self._generate_assessment_form(spec, assessment)
            if form:
                forms.append(form)
        
        return forms
    
    def _generate_assessment_form(
        self,
        spec: TrialSpecInput,
        assessment: Dict[str, Any]
    ) -> Optional[CRFForm]:
        """Generate a CRF form for a specific assessment using LLM."""
        
        assessment_id = assessment.get('assessment_id', 'CUSTOM')
        assessment_name = assessment.get('name', 'Custom Assessment')
        assessment_desc = assessment.get('description', '')
        
        # Use LLM to generate indication-specific fields
        if self.llm_service:
            try:
                # Add user instructions if provided
                user_instructions = ""
                if spec.additional_instructions:
                    user_instructions = f"\n\n## ADDITIONAL USER INSTRUCTIONS:\n{spec.additional_instructions}\n"
                
                prompt = f"""You are an expert in clinical trial data collection and CRF design for {spec.indication}.

Generate CRF fields for the following assessment:
- Assessment: {assessment_name}
- Description: {assessment_desc}
- Indication: {spec.indication}
{user_instructions}
Create fields appropriate for {spec.indication} that would be used to capture this assessment data.
For example:
- Cancer tumor assessment: Lesion IDs, target/non-target, measurements, RECIST response
- Acne lesion count: Inflammatory count, non-inflammatory count, location, severity
- Lab tests: Test name, result value, units, normal ranges

Return ONLY a JSON array of field objects.
Each field should have: field_id, field_name, field_label, data_type (text/number/date/dropdown/checkbox), required (true/false).

Example format:
[
  {{"field_id": "TUMOR_ID", "field_name": "lesion_id", "field_label": "Target Lesion ID", "data_type": "text", "required": true}},
  {{"field_id": "TUMOR_SIZE", "field_name": "lesion_size", "field_label": "Lesion Size (mm)", "data_type": "number", "required": true}}
]

Generate 3-6 relevant fields for {assessment_name} in {spec.indication}.
Return ONLY the JSON array, no other text."""

                response = self.llm_service.client.chat.completions.create(
                    model=self.llm_service.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=1000,
                )
                
                llm_response = response.choices[0].message.content.strip()
                
                # Parse JSON
                import json
                import re
                
                json_match = re.search(r'\[.*\]', llm_response, re.DOTALL)
                if json_match:
                    field_dicts = json.loads(json_match.group())
                    
                    # Convert to CRFField objects
                    fields = []
                    for fd in field_dicts:
                        fields.append(CRFField(
                            field_id=fd.get('field_id', f'FIELD_{len(fields)}'),
                            field_name=fd.get('field_name', 'field'),
                            field_label=fd.get('field_label', 'Field'),
                            data_type=fd.get('data_type', 'text'),
                            required=fd.get('required', False),
                        ))
                    
                    print(f"✓ Generated {len(fields)} CRF fields for {assessment_name} using LLM")
                    
                    return CRFForm(
                        form_id=assessment_id,
                        form_name=assessment_name,
                        form_description=assessment_desc,
                        fields=fields,
                        repeating=True,  # Most assessments can repeat
                    )
                
            except Exception as e:
                print(f"⚠ LLM CRF field generation failed for {assessment_name}: {e}")
        
        # Fallback: Create generic form
        return None
        
        return CRFSchema(
            study_id=protocol.protocol_id,
            version="1.0",
            generated_at=datetime.now(),
            forms=forms,
            visits=visits,
            cdash_compliance=True,
            sdtm_mappings={
                "SUBJID": "usubjid",
                "VISITNUM": "visitnum",
                "VISIT": "visit",
            },
        )
    
    def _generate_standard_forms(self, spec: TrialSpecInput) -> List[CRFForm]:
        """Generate standard CRF forms."""
        forms = []
        
        # Demographics Form
        demo_fields = [
            CRFField(
                field_id="SUBJID",
                field_name="subject_id",
                field_label="Subject ID",
                data_type="text",
                required=True,
                cdash_variable="SUBJID",
                sdtm_variable="USUBJID",
            ),
            CRFField(
                field_id="AGE",
                field_name="age",
                field_label="Age (years)",
                data_type="number",
                required=True,
                validation_rules={"min": 0, "max": 120},
                cdash_variable="AGE",
                sdtm_variable="AGE",
            ),
            CRFField(
                field_id="SEX",
                field_name="sex",
                field_label="Sex",
                data_type="radio",
                required=True,
                validation_rules={"options": ["Male", "Female", "Other"]},
                cdash_variable="SEX",
                sdtm_variable="SEX",
            ),
            CRFField(
                field_id="RACE",
                field_name="race",
                field_label="Race",
                data_type="dropdown",
                required=True,
                controlled_vocabulary="CDASH_RACE",
                cdash_variable="RACE",
                sdtm_variable="RACE",
            ),
        ]
        
        forms.append(CRFForm(
            form_id="DM",
            form_name="Demographics",
            form_description="Subject demographics and baseline characteristics",
            fields=demo_fields,
            repeating=False,
        ))
        
        # Vital Signs Form
        vital_fields = [
            CRFField(
                field_id="VS_DATE",
                field_name="assessment_date",
                field_label="Assessment Date",
                data_type="date",
                required=True,
                cdash_variable="VSDTC",
            ),
            CRFField(
                field_id="SYSBP",
                field_name="systolic_bp",
                field_label="Systolic Blood Pressure (mmHg)",
                data_type="number",
                required=True,
                validation_rules={"min": 50, "max": 250},
                cdash_variable="VSORRES",
                sdtm_variable="VSSTRESN",
            ),
            CRFField(
                field_id="DIABP",
                field_name="diastolic_bp",
                field_label="Diastolic Blood Pressure (mmHg)",
                data_type="number",
                required=True,
                validation_rules={"min": 30, "max": 150},
                cdash_variable="VSORRES",
                sdtm_variable="VSSTRESN",
            ),
            CRFField(
                field_id="HR",
                field_name="heart_rate",
                field_label="Heart Rate (bpm)",
                data_type="number",
                required=True,
                validation_rules={"min": 30, "max": 200},
                cdash_variable="VSORRES",
                sdtm_variable="VSSTRESN",
            ),
            CRFField(
                field_id="TEMP",
                field_name="temperature",
                field_label="Temperature (°C)",
                data_type="number",
                required=True,
                validation_rules={"min": 35.0, "max": 42.0},
                cdash_variable="VSORRES",
                sdtm_variable="VSSTRESN",
            ),
        ]
        
        forms.append(CRFForm(
            form_id="VS",
            form_name="Vital Signs",
            form_description="Vital signs assessment",
            fields=vital_fields,
            repeating=False,
        ))
        
        # Adverse Events Form
        ae_fields = [
            CRFField(
                field_id="AE_TERM",
                field_name="ae_term",
                field_label="Adverse Event Term",
                data_type="text",
                required=True,
                cdash_variable="AETERM",
                sdtm_variable="AETERM",
            ),
            CRFField(
                field_id="AE_START",
                field_name="ae_start_date",
                field_label="Start Date",
                data_type="date",
                required=True,
                cdash_variable="AESTDTC",
            ),
            CRFField(
                field_id="AE_SEV",
                field_name="severity",
                field_label="Severity",
                data_type="dropdown",
                required=True,
                validation_rules={"options": ["Mild", "Moderate", "Severe"]},
                cdash_variable="AESEV",
                sdtm_variable="AESEV",
            ),
            CRFField(
                field_id="AE_REL",
                field_name="relationship",
                field_label="Relationship to Study Drug",
                data_type="dropdown",
                required=True,
                validation_rules={"options": ["Not Related", "Unlikely", "Possible", "Probable", "Definite"]},
                cdash_variable="AEREL",
                sdtm_variable="AEREL",
            ),
        ]
        
        forms.append(CRFForm(
            form_id="AE",
            form_name="Adverse Events",
            form_description="Adverse event reporting",
            fields=ae_fields,
            repeating=True,
        ))
        
        # Efficacy Assessment (if endpoints mention scores)
        has_score_endpoint = any("score" in ep.name.lower() for ep in spec.key_endpoints)
        if has_score_endpoint:
            score_fields = [
                CRFField(
                    field_id="SCORE_DATE",
                    field_name="assessment_date",
                    field_label="Assessment Date",
                    data_type="date",
                    required=True,
                ),
                CRFField(
                    field_id="TOTAL_SCORE",
                    field_name="total_score",
                    field_label="Total Score",
                    data_type="number",
                    required=True,
                    validation_rules={"min": 0, "max": 100},
                ),
            ]
            
            forms.append(CRFForm(
                form_id="EFF",
                form_name="Efficacy Assessment",
                form_description="Clinical efficacy score assessment",
                fields=score_fields,
                repeating=False,
            ))
        
        return forms
    
    def _generate_visit_definitions(self, visit_schedule: List[Dict[str, Any]]) -> List[VisitDefinition]:
        """Generate visit definitions with form assignments."""
        visits = []
        
        for i, visit in enumerate(visit_schedule, 1):
            # Standard forms for all visits
            forms = ["VS", "AE"]
            
            # Demographics only at screening
            if visit["visit_id"] == "V0":
                forms.insert(0, "DM")
            
            # Efficacy at baseline and follow-ups
            if visit["visit_id"] != "V0":
                forms.append("EFF")
            
            visits.append(VisitDefinition(
                visit_id=visit["visit_id"],
                visit_name=visit["visit_name"],
                visit_number=i,
                timepoint=f"Week {visit['week']}" if visit['week'] >= 0 else "Screening",
                window=visit.get("window"),
                forms=forms,
            ))
        
        return visits
