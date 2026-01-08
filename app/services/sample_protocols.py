"""Sample protocol data for populating the vector database."""
from app.models.schemas import TrialSpecInput, TrialPhase, TrialEndpoint, EndpointType


# Sample Protocol 1: Oncology Phase 3
ONCOLOGY_PHASE3 = TrialSpecInput(
    sponsor="Oncology Research Institute",
    title="Phase III Randomized Study of Novel Checkpoint Inhibitor in Advanced Non-Small Cell Lung Cancer",
    short_title="Checkpoint Inhibitor in NSCLC",
    indication="Advanced Non-Small Cell Lung Cancer",
    phase=TrialPhase.PHASE_3,
    design="randomized, open-label, active-controlled, multicenter",
    sample_size=450,
    duration_weeks=104,
    treatment_arms=[
        "Novel Checkpoint Inhibitor 200mg IV Q3W",
        "Standard of Care Chemotherapy"
    ],
    key_endpoints=[
        TrialEndpoint(
            type=EndpointType.PRIMARY,
            name="Overall Survival (OS)",
            description="Time from randomization to death from any cause",
            measurement_timepoint="Until death or end of study"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Progression-Free Survival (PFS)",
            description="Time from randomization to disease progression or death",
            measurement_timepoint="Every 6 weeks"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Objective Response Rate (ORR)",
            description="Proportion of patients with complete or partial response",
            measurement_timepoint="Every 6 weeks"
        ),
    ],
    inclusion_criteria=[
        "Age ≥ 18 years",
        "Histologically confirmed advanced NSCLC",
        "ECOG performance status 0-1",
        "Measurable disease per RECIST v1.1",
        "Adequate organ function",
        "Life expectancy ≥ 3 months",
    ],
    exclusion_criteria=[
        "Prior immune checkpoint inhibitor therapy",
        "Active brain metastases",
        "Active autoimmune disease",
        "Systemic immunosuppression",
        "Uncontrolled intercurrent illness",
    ],
    age_range="18-99",
    region="Global",
    number_of_sites=100,
    background="NSCLC remains a leading cause of cancer mortality. Novel checkpoint inhibitors targeting PD-L1 have shown promising results in early phase studies.",
    prior_therapy_allowed=True
)

# Sample Protocol 2: Cardiovascular Phase 2
CARDIOVASCULAR_PHASE2 = TrialSpecInput(
    sponsor="Cardiology Innovations Ltd",
    title="Phase II Double-Blind Study of Novel PCSK9 Inhibitor in Patients with Hypercholesterolemia",
    short_title="PCSK9 Inhibitor Study",
    indication="Hypercholesterolemia",
    phase=TrialPhase.PHASE_2,
    design="randomized, double-blind, placebo-controlled, parallel-group",
    sample_size=180,
    duration_weeks=24,
    treatment_arms=[
        "PCSK9 Inhibitor 150mg SC Q2W",
        "PCSK9 Inhibitor 300mg SC Q4W",
        "Placebo SC Q2W"
    ],
    key_endpoints=[
        TrialEndpoint(
            type=EndpointType.PRIMARY,
            name="Change in LDL-C from baseline to Week 24",
            description="Percent change in LDL cholesterol levels",
            measurement_timepoint="Week 24"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Change in total cholesterol",
            description="Percent change in total cholesterol from baseline",
            measurement_timepoint="Week 12 and Week 24"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Safety and tolerability",
            description="Incidence of adverse events",
            measurement_timepoint="Throughout study"
        ),
    ],
    inclusion_criteria=[
        "Age 18-75 years",
        "LDL-C ≥ 100 mg/dL despite statin therapy",
        "Stable statin dose for ≥ 4 weeks",
        "BMI 18-40 kg/m²",
    ],
    exclusion_criteria=[
        "Uncontrolled hypertension (>160/100 mmHg)",
        "Recent cardiovascular event (<3 months)",
        "Severe hepatic impairment",
        "Known PCSK9 inhibitor intolerance",
    ],
    age_range="18-75",
    region="US/EU",
    number_of_sites=30,
    background="Hypercholesterolemia is a major risk factor for cardiovascular disease. PCSK9 inhibitors represent a promising approach for patients with inadequate LDL-C control on statins.",
    prior_therapy_allowed=True
)

