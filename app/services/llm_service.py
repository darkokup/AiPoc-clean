"""LLM service for AI-enhanced protocol generation using OpenAI."""
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config import settings


class LLMService:
    """Service for interacting with OpenAI's LLM."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        if not settings.openai_api_key:
            raise ValueError(
                "OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
            )
        
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o"  # or "gpt-3.5-turbo" for faster/cheaper
        
    def enhance_protocol_section(
        self,
        section_type: str,
        template_content: str,
        trial_spec: Dict[str, Any],
        rag_context: Optional[List[Dict]] = None,
    ) -> str:
        """
        Use LLM to enhance a protocol section with RAG context.
        
        Args:
            section_type: Type of section (synopsis, objectives, etc.)
            template_content: Base template content
            trial_spec: Trial specification details
            rag_context: Similar protocols from RAG for context
            
        Returns:
            Enhanced section content
        """
        # Build context from similar protocols
        rag_examples = ""
        if rag_context:
            rag_examples = "\n\n## Similar Protocol Examples:\n"
            for i, protocol in enumerate(rag_context[:2], 1):
                rag_examples += f"\n### Example {i}:\n"
                rag_examples += f"Title: {protocol.get('title', 'N/A')}\n"
                if 'protocol' in protocol:
                    rag_examples += f"Content: {str(protocol['protocol'])[:500]}...\n"
        
        # Create prompt
        prompt = f"""You are an expert clinical trial protocol writer. Generate a professional {section_type} section for a clinical trial protocol.

## Trial Specification:
- Title: {trial_spec.get('title')}
- Phase: {trial_spec.get('phase')}
- Indication: {trial_spec.get('indication')}
- Design: {trial_spec.get('design')}
- Sample Size: {trial_spec.get('sample_size')}
- Duration: {trial_spec.get('duration_weeks')} weeks

## Template Content:
{template_content}

{rag_examples}

## Instructions:
1. Use the template as a base structure
2. Incorporate insights from similar protocols if provided
3. Ensure content is scientifically accurate and follows ICH-GCP guidelines
4. Use professional clinical trial language
5. Be specific and detailed where appropriate
6. Include all required regulatory elements for a {section_type} section

