"""
Import real clinical trial protocols from ClinicalTrials.gov API.

This script fetches real trial data from ClinicalTrials.gov and converts it
into the format needed for our RAG database.

API Documentation: https://clinicaltrials.gov/data-api/api
"""
import sys
import os
import requests
import time
from typing import List, Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.rag_service import get_rag_service
from app.services.generator import ProtocolTemplateGenerator
from app.models.schemas import TrialSpecInput, TrialPhase, TrialEndpoint, EndpointType


class ClinicalTrialsImporter:
    """Import trials from ClinicalTrials.gov API."""
    
    BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ClinicalTrialProtocolGenerator/1.0'
        })
    
    def fetch_trials(
        self,
        max_trials: int = 500,
        phases: Optional[List[str]] = None,
        conditions: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch trials from ClinicalTrials.gov API.
        
        Args:
            max_trials: Maximum number of trials to fetch
            phases: List of phases to filter (e.g., ["PHASE2", "PHASE3"])
            conditions: List of conditions/diseases to filter
            
        Returns:
            List of trial data dictionaries
        """
        print(f"\n📡 Fetching trials from ClinicalTrials.gov...")
        print(f"   Target: {max_trials} trials")
        
        # Build query parameters
        params = {
            'format': 'json',
            'pageSize': 100,  # API max per request
            'countTotal': 'true',
            'fields': 'NCTId,BriefTitle,OfficialTitle,Phase,Condition,PrimaryOutcomeMeasure,'
                     'SecondaryOutcomeMeasure,EnrollmentCount,StudyType,DesignAllocation,'
                     'DesignInterventionModel,EligibilityCriteria,MinimumAge,MaximumAge,'
                     'Gender,LeadSponsorName,StudyFirstPostDate,OverallStatus'
        }
        
        # Add filters
        query_parts = []
        
        if phases:
            phase_query = " OR ".join(phases)
            query_parts.append(f"AREA[Phase]({phase_query})")
        else:
            # Default to Phase 2 and 3 for quality data
            query_parts.append("AREA[Phase](PHASE2 OR PHASE3)")
        
        # Filter for interventional studies only
        query_parts.append("AREA[StudyType]Interventional")
        
        # Filter for completed or active studies (better data quality)
        query_parts.append("AREA[OverallStatus](COMPLETED OR ACTIVE_NOT_RECRUITING OR RECRUITING)")
        
        if conditions:
            condition_query = " OR ".join(conditions)
            query_parts.append(f"AREA[Condition]({condition_query})")
        
        params['query.term'] = " AND ".join(query_parts)
        
        trials = []
        page_token = None
        
        try:
            while len(trials) < max_trials:
                # Add pagination token if we have one
                if page_token:
                    params['pageToken'] = page_token
                
                print(f"\r   Fetching: {len(trials)}/{max_trials} trials...", end='', flush=True)
                
                response = self.session.get(self.BASE_URL, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                if 'studies' not in data:
                    print(f"\n   ⚠ No studies found in response")
                    break
                
                studies = data['studies']
                trials.extend(studies)
                
                # Check if there are more pages
                next_page_token = data.get('nextPageToken')
                if not next_page_token or len(trials) >= max_trials:
                    break
                
                page_token = next_page_token
                
                # Be nice to the API
                time.sleep(0.5)
            
            print(f"\r   ✅ Fetched {len(trials)} trials successfully")
            
        except requests.exceptions.RequestException as e:
            print(f"\n   ❌ Error fetching trials: {e}")
            return trials[:max_trials] if trials else []
        
        return trials[:max_trials]
    
    def convert_to_trial_spec(self, trial_data: Dict[str, Any]) -> Optional[TrialSpecInput]:
        """
        Convert ClinicalTrials.gov data to TrialSpecInput format.
        
        Args:
            trial_data: Raw trial data from API
            
        Returns:
            TrialSpecInput object or None if conversion fails
        """
        try:
            protocol = trial_data.get('protocolSection', {})
            
            # Extract identification info
            id_module = protocol.get('identificationModule', {})
            nct_id = id_module.get('nctId', 'UNKNOWN')
            brief_title = id_module.get('briefTitle', 'Unknown Study')
            official_title = id_module.get('officialTitle', brief_title)
            
            # Extract sponsor
            sponsor_module = protocol.get('sponsorCollaboratorsModule', {})
            lead_sponsor = sponsor_module.get('leadSponsor', {})
            sponsor_name = lead_sponsor.get('name', 'Unknown Sponsor')
            
            # Extract phase
            design_module = protocol.get('designModule', {})
            phases = design_module.get('phases', [])
            
            # Map phase strings to our enum
            phase_mapping = {
                'PHASE1': TrialPhase.PHASE_1,
                'PHASE2': TrialPhase.PHASE_2,
                'PHASE3': TrialPhase.PHASE_3,
                'PHASE4': TrialPhase.PHASE_4,
                'PHASE1_PHASE2': TrialPhase.PHASE_2,
                'PHASE2_PHASE3': TrialPhase.PHASE_3,
            }
            
            trial_phase = TrialPhase.PHASE_2  # default
            if phases:
                phase_str = phases[0] if isinstance(phases, list) else phases
                trial_phase = phase_mapping.get(phase_str, TrialPhase.PHASE_2)
            
            # Extract conditions
            conditions_module = protocol.get('conditionsModule', {})
            conditions = conditions_module.get('conditions', [])
            indication = conditions[0] if conditions else "Unknown Condition"
            
            # Extract design
            study_type = design_module.get('studyType', 'Interventional')
            allocation = design_module.get('designInfo', {}).get('allocation', 'RANDOMIZED')
            intervention_model = design_module.get('designInfo', {}).get('interventionModel', 'PARALLEL')
            
            design = f"{allocation.lower().replace('_', ' ')} {intervention_model.lower().replace('_', ' ')} trial"
            
            # Extract enrollment
            status_module = protocol.get('statusModule', {})
            enrollment_info = status_module.get('enrollmentInfo', {})
            sample_size = enrollment_info.get('count', 100)
            if not sample_size or sample_size <= 0:
                sample_size = 100  # default
            
            # Estimate duration (not always available)
            duration_weeks = 52  # default to 1 year
            
            # Extract outcomes as endpoints
            outcomes_module = protocol.get('outcomesModule', {})
            
            endpoints = []
            
            # Primary outcomes
            primary_outcomes = outcomes_module.get('primaryOutcomes', [])
            for i, outcome in enumerate(primary_outcomes[:2], 1):  # Limit to 2
                measure = outcome.get('measure', f'Primary Outcome {i}')
                endpoints.append(TrialEndpoint(
                    type=EndpointType.PRIMARY,
                    name=measure[:100]  # Truncate if too long
                ))
            
            # Add at least one primary endpoint if none found
            if not endpoints:
                endpoints.append(TrialEndpoint(
                    type=EndpointType.PRIMARY,
                    name="Efficacy Outcome"
                ))
            
            # Secondary outcomes (limit to 2)
            secondary_outcomes = outcomes_module.get('secondaryOutcomes', [])
            for i, outcome in enumerate(secondary_outcomes[:2], 1):
                measure = outcome.get('measure', f'Secondary Outcome {i}')
                endpoints.append(TrialEndpoint(
                    type=EndpointType.SECONDARY,
                    name=measure[:100]
                ))
            
            # Extract eligibility criteria
            eligibility_module = protocol.get('eligibilityModule', {})
            
            # Parse inclusion/exclusion from criteria text
            criteria_text = eligibility_module.get('eligibilityCriteria', '')
            
            inclusion_criteria = []
            exclusion_criteria = []
            
            if criteria_text:
                # Simple parsing - split on common headers
                criteria_lower = criteria_text.lower()
                
                if 'inclusion criteria' in criteria_lower:
                    parts = criteria_text.split('Inclusion Criteria')
                    if len(parts) > 1:
                        inc_text = parts[1].split('Exclusion Criteria')[0] if 'Exclusion Criteria' in parts[1] else parts[1]
                        # Extract bullet points or numbered items
                        lines = [l.strip() for l in inc_text.split('\n') if l.strip() and len(l.strip()) > 10]
                        inclusion_criteria = [l.lstrip('-*•123456789. ') for l in lines[:5]]  # Limit to 5
                
                if 'exclusion criteria' in criteria_lower:
                    parts = criteria_text.split('Exclusion Criteria')
                    if len(parts) > 1:
                        exc_text = parts[1]
                        lines = [l.strip() for l in exc_text.split('\n') if l.strip() and len(l.strip()) > 10]
                        exclusion_criteria = [l.lstrip('-*•123456789. ') for l in lines[:5]]  # Limit to 5
            
            # Add basic criteria if none found
            if not inclusion_criteria:
                min_age = eligibility_module.get('minimumAge', '18 Years')
                max_age = eligibility_module.get('maximumAge', '75 Years')
                gender = eligibility_module.get('sex', 'ALL')
                
                inclusion_criteria = [
                    f"Age {min_age} to {max_age}",
                    f"Gender: {gender}",
                    f"Diagnosed with {indication}"
                ]
            
            if not exclusion_criteria:
                exclusion_criteria = [
                    "Pregnancy or breastfeeding",
                    "Serious medical conditions",
                    "Active infection"
                ]
            
            # Create TrialSpecInput
            trial_spec = TrialSpecInput(
                sponsor=sponsor_name,
                title=official_title,
                short_title=brief_title,
                indication=indication,
                phase=trial_phase,
                design=design,
                sample_size=sample_size,
                duration_weeks=duration_weeks,
                key_endpoints=endpoints,
                inclusion_criteria=inclusion_criteria,
                exclusion_criteria=exclusion_criteria,
                region="Global"  # Most trials don't specify, use Global
            )
            
            return trial_spec
            
        except Exception as e:
            print(f"\n   ⚠ Error converting trial: {e}")
            return None
    
    def import_to_rag(
        self,
        max_trials: int = 500,
        phases: Optional[List[str]] = None,
        conditions: Optional[List[str]] = None,
        batch_size: int = 50
    ) -> Dict[str, int]:
        """
        Import trials from ClinicalTrials.gov into RAG database.
        
        Args:
            max_trials: Maximum number of trials to import
            phases: List of phases to filter
            conditions: List of conditions to filter
            batch_size: Number of trials to process before reporting progress
            
        Returns:
            Dictionary with import statistics
        """
        print("\n" + "="*70)
        print("IMPORTING REAL CLINICAL TRIALS FROM CLINICALTRIALS.GOV")
        print("="*70)
        
        # Fetch trials
        trials = self.fetch_trials(max_trials, phases, conditions)
        
        if not trials:
            print("\n❌ No trials fetched. Aborting import.")
            return {'fetched': 0, 'converted': 0, 'added': 0, 'failed': 0}
        
        print(f"\n🔄 Converting and importing {len(trials)} trials...")
        print(f"   This may take several minutes...\n")
        
        # Initialize services
        rag_service = get_rag_service()
        generator = ProtocolTemplateGenerator(use_rag=False, use_llm=False)
        
        # Statistics
        stats = {
            'fetched': len(trials),
            'converted': 0,
            'added': 0,
            'failed': 0
        }
        
        # Process trials
        for i, trial_data in enumerate(trials, 1):
            try:
                # Convert to TrialSpecInput
                trial_spec = self.convert_to_trial_spec(trial_data)
                
                if not trial_spec:
                    stats['failed'] += 1
                    continue
                
                stats['converted'] += 1
                
                # Generate protocol structure
                protocol = generator.generate_structured_protocol(trial_spec)
                
                # Add to RAG
                doc_id = rag_service.add_protocol_example(trial_spec, protocol)
                
                stats['added'] += 1
                
                # Progress update
                if i % batch_size == 0 or i == len(trials):
                    print(f"   Progress: {i}/{len(trials)} | "
                          f"✅ Added: {stats['added']} | "
                          f"❌ Failed: {stats['failed']}")
                
            except Exception as e:
                stats['failed'] += 1
                if stats['failed'] <= 5:  # Only show first few errors
                    print(f"   ⚠ Error processing trial {i}: {str(e)[:60]}")
        
        # Final report
        print("\n" + "="*70)
        print("IMPORT COMPLETE!")
        print("="*70)
        print(f"\n📊 Import Statistics:")
        print(f"   Fetched from API: {stats['fetched']}")
        print(f"   Successfully converted: {stats['converted']}")
        print(f"   Added to RAG database: {stats['added']}")
        print(f"   Failed: {stats['failed']}")
        print(f"   Success rate: {(stats['added']/stats['fetched']*100):.1f}%")
        
        # Show updated database stats
        total_count = rag_service.get_count()
        print(f"\n📈 Total protocols in RAG database: {total_count}")
        
        print(f"\n💡 Database location: ./vector_db/")
        print("="*70)
        
        return stats


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Import real clinical trials from ClinicalTrials.gov'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=500,
        help='Number of trials to import (default: 500)'
    )
    parser.add_argument(
        '--phases',
        nargs='+',
        choices=['PHASE1', 'PHASE2', 'PHASE3', 'PHASE4'],
        default=['PHASE2', 'PHASE3'],
        help='Trial phases to import (default: PHASE2 PHASE3)'
    )
    parser.add_argument(
        '--conditions',
        nargs='+',
        help='Specific conditions to filter (e.g., Cancer Diabetes)'
    )
    
    args = parser.parse_args()
    
    # Create importer
    importer = ClinicalTrialsImporter()
    
    # Run import
    stats = importer.import_to_rag(
        max_trials=args.count,
        phases=args.phases,
        conditions=args.conditions
    )
    
    # Exit with appropriate code
    if stats['added'] > 0:
        print(f"\n✅ Successfully imported {stats['added']} real clinical trial protocols!")
        sys.exit(0)
    else:
        print("\n❌ Import failed - no protocols were added")
        sys.exit(1)


if __name__ == "__main__":
    main()