# Sample Protocol 3: Rheumatology Phase 2
RHEUMATOLOGY_PHASE2 = TrialSpecInput(
    sponsor="Autoimmune Therapeutics Inc",
    title="Phase II Proof-of-Concept Study of JAK Inhibitor in Moderate to Severe Rheumatoid Arthritis",
    short_title="JAK Inhibitor in RA",
    indication="Rheumatoid Arthritis",
    phase=TrialPhase.PHASE_2,
    design="randomized, double-blind, placebo-controlled",
    sample_size=200,
    duration_weeks=52,
    treatment_arms=[
        "JAK Inhibitor 5mg once daily",
        "JAK Inhibitor 10mg once daily",
        "Placebo once daily"
    ],
    key_endpoints=[
        TrialEndpoint(
            type=EndpointType.PRIMARY,
            name="ACR20 response at Week 24",
            description="Proportion of patients achieving ACR20 response",
            measurement_timepoint="Week 24"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Change in DAS28-CRP",
            description="Change from baseline in Disease Activity Score",
            measurement_timepoint="Week 12, 24, 52"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Radiographic progression",
            description="Change in modified Total Sharp Score",
            measurement_timepoint="Week 52"
        ),
    ],
    inclusion_criteria=[
        "Age 18-75 years",
        "ACR/EULAR 2010 criteria for RA ≥6 months",
        "Active disease (DAS28-CRP ≥3.2)",
        "≥6 tender and ≥6 swollen joints",
        "Inadequate response to MTX or csDMARDs",
    ],
    exclusion_criteria=[
        "Prior JAK inhibitor therapy",
        "Recent biologic DMARD use (<8 weeks)",
        "Active or latent tuberculosis",
        "Hepatitis B or C infection",
        "Absolute lymphocyte count <500/mm³",
    ],
    age_range="18-75",
    region="US/EU/Asia",
    number_of_sites=50,
    background="Rheumatoid arthritis affects millions globally. JAK inhibitors offer a novel oral treatment option for patients with inadequate response to conventional DMARDs.",
    prior_therapy_allowed=True
)

# Sample Protocol 4: Neurology Phase 2
NEUROLOGY_PHASE2 = TrialSpecInput(
    sponsor="Neuroscience Partners",
    title="Phase II Study of Monoclonal Antibody in Early Alzheimer's Disease",
    short_title="Anti-Amyloid mAb in AD",
    indication="Early Alzheimer's Disease",
    phase=TrialPhase.PHASE_2,
    design="randomized, double-blind, placebo-controlled",
    sample_size=250,
    duration_weeks=78,
    treatment_arms=[
        "Anti-Amyloid mAb 10mg/kg IV Q4W",
        "Placebo IV Q4W"
    ],
    key_endpoints=[
        TrialEndpoint(
            type=EndpointType.PRIMARY,
            name="Change in CDR-SB at Week 78",
            description="Change from baseline in Clinical Dementia Rating Sum of Boxes",
            measurement_timepoint="Week 78"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Change in ADAS-Cog14",
            description="Change in cognitive function score",
            measurement_timepoint="Week 26, 52, 78"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Amyloid PET SUVr change",
            description="Change in brain amyloid burden",
            measurement_timepoint="Week 78"
        ),
    ],
    inclusion_criteria=[
        "Age 50-85 years",
        "Clinical diagnosis of mild cognitive impairment or mild dementia due to AD",
        "MMSE score 20-28",
        "Positive amyloid PET scan",
        "Study partner available",
        "Stable medications for ≥4 weeks",
    ],
    exclusion_criteria=[
        "Other primary cause of dementia",
        "History of stroke or TIA within 2 years",
        "Significant cardiovascular disease",
        "MRI contraindications",
        "ARIA risk factors",
    ],
    age_range="50-85",
    region="US/EU",
    number_of_sites=60,
    background="Alzheimer's disease is a progressive neurodegenerative disorder. Anti-amyloid therapies targeting beta-amyloid plaques represent a disease-modifying approach.",
    prior_therapy_allowed=False
)