Generate the enhanced {section_type} section:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert clinical trial protocol writer with deep knowledge of ICH-GCP guidelines, CDISC standards, and regulatory requirements.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"⚠ LLM generation failed: {e}. Falling back to template.")
            return template_content
    
    def generate_objectives(
        self,
        trial_spec: Dict[str, Any],
        rag_context: Optional[List[Dict]] = None,
        additional_instructions: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Generate primary and secondary objectives using LLM.
        
        Args:
            trial_spec: Trial specification details
            rag_context: Similar protocols for context
            
        Returns:
            Dictionary with 'primary' and 'secondary' objectives
        """
        # Build RAG context
        rag_objectives = ""
        if rag_context:
            rag_objectives = "\n\n## Example Objectives from Similar Protocols:\n"
            for i, protocol in enumerate(rag_context[:2], 1):
                if 'protocol' in protocol and 'objectives' in protocol['protocol']:
                    obj = protocol['protocol']['objectives']
                    rag_objectives += f"\n### Example {i}:\n"
                    rag_objectives += f"Primary: {obj.get('primary', 'N/A')}\n"
                    rag_objectives += f"Secondary: {obj.get('secondary', 'N/A')}\n"
        
        # Add user instructions if provided
        user_instructions = ""
        if additional_instructions:
            user_instructions = f"\n\n## ADDITIONAL USER INSTRUCTIONS:\n{additional_instructions}\n"
        
        prompt = f"""Generate primary and secondary objectives for a clinical trial.

## Trial Details:
- Title: {trial_spec.get('title')}
- Phase: {trial_spec.get('phase')}
- Indication: {trial_spec.get('indication')}
- Design: {trial_spec.get('design')}

{rag_objectives}{user_instructions}

## Instructions:
1. Primary objective should be clear, measurable, and align with the study design
2. Include 2-3 secondary objectives covering safety, tolerability, and additional efficacy endpoints
3. Use standard clinical trial objective language
4. Be specific about endpoints where possible

Return ONLY a JSON object with this exact format:
{{
    "primary": "Primary objective text here",
    "secondary": "Secondary objectives text here (can be multiple objectives in one string)"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a clinical trial expert. Return only valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=500,
                response_format={"type": "json_object"},
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"⚠ LLM objective generation failed: {e}. Using defaults.")
            return {
                "primary": f"To evaluate the efficacy of the study intervention in patients with {trial_spec.get('indication')}.",
                "secondary": "To assess the safety and tolerability of the study intervention.",
            }
    
    def generate_inclusion_criteria(
        self,
        trial_spec: Dict[str, Any],
        rag_context: Optional[List[Dict]] = None,
        additional_instructions: Optional[str] = None,
    ) -> List[str]:
        """
        Generate inclusion criteria using LLM.
        
        Args:
            trial_spec: Trial specification details
            rag_context: Similar protocols for context
            
        Returns:
            List of inclusion criteria
        """
        rag_criteria = ""
        if rag_context:
            rag_criteria = "\n\n## Example Criteria from Similar Protocols:\n"
            for i, protocol in enumerate(rag_context[:2], 1):
                if 'protocol' in protocol and 'eligibility' in protocol['protocol']:
                    eligibility = protocol['protocol']['eligibility']
                    if 'inclusion_criteria' in eligibility:
                        rag_criteria += f"\n### Example {i}:\n"
                        for criterion in eligibility['inclusion_criteria'][:3]:
                            rag_criteria += f"- {criterion}\n"
        
        # Add user instructions if provided
        user_instructions = ""
        if additional_instructions:
            user_instructions = f"\n\n## ADDITIONAL USER INSTRUCTIONS:\n{additional_instructions}\n"
        
        prompt = f"""Generate comprehensive inclusion criteria for a clinical trial.

## Trial Details:
- Phase: {trial_spec.get('phase')}
- Indication: {trial_spec.get('indication')}
- Design: {trial_spec.get('design')}

{rag_criteria}{user_instructions}

## Instructions:
Generate 6-10 inclusion criteria that are:
1. Specific and measurable
2. Appropriate for the indication and phase
3. Follow standard clinical trial criteria format
4. Include age, diagnosis, consent, and relevant clinical parameters

Return ONLY a JSON array of strings:
["Criterion 1", "Criterion 2", ...]"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a clinical trial expert. Return only valid JSON array.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=800,
                response_format={"type": "json_object"},
            )
            
            import json
            # OpenAI returns {"criteria": [...]} or similar, extract the array
            result = json.loads(response.choices[0].message.content)
            
            # Handle different possible response formats
            if isinstance(result, list):
                return result
            elif 'criteria' in result:
                return result['criteria']
            elif 'inclusion_criteria' in result:
                return result['inclusion_criteria']
            else:
                # Return first list found in the response
                for value in result.values():
                    if isinstance(value, list):
                        return value
            
            raise ValueError("No list found in LLM response")
            
        except Exception as e:
            print(f"⚠ LLM criteria generation failed: {e}. Using defaults.")
            return [
                f"Age ≥18 years",
                f"Confirmed diagnosis of {trial_spec.get('indication')}",
                "Able to provide informed consent",
                "Adequate organ function",
            ]
    
    def generate_exclusion_criteria(
        self,
        trial_spec: Dict[str, Any],
        rag_context: Optional[List[Dict]] = None,
        additional_instructions: Optional[str] = None,
    ) -> List[str]:
        """Generate exclusion criteria using LLM."""
        # Add user instructions if provided
        user_instructions = ""
        if additional_instructions:
            user_instructions = f"\n\n## ADDITIONAL USER INSTRUCTIONS:\n{additional_instructions}\n"
        
        # Similar to inclusion criteria but for exclusions
        prompt = f"""Generate exclusion criteria for a clinical trial.

## Trial Details:
- Phase: {trial_spec.get('phase')}
- Indication: {trial_spec.get('indication')}

{user_instructions}
Generate 4-8 exclusion criteria covering contraindications, safety concerns, and confounding factors.

Return ONLY a JSON array of strings:
["Criterion 1", "Criterion 2", ...]"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a clinical trial expert. Return only valid JSON array.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=600,
                response_format={"type": "json_object"},
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            # Extract array from response
            if isinstance(result, list):
                return result
            for key in ['criteria', 'exclusion_criteria', 'exclusions']:
                if key in result and isinstance(result[key], list):
                    return result[key]
            for value in result.values():
                if isinstance(value, list):
                    return value
            
            raise ValueError("No list found in LLM response")
            
        except Exception as e:
            print(f"⚠ LLM exclusion generation failed: {e}. Using defaults.")
            return [
                "Pregnancy or lactation",
                "Known hypersensitivity to study drug",
                "Participation in another clinical trial within 30 days",
            ]


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create the LLM service singleton."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def is_llm_available() -> bool:
    """Check if LLM service is available."""
    try:
        get_llm_service()
        return True
    except ValueError:
        return False
