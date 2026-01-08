"""Generate UI dropdown options from RAG database."""
import sys
import os
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.rag_service import get_rag_service


def categorize_indication(indication: str) -> str:
    """Categorize indication into therapeutic area."""
    indication_lower = indication.lower()
    
    # Oncology keywords
    oncology_keywords = ['cancer', 'carcinoma', 'melanoma', 'leukemia', 'lymphoma', 'sarcoma', 
                         'myeloma', 'glioma', 'glioblastoma', 'tumor', 'neoplasm', 'malignant']
    
    # Cardiovascular keywords
    cardio_keywords = ['heart', 'cardiac', 'cardiovascular', 'myocardial', 'atrial', 'hypertension',
                      'hypercholesterolemia', 'stroke', 'angina', 'infarction']
    
    # Rheumatology/Immunology keywords
    rheum_keywords = ['arthritis', 'lupus', 'rheumatoid', 'spondylitis', 'autoimmune', 'psoriasis',
                     'scleroderma', 'dermatomyositis']
    
    # Neurology keywords
    neuro_keywords = ['alzheimer', 'parkinson', 'multiple sclerosis', 'epilepsy', 'migraine', 
                     'neuropathy', 'tremor', 'dementia', 'encephalopathy', 'dystonia']
    
    # Endocrinology keywords
    endo_keywords = ['diabetes', 'obesity', 'thyroid', 'metabolic', 'hypoglycemia', 'insulin',
                    'hypoparathyroidism', 'gaucher', 'lipodystrophy']
    
    # Psychiatry keywords
    psych_keywords = ['depression', 'schizophrenia', 'bipolar', 'anxiety', 'ptsd', 'autism',
                     'adhd', 'mental', 'psychiatric', 'gambling', 'obsessive']
    
    # Dermatology keywords
    derm_keywords = ['dermatitis', 'atopic', 'skin', 'eczema', 'urticaria', 'psoriasis',
                    'alopecia', 'hyperhidrosis', 'acne']
    
    # Respiratory keywords
    resp_keywords = ['asthma', 'copd', 'pulmonary', 'lung', 'respiratory', 'fibrosis', 
                    'pneumonia', 'cystic fibrosis', 'bronchial']
    
    # Gastroenterology keywords
    gastro_keywords = ['colitis', 'crohn', 'ibs', 'bowel', 'gastric', 'hepatitis', 
                      'liver', 'gastrointestinal', 'esophageal', 'pancreatic']
    
    # Infectious Disease keywords
    infect_keywords = ['hiv', 'hepatitis', 'tuberculosis', 'covid', 'influenza', 'infection',
                      'sepsis', 'pneumococcal', 'viral', 'bacterial']
    
    # Hematology keywords
    hema_keywords = ['anemia', 'hemophilia', 'sickle cell', 'thrombocytopenia', 'polycythemia',
                    'myeloproliferative', 'myelodysplastic']
    
    # Nephrology keywords
    nephro_keywords = ['kidney', 'renal', 'nephropathy', 'nephritis', 'dialysis']
    
    # Check categories
    for keyword in oncology_keywords:
        if keyword in indication_lower:
            return "Oncology"
    
    for keyword in cardio_keywords:
        if keyword in indication_lower:
            return "Cardiovascular"
    
    for keyword in rheum_keywords:
        if keyword in indication_lower:
            return "Rheumatology / Immunology"
    
    for keyword in neuro_keywords:
        if keyword in indication_lower:
            return "Neurology"
    
    for keyword in endo_keywords:
        if keyword in indication_lower:
            return "Endocrinology / Metabolism"
    
    for keyword in psych_keywords:
        if keyword in indication_lower:
            return "Psychiatry"
    
    for keyword in derm_keywords:
        if keyword in indication_lower:
            return "Dermatology"
    
    for keyword in resp_keywords:
        if keyword in indication_lower:
            return "Respiratory"
    
    for keyword in gastro_keywords:
        if keyword in indication_lower:
            return "Gastroenterology"
    
    for keyword in infect_keywords:
        if keyword in indication_lower:
            return "Infectious Disease"
    
    for keyword in hema_keywords:
        if keyword in indication_lower:
            return "Hematology"
    
    for keyword in nephro_keywords:
        if keyword in indication_lower:
            return "Nephrology"
    
    return "Other"


def generate_indication_options():
    """Generate HTML options for indication dropdown from RAG database."""
    rag = get_rag_service()
    
    # Get all protocols with metadata
    results = rag.collection.get(include=['metadatas'])
    
    # Count indications
    indication_counts = defaultdict(int)
    for metadata in results['metadatas']:
        indication = metadata.get('indication', 'Unknown')
        indication_counts[indication] += 1
    
    # Group by category
    categories = defaultdict(list)
    for indication, count in indication_counts.items():
        if indication == 'Unknown' or not indication:
            continue
        category = categorize_indication(indication)
        categories[category].append((indication, count))
    
    # Sort indications within each category by count (most common first)
    for category in categories:
        categories[category].sort(key=lambda x: (-x[1], x[0]))
    
    # Sort categories
    category_order = [
        "Oncology",
        "Cardiovascular", 
        "Rheumatology / Immunology",
        "Neurology",
        "Endocrinology / Metabolism",
        "Psychiatry",
        "Dermatology",
        "Respiratory",
        "Gastroenterology",
        "Infectious Disease",
        "Hematology",
        "Nephrology",
        "Pain Management",
        "Ophthalmology",
        "Other"
    ]
    
    # Generate HTML
    print("\n" + "="*70)
    print("INDICATION DROPDOWN OPTIONS (based on 1,096 protocols)")
    print("="*70)
    print("\nPaste this into web/index.html (replace the indication select options):\n")
    
    for category in category_order:
        if category not in categories:
            continue
        
        indications = categories[category]
        print(f'                                <optgroup label="{category}">')
        
        # Show top indications per category (up to 15)
        for indication, count in indications[:15]:
            safe_indication = indication.replace('"', '&quot;')
            print(f'                                    <option value="{safe_indication}">{indication} ({count})</option>')
        
        print('                                </optgroup>')
        print()
    
    # Statistics
    print("\n" + "="*70)
    print("STATISTICS")
    print("="*70)
    total_unique = sum(len(indications) for indications in categories.values())
    print(f"Total unique indications: {total_unique}")
    print(f"Total protocols: {sum(indication_counts.values())}")
    print(f"\nTop 20 Most Common Indications:")
    top_20 = sorted(indication_counts.items(), key=lambda x: -x[1])[:20]
    for i, (indication, count) in enumerate(top_20, 1):
        print(f"  {i:2}. {indication:50} ({count:3} protocols)")


if __name__ == "__main__":
    generate_indication_options()