# Sample Protocol 5: Diabetes Phase 3
DIABETES_PHASE3 = TrialSpecInput(
    sponsor="Metabolic Health Corp",
    title="Phase III Study of Novel GLP-1 Receptor Agonist in Type 2 Diabetes",
    short_title="GLP-1 RA in T2D",
    indication="Type 2 Diabetes Mellitus",
    phase=TrialPhase.PHASE_3,
    design="randomized, double-blind, active-controlled, non-inferiority",
    sample_size=800,
    duration_weeks=52,
    treatment_arms=[
        "Novel GLP-1 RA 1mg SC once weekly",
        "Active Comparator GLP-1 RA 1mg SC once weekly"
    ],
    key_endpoints=[
        TrialEndpoint(
            type=EndpointType.PRIMARY,
            name="Change in HbA1c at Week 52",
            description="Change from baseline in glycated hemoglobin",
            measurement_timepoint="Week 52"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Proportion achieving HbA1c <7%",
            description="Glycemic control target achievement",
            measurement_timepoint="Week 52"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Change in body weight",
            description="Percent change in body weight from baseline",
            measurement_timepoint="Week 26 and 52"
        ),
    ],
    inclusion_criteria=[
        "Age 18-75 years",
        "Type 2 diabetes ≥6 months",
        "HbA1c 7.0-10.5%",
        "BMI 23-45 kg/m²",
        "Stable metformin therapy ≥8 weeks",
    ],
    exclusion_criteria=[
        "Type 1 diabetes or secondary diabetes",
        "History of pancreatitis",
        "Severe renal impairment (eGFR <30)",
        "Recent cardiovascular event (<3 months)",
        "Personal or family history of medullary thyroid carcinoma",
    ],
    age_range="18-75",
    region="Global",
    number_of_sites=150,
    background="Type 2 diabetes affects over 400 million people worldwide. GLP-1 receptor agonists offer glycemic control with weight loss benefits and cardiovascular protection.",
    prior_therapy_allowed=True
)

# Sample Protocol 6: Gastroenterology - IBD
GASTRO_IBD_PHASE3 = TrialSpecInput(
    sponsor="GI Therapeutics Global",
    title="Phase III Study of Anti-Integrin Monoclonal Antibody in Moderate to Severe Ulcerative Colitis",
    short_title="Anti-Integrin mAb in UC",
    indication="Ulcerative Colitis",
    phase=TrialPhase.PHASE_3,
    design="randomized, double-blind, placebo-controlled, multicenter",
    sample_size=600,
    duration_weeks=52,
    treatment_arms=[
        "Anti-Integrin mAb 300mg IV at Weeks 0, 2, 6, then Q8W",
        "Placebo IV at Weeks 0, 2, 6, then Q8W"
    ],
    key_endpoints=[
        TrialEndpoint(
            type=EndpointType.PRIMARY,
            name="Clinical remission at Week 52",
            description="Mayo score ≤2 with no subscore >1 and rectal bleeding subscore 0",
            measurement_timepoint="Week 52"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Endoscopic improvement",
            description="Endoscopic Mayo subscore ≤1",
            measurement_timepoint="Week 52"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Corticosteroid-free remission",
            description="Clinical remission without corticosteroids",
            measurement_timepoint="Week 52"
        ),
    ],
    inclusion_criteria=[
        "Age 18-75 years",
        "Confirmed diagnosis of UC ≥3 months",
        "Moderate to severe active disease (Mayo score 6-12)",
        "Endoscopic subscore ≥2",
        "Inadequate response or intolerance to conventional therapy",
        "Stable oral 5-ASA or immunomodulators if used",
    ],
    exclusion_criteria=[
        "Crohn's disease or indeterminate colitis",
        "Toxic megacolon or bowel obstruction",
        "Colonic dysplasia or cancer",
        "Prior anti-integrin therapy",
        "Active or latent tuberculosis",
        "Progressive multifocal leukoencephalopathy risk",
    ],
    age_range="18-75",
    region="Global",
    number_of_sites=120,
    background="Ulcerative colitis is a chronic inflammatory bowel disease affecting the colon. Integrin antagonists block lymphocyte trafficking to the gut, offering a targeted approach for UC treatment.",
    prior_therapy_allowed=True
)

