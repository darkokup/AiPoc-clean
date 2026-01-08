"""Clinical rules validation engine."""
from typing import List, Dict, Any
from app.models.schemas import (
    TrialSpecInput,
    ProtocolStructured,
    CRFSchema,
    ValidationResult,
)


class ClinicalRulesValidator:
    """Validates protocols against clinical trial rules and best practices."""
    
    def __init__(self):
        """Initialize validator with rule definitions."""
        self.rules = self._define_rules()
    
    def _define_rules(self) -> Dict[str, Any]:
        """Define validation rules."""
        return {
            "sample_size_minimum": {
                "description": "Minimum sample size for phase",
                "phase_minimums": {
                    "Phase 1": 20,
                    "Phase 2": 40,
                    "Phase 3": 100,
                    "Phase 4": 100,
                },
            },
            "duration_minimum": {
                "description": "Minimum study duration in weeks",
                "minimum_weeks": 4,
            },
            "endpoint_requirements": {
                "description": "Endpoint requirements",
                "requires_primary": True,
                "max_primary": 3,
            },
            "eligibility_criteria": {
                "description": "Eligibility criteria requirements",
                "min_inclusion": 2,
                "min_exclusion": 1,
            },
        }
    
    def validate_trial_spec(self, spec: TrialSpecInput) -> ValidationResult:
        """Validate trial specification input."""
        errors = []
        warnings = []
        info = []
        rules_checked = []
        
        # Rule: Sample size check
        rules_checked.append("sample_size_minimum")
        min_sample = self.rules["sample_size_minimum"]["phase_minimums"].get(spec.phase.value, 20)
        if spec.sample_size < min_sample:
            warnings.append(
                f"Sample size ({spec.sample_size}) is below recommended minimum "
                f"for {spec.phase.value} ({min_sample})"
            )
        
        # Rule: Duration check
        rules_checked.append("duration_minimum")
        min_duration = self.rules["duration_minimum"]["minimum_weeks"]
        if spec.duration_weeks < min_duration:
            warnings.append(
                f"Study duration ({spec.duration_weeks} weeks) is below minimum "
                f"recommended duration ({min_duration} weeks)"
            )
        
        # Rule: Endpoint requirements
        rules_checked.append("endpoint_requirements")
        primary_endpoints = [ep for ep in spec.key_endpoints if ep.type.value == "primary"]
        
        if not primary_endpoints:
            errors.append("At least one primary endpoint is required")
        elif len(primary_endpoints) > self.rules["endpoint_requirements"]["max_primary"]:
            warnings.append(
                f"Number of primary endpoints ({len(primary_endpoints)}) exceeds "
                f"recommended maximum (3). Consider secondary endpoints for some."
            )
        
        # Rule: Eligibility criteria
        rules_checked.append("eligibility_criteria")
        min_inclusion = self.rules["eligibility_criteria"]["min_inclusion"]
        min_exclusion = self.rules["eligibility_criteria"]["min_exclusion"]
        
        if len(spec.inclusion_criteria) < min_inclusion:
            warnings.append(
                f"Only {len(spec.inclusion_criteria)} inclusion criteria provided. "
                f"Consider adding more detailed criteria."
            )
        
        if len(spec.exclusion_criteria) < min_exclusion:
            warnings.append(
                f"Only {len(spec.exclusion_criteria)} exclusion criteria provided. "
                f"Consider adding more detailed criteria."
            )
        
        # Age range validation
        if spec.age_range:
            if not self._validate_age_range(spec.age_range):
                errors.append(f"Invalid age range format: {spec.age_range}. Expected format: '18-65'")
        
        # Treatment arms check
        if spec.treatment_arms and len(spec.treatment_arms) < 2:
            warnings.append("Only one treatment arm specified. Consider adding a control/comparator arm.")
        
        # Info messages
        info.append(f"Protocol validated for {spec.phase.value} study")
        info.append(f"Target enrollment: {spec.sample_size} participants")
        
        valid = len(errors) == 0
        
        return ValidationResult(
            valid=valid,
            errors=errors,
            warnings=warnings,
            info=info,
            rules_checked=rules_checked,
        )
    
    def validate_protocol(self, protocol: ProtocolStructured) -> ValidationResult:
        """Validate structured protocol."""
        errors = []
        warnings = []
        info = []
        rules_checked = []
        
        # Check required sections
        rules_checked.append("required_sections")
        required_section_ids = ["1.0", "2.0"]  # Synopsis, Objectives
        existing_ids = {s.section_id for s in protocol.sections}
        
        missing = set(required_section_ids) - existing_ids
        if missing:
            warnings.append(f"Missing recommended sections: {missing}")
        
        # Validate visit schedule
        rules_checked.append("visit_schedule")
        if len(protocol.visit_schedule) < 2:
            errors.append("Visit schedule must have at least 2 visits (baseline and follow-up)")
        
        # Check for baseline visit
        has_baseline = any(v.get("week") == 0 for v in protocol.visit_schedule)
        if not has_baseline:
            errors.append("Visit schedule must include a baseline visit (Week 0)")
        
        # Statistical plan validation
        rules_checked.append("statistical_plan")
        if protocol.statistical_plan.get("power", 0) < 0.80:
            warnings.append("Statistical power below 80% may lead to inconclusive results")
        
        # Safety monitoring
        rules_checked.append("safety_monitoring")
        if not protocol.safety_monitoring.get("dsmb"):
            warnings.append("Consider establishing a Data Safety Monitoring Board (DSMB)")
        
        info.append(f"Protocol {protocol.protocol_id} validated")
        info.append(f"{len(protocol.sections)} sections generated")
        
        valid = len(errors) == 0
        
        return ValidationResult(
            valid=valid,
            errors=errors,
            warnings=warnings,
            info=info,
            rules_checked=rules_checked,
        )
    
    def validate_crf_schema(self, crf_schema: CRFSchema) -> ValidationResult:
        """Validate CRF schema."""
        errors = []
        warnings = []
        info = []
        rules_checked = []
        
        # Check required forms
        rules_checked.append("required_forms")
        required_forms = {"DM", "AE"}  # Demographics and Adverse Events
        existing_forms = {f.form_id for f in crf_schema.forms}
        
        missing = required_forms - existing_forms
        if missing:
            errors.append(f"Missing required forms: {missing}")
        
        # Validate CDASH compliance
        rules_checked.append("cdash_compliance")
        if crf_schema.cdash_compliance:
            for form in crf_schema.forms:
                for field in form.fields:
                    if not field.cdash_variable:
                        warnings.append(
                            f"Field {field.field_id} in form {form.form_id} "
                            f"missing CDASH variable mapping"
                        )
        
        # Check visit assignments
        rules_checked.append("visit_form_assignments")
        for visit in crf_schema.visits:
            if not visit.forms:
                errors.append(f"Visit {visit.visit_id} has no forms assigned")
        
        # Validate field data types
        rules_checked.append("field_validations")
        for form in crf_schema.forms:
            for field in form.fields:
                if field.data_type == "number" and not field.validation_rules:
                    warnings.append(
                        f"Numeric field {field.field_id} in {form.form_id} "
                        f"should have validation rules (min/max)"
                    )
        
        info.append(f"CRF schema validated for study {crf_schema.study_id}")
        info.append(f"{len(crf_schema.forms)} forms, {len(crf_schema.visits)} visits")
        
        valid = len(errors) == 0
        
        return ValidationResult(
            valid=valid,
            errors=errors,
            warnings=warnings,
            info=info,
            rules_checked=rules_checked,
        )
    
    def _validate_age_range(self, age_range: str) -> bool:
        """Validate age range format (e.g., '18-65')."""
        try:
            if "-" not in age_range:
                return False
            parts = age_range.split("-")
            if len(parts) != 2:
                return False
            min_age = int(parts[0].strip())
            max_age = int(parts[1].strip())
            return 0 <= min_age < max_age <= 120
        except:
            return False