# Sample Protocol 7: Dermatology - Psoriasis
DERMATOLOGY_PSORIASIS_PHASE3 = TrialSpecInput(
    sponsor="Dermatology Innovations Inc",
    title="Phase III Study of IL-17 Inhibitor in Moderate to Severe Plaque Psoriasis",
    short_title="IL-17 Inhibitor in Psoriasis",
    indication="Plaque Psoriasis",
    phase=TrialPhase.PHASE_3,
    design="randomized, double-blind, active-controlled, parallel-group",
    sample_size=450,
    duration_weeks=52,
    treatment_arms=[
        "IL-17 Inhibitor 150mg SC at Weeks 0, 1, 2, 3, 4, then Q4W",
        "Active Comparator TNF-alpha Inhibitor per label"
    ],
    key_endpoints=[
        TrialEndpoint(
            type=EndpointType.PRIMARY,
            name="PASI 90 at Week 16",
            description="Proportion achieving ≥90% improvement in PASI score",
            measurement_timepoint="Week 16"
        ),
        TrialEndpoint(
            type=EndpointType.PRIMARY,
            name="IGA 0/1 at Week 16",
            description="Investigator Global Assessment score of clear or almost clear",
            measurement_timepoint="Week 16"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Sustained response at Week 52",
            description="Maintenance of PASI 90 response",
            measurement_timepoint="Week 52"
        ),
    ],
    inclusion_criteria=[
        "Age 18-75 years",
        "Chronic plaque psoriasis ≥6 months",
        "BSA ≥10%, PASI ≥12, IGA ≥3",
        "Candidate for systemic therapy or phototherapy",
        "Inadequate response to topical therapy",
    ],
    exclusion_criteria=[
        "Non-plaque forms of psoriasis",
        "Drug-induced psoriasis",
        "Active infection requiring treatment",
        "Active tuberculosis or untreated latent TB",
        "Inflammatory bowel disease requiring treatment",
        "Previous exposure to IL-17 inhibitors",
    ],
    age_range="18-75",
    region="US/EU/Asia-Pacific",
    number_of_sites=80,
    background="Psoriasis is a chronic immune-mediated skin disease affecting 2-3% of the population. IL-17 inhibitors target a key cytokine in psoriasis pathogenesis, offering high efficacy rates.",
    prior_therapy_allowed=True
)

# Sample Protocol 8: Psychiatry - Depression
PSYCHIATRY_DEPRESSION_PHASE3 = TrialSpecInput(
    sponsor="NeuroMind Pharmaceuticals",
    title="Phase III Study of Novel Glutamatergic Modulator in Treatment-Resistant Major Depressive Disorder",
    short_title="Glutamatergic Agent in TRD",
    indication="Treatment-Resistant Depression",
    phase=TrialPhase.PHASE_3,
    design="randomized, double-blind, placebo-controlled, flexible-dose",
    sample_size=350,
    duration_weeks=32,
    treatment_arms=[
        "Glutamatergic Modulator 56mg nasal spray twice weekly",
        "Placebo nasal spray twice weekly"
    ],
    key_endpoints=[
        TrialEndpoint(
            type=EndpointType.PRIMARY,
            name="Change in MADRS at Week 4",
            description="Change from baseline in Montgomery-Åsberg Depression Rating Scale",
            measurement_timepoint="Week 4"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Response rate",
            description="Proportion with ≥50% reduction in MADRS",
            measurement_timepoint="Week 4 and 8"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Remission rate",
            description="Proportion achieving MADRS ≤10",
            measurement_timepoint="Week 4 and 8"
        ),
    ],
    inclusion_criteria=[
        "Age 18-65 years",
        "MDD per DSM-5, current major depressive episode ≥4 weeks",
        "MADRS ≥28 at screening and baseline",
        "Treatment-resistant: inadequate response to ≥2 antidepressants",
        "On stable antidepressant ≥4 weeks",
        "CGI-Severity ≥4",
    ],
    exclusion_criteria=[
        "Bipolar disorder or psychotic disorder",
        "Active suicidal ideation with intent",
        "Substance use disorder within 6 months",
        "History of ketamine/esketamine use disorder",
        "Uncontrolled hypertension",
        "Pregnancy or breastfeeding",
    ],
    age_range="18-65",
    region="US/EU",
    number_of_sites=70,
    background="Treatment-resistant depression affects 30% of MDD patients. Novel glutamatergic modulators offer rapid antidepressant effects through NMDA receptor antagonism.",
    prior_therapy_allowed=True
)

# Sample Protocol 9: Infectious Disease - HIV
INFECTIOUS_HIV_PHASE2 = TrialSpecInput(
    sponsor="Global Health Partners",
    title="Phase II Study of Long-Acting Injectable HIV Treatment in Virologically Suppressed Adults",
    short_title="LA-ART in HIV",
    indication="HIV-1 Infection",
    phase=TrialPhase.PHASE_2,
    design="randomized, open-label, active-controlled, non-inferiority",
    sample_size=280,
    duration_weeks=96,
    treatment_arms=[
        "Long-Acting Injectable Regimen IM Q8W",
        "Current Oral ART (continuation)"
    ],
    key_endpoints=[
        TrialEndpoint(
            type=EndpointType.PRIMARY,
            name="Virologic suppression at Week 48",
            description="Proportion with HIV-1 RNA <50 copies/mL",
            measurement_timepoint="Week 48"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Sustained suppression at Week 96",
            description="HIV-1 RNA <50 copies/mL maintained",
            measurement_timepoint="Week 96"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Treatment satisfaction",
            description="HIV Treatment Satisfaction Questionnaire score",
            measurement_timepoint="Week 24, 48, 96"
        ),
    ],
    inclusion_criteria=[
        "Age 18-65 years",
        "Confirmed HIV-1 infection",
        "On stable oral ART ≥6 months",
        "HIV-1 RNA <50 copies/mL for ≥6 months",
        "CD4+ count ≥200 cells/μL",
        "No resistance to study drugs",
    ],
    exclusion_criteria=[
        "Hepatitis B requiring treatment",
        "Active opportunistic infection",
        "Prior virologic failure on integrase inhibitor",
        "Chronic hepatitis with ALT >5x ULN",
        "Pregnancy or breastfeeding",
        "BMI <18 or >35 kg/m²",
    ],
    age_range="18-65",
    region="Global",
    number_of_sites=50,
    background="HIV treatment adherence challenges persist with daily oral therapy. Long-acting injectable antiretroviral regimens offer improved convenience and potentially better adherence.",
    prior_therapy_allowed=True
)

# Sample Protocol 10: Hematology - Anemia
HEMATOLOGY_ANEMIA_PHASE3 = TrialSpecInput(
    sponsor="Hematology Research Consortium",
    title="Phase III Study of Novel Erythropoiesis-Stimulating Agent in Anemia of Chronic Kidney Disease",
    short_title="ESA in CKD Anemia",
    indication="Anemia of Chronic Kidney Disease",
    phase=TrialPhase.PHASE_3,
    design="randomized, open-label, active-controlled, non-inferiority",
    sample_size=500,
    duration_weeks=52,
    treatment_arms=[
        "Novel ESA IV/SC Q4W",
        "Standard ESA IV/SC Q1W or Q2W per label"
    ],
    key_endpoints=[
        TrialEndpoint(
            type=EndpointType.PRIMARY,
            name="Mean hemoglobin change",
            description="Change from baseline in mean hemoglobin (Weeks 40-52)",
            measurement_timepoint="Weeks 40-52"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Proportion achieving Hb target",
            description="Hemoglobin 10-12 g/dL maintained",
            measurement_timepoint="Weeks 40-52"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Cardiovascular events",
            description="MACE (death, MI, stroke, hospitalization for HF)",
            measurement_timepoint="Throughout study"
        ),
    ],
    inclusion_criteria=[
        "Age 18-85 years",
        "CKD Stage 3-5 not on dialysis or on hemodialysis",
        "Hemoglobin 8.0-11.0 g/dL",
        "Either ESA-naive or on stable ESA ≥8 weeks",
        "Transferrin saturation ≥20%, ferritin ≥100 ng/mL",
    ],
    exclusion_criteria=[
        "Active bleeding or recent transfusion <8 weeks",
        "Uncontrolled hypertension (>180/110 mmHg)",
        "Recent cardiovascular event (<3 months)",
        "Active malignancy",
        "Pure red cell aplasia or hemolytic anemia",
    ],
    age_range="18-85",
    region="Global",
    number_of_sites=100,
    background="Anemia is prevalent in CKD patients and associated with increased morbidity. Novel long-acting ESAs offer less frequent dosing while maintaining effective erythropoiesis.",
    prior_therapy_allowed=True
)

# Sample Protocol 11: Pulmonary - Asthma
PULMONARY_ASTHMA_PHASE3 = TrialSpecInput(
    sponsor="Respiratory Medicine Alliance",
    title="Phase III Study of Anti-IL-5 Receptor Monoclonal Antibody in Severe Eosinophilic Asthma",
    short_title="Anti-IL-5R mAb in Asthma",
    indication="Severe Eosinophilic Asthma",
    phase=TrialPhase.PHASE_3,
    design="randomized, double-blind, placebo-controlled, parallel-group",
    sample_size=400,
    duration_weeks=52,
    treatment_arms=[
        "Anti-IL-5R mAb 100mg SC Q4W",
        "Placebo SC Q4W"
    ],
    key_endpoints=[
        TrialEndpoint(
            type=EndpointType.PRIMARY,
            name="Annual exacerbation rate",
            description="Rate of clinically significant asthma exacerbations",
            measurement_timepoint="52 weeks"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Change in FEV1",
            description="Change from baseline in pre-bronchodilator FEV1",
            measurement_timepoint="Week 52"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Asthma control",
            description="Change in ACQ-5 score from baseline",
            measurement_timepoint="Week 52"
        ),
    ],
    inclusion_criteria=[
        "Age 18-75 years",
        "Physician-diagnosed asthma ≥12 months",
        "≥2 exacerbations in past 12 months requiring systemic corticosteroids",
        "Blood eosinophils ≥300 cells/μL at screening",
        "On high-dose ICS plus LABA ≥12 weeks",
        "FEV1 <80% predicted",
    ],
    exclusion_criteria=[
        "Current smoker or ≥10 pack-year history",
        "Other significant lung disease",
        "Parasitic infection within 6 months",
        "Immunodeficiency disorder",
        "Recent biologics use (<4 months)",
    ],
    age_range="18-75",
    region="Global",
    number_of_sites=90,
    background="Severe asthma with eosinophilic inflammation affects ~10% of asthma patients. Anti-IL-5 receptor antibodies reduce eosinophils and exacerbation rates in this population.",
    prior_therapy_allowed=True
)

# Sample Protocol 12: Endocrinology - Thyroid
ENDOCRINE_THYROID_PHASE2 = TrialSpecInput(
    sponsor="Endocrine Therapeutics Ltd",
    title="Phase II Study of Selective Thyroid Hormone Receptor Beta Agonist in Non-Alcoholic Steatohepatitis",
    short_title="THR-β Agonist in NASH",
    indication="Non-Alcoholic Steatohepatitis",
    phase=TrialPhase.PHASE_2,
    design="randomized, double-blind, placebo-controlled, dose-ranging",
    sample_size=240,
    duration_weeks=36,
    treatment_arms=[
        "THR-β Agonist 5mg once daily",
        "THR-β Agonist 10mg once daily",
        "THR-β Agonist 20mg once daily",
        "Placebo once daily"
    ],
    key_endpoints=[
        TrialEndpoint(
            type=EndpointType.PRIMARY,
            name="Hepatic fat reduction",
            description="Relative reduction in hepatic fat fraction by MRI-PDFF",
            measurement_timepoint="Week 36"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="NASH resolution",
            description="Resolution of NASH without worsening fibrosis on liver biopsy",
            measurement_timepoint="Week 36"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Change in liver enzymes",
            description="Change in ALT and AST from baseline",
            measurement_timepoint="Week 12, 24, 36"
        ),
    ],
    inclusion_criteria=[
        "Age 18-75 years",
        "Biopsy-confirmed NASH with NAS ≥4 and fibrosis stage F1-F3",
        "Hepatic fat fraction ≥10% by MRI-PDFF",
        "BMI 25-45 kg/m²",
        "Stable weight (±5%) for 6 months",
    ],
    exclusion_criteria=[
        "Other causes of chronic liver disease",
        "Decompensated cirrhosis or HCC",
        "Thyroid dysfunction (TSH outside normal range)",
        "Recent weight loss surgery (<2 years)",
        "Alcohol consumption >20g/day (women) or >30g/day (men)",
        "Type 1 diabetes",
    ],
    age_range="18-75",
    region="US/EU",
    number_of_sites=40,
    background="NASH is a progressive liver disease with limited treatment options. Thyroid hormone receptor-β agonists reduce hepatic lipid accumulation while avoiding systemic thyrotoxicity.",
    prior_therapy_allowed=False
)

# Sample Protocol 13: Renal - CKD
RENAL_CKD_PHASE3 = TrialSpecInput(
    sponsor="Nephrology Innovation Group",
    title="Phase III Study of SGLT2 Inhibitor in Chronic Kidney Disease without Diabetes",
    short_title="SGLT2i in Non-Diabetic CKD",
    indication="Chronic Kidney Disease",
    phase=TrialPhase.PHASE_3,
    design="randomized, double-blind, placebo-controlled, event-driven",
    sample_size=3000,
    duration_weeks=156,
    treatment_arms=[
        "SGLT2 Inhibitor 10mg once daily",
        "Placebo once daily"
    ],
    key_endpoints=[
        TrialEndpoint(
            type=EndpointType.PRIMARY,
            name="Composite renal outcome",
            description="Sustained ≥50% eGFR decline, ESKD, or renal death",
            measurement_timepoint="Time to event (median 3 years)"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Cardiovascular composite",
            description="CV death, non-fatal MI, non-fatal stroke, hospitalization for HF",
            measurement_timepoint="Time to event"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="eGFR slope",
            description="Annual rate of eGFR decline",
            measurement_timepoint="Throughout study"
        ),
    ],
    inclusion_criteria=[
        "Age 18-85 years",
        "CKD with eGFR 20-60 mL/min/1.73m²",
        "UACR ≥200 mg/g",
        "On stable ACEi or ARB therapy ≥4 weeks (unless contraindicated)",
        "No diabetes mellitus",
    ],
    exclusion_criteria=[
        "Type 1 or Type 2 diabetes",
        "Kidney transplant recipient or planned transplant",
        "Autoimmune kidney disease requiring immunosuppression",
        "Polycystic kidney disease",
        "Recent acute kidney injury (<3 months)",
    ],
    age_range="18-85",
    region="Global",
    number_of_sites=200,
    background="CKD affects 10% of the global population. SGLT2 inhibitors have shown renoprotective effects in diabetic kidney disease and may benefit non-diabetic CKD patients.",
    prior_therapy_allowed=True
)

# Sample Protocol 14: Hepatology - NASH Cirrhosis
HEPATOLOGY_NASH_PHASE3 = TrialSpecInput(
    sponsor="Liver Disease Research Network",
    title="Phase III Study of FXR Agonist in NASH with Compensated Cirrhosis",
    short_title="FXR Agonist in NASH Cirrhosis",
    indication="NASH with Compensated Cirrhosis",
    phase=TrialPhase.PHASE_3,
    design="randomized, double-blind, placebo-controlled",
    sample_size=1200,
    duration_weeks=240,
    treatment_arms=[
        "FXR Agonist 10mg once daily",
        "Placebo once daily"
    ],
    key_endpoints=[
        TrialEndpoint(
            type=EndpointType.PRIMARY,
            name="Clinical outcome composite",
            description="Time to liver-related death, liver transplant, MELD ≥15, ascites, variceal hemorrhage, HCC, or HE",
            measurement_timepoint="Time to event (up to 240 weeks)"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Fibrosis improvement",
            description="≥1 stage fibrosis improvement without NASH worsening",
            measurement_timepoint="Week 96 (biopsy)"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Change in liver stiffness",
            description="Change in vibration-controlled transient elastography",
            measurement_timepoint="Week 48, 96, 144, 192"
        ),
    ],
    inclusion_criteria=[
        "Age 18-75 years",
        "Biopsy-confirmed NASH with compensated cirrhosis (F4)",
        "Liver stiffness ≥14.6 kPa by VCTE",
        "MELD score <12",
        "Platelets ≥75,000/μL",
    ],
    exclusion_criteria=[
        "Decompensated cirrhosis (ascites, variceal bleeding, HE)",
        "Other causes of chronic liver disease",
        "Hepatocellular carcinoma or AFP >50 ng/mL",
        "Liver transplant recipient",
        "Alcohol >20g/day (women) or >30g/day (men)",
        "Recent GI bleeding (<6 months)",
    ],
    age_range="18-75",
    region="Global",
    number_of_sites=150,
    background="NASH cirrhosis is a leading indication for liver transplantation. FXR agonists reduce inflammation and fibrosis through bile acid-mediated pathways.",
    prior_therapy_allowed=False
)

# Sample Protocol 15: Immunology - Lupus
IMMUNOLOGY_LUPUS_PHASE3 = TrialSpecInput(
    sponsor="Autoimmune Disease Institute",
    title="Phase III Study of B-Cell Depleting Antibody in Active Lupus Nephritis",
    short_title="B-Cell Depletion in LN",
    indication="Lupus Nephritis",
    phase=TrialPhase.PHASE_3,
    design="randomized, double-blind, placebo-controlled",
    sample_size=450,
    duration_weeks=104,
    treatment_arms=[
        "B-Cell Depleting mAb 1000mg IV at Days 1 and 15, then at Months 6 and 12",
        "Placebo IV at Days 1 and 15, then at Months 6 and 12"
    ],
    key_endpoints=[
        TrialEndpoint(
            type=EndpointType.PRIMARY,
            name="Complete renal response at Week 104",
            description="UPCR <0.5, eGFR ≥60 or ≤20% below baseline, no rescue therapy",
            measurement_timepoint="Week 104"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Sustained response",
            description="Complete renal response maintained from Week 52-104",
            measurement_timepoint="Week 52-104"
        ),
        TrialEndpoint(
            type=EndpointType.SECONDARY,
            name="Time to event outcome",
            description="Time to renal-related event or death",
            measurement_timepoint="Throughout study"
        ),
    ],
    inclusion_criteria=[
        "Age 18-70 years",
        "SLE per ACR or SLICC criteria",
        "Active lupus nephritis (Class III, IV, or V on biopsy within 6 months)",
        "UPCR ≥1.0 mg/mg",
        "eGFR ≥30 mL/min/1.73m²",
        "Concurrent MMF or cyclophosphamide induction",
    ],
    exclusion_criteria=[
        "Severe CNS lupus",
        "Severe active infection",
        "Prior B-cell depleting therapy within 12 months",
        "Pregnancy or breastfeeding",
        "Live vaccine within 4 weeks",
        "Hepatitis B or C, HIV infection",
    ],
    age_range="18-70",
    region="Global",
    number_of_sites=110,
    background="Lupus nephritis affects 40-50% of SLE patients and leads to ESKD in 10-30%. B-cell depletion targets the autoantibody-producing cells driving renal inflammation.",
    prior_therapy_allowed=True
)


# Collection of all sample protocols
SAMPLE_PROTOCOLS = [
    ONCOLOGY_PHASE3,
    CARDIOVASCULAR_PHASE2,
    RHEUMATOLOGY_PHASE2,
    NEUROLOGY_PHASE2,
    DIABETES_PHASE3,
    GASTRO_IBD_PHASE3,
    DERMATOLOGY_PSORIASIS_PHASE3,
    PSYCHIATRY_DEPRESSION_PHASE3,
    INFECTIOUS_HIV_PHASE2,
    HEMATOLOGY_ANEMIA_PHASE3,
    PULMONARY_ASTHMA_PHASE3,
    ENDOCRINE_THYROID_PHASE2,
    RENAL_CKD_PHASE3,
    HEPATOLOGY_NASH_PHASE3,
    IMMUNOLOGY_LUPUS_PHASE3,
]
