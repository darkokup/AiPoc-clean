# AI-Generated Clinical Trial Module - Proof of Concept

> ** SECURITY NOTICE**: This project has been cleaned of secrets. Before using:
> 1. Copy .env.example to .env and add your own keys
> 2. Generate a secure SECRET_KEY (see [SETUP.md](SETUP.md))
> 3. Read [SECURITY.md](SECURITY.md) for production deployment guidelines



A FastAPI-based system for generating complete clinical trial protocols and EDC configurations from high-level trial specifications. This PoC implements **RAG (Retrieval-Augmented Generation) + LLM-enhanced generation**, clinical rules validation, and multi-format export capabilities.

## Features

✅ **AI-Enhanced Protocol Generation**
- **RAG Integration**: Learns from 1,159+ real clinical trial protocols
- **LLM Integration**: OpenAI GPT-4 for professional content generation
- **Graceful Fallback**: Works without API keys (RAG-only mode)
- Structured protocol JSON generation
- Human-readable narrative protocol text
- Automatic visit schedule creation
- Statistical plan and safety monitoring sections

✅ **🆕 RAG (Retrieval-Augmented Generation)**
- Vector database (ChromaDB) with 1,159+ real protocols
- Semantic search for similar protocols
- Context-aware generation using historical data
- Continuous learning from new protocols
- Import from ClinicalTrials.gov

✅ **🆕 LLM Enhancement (OpenAI GPT-4)**
- AI-generated objectives and endpoints
- Professional, regulatory-compliant language
- Indication-specific inclusion/exclusion criteria
- Enhanced protocol sections with RAG context
- **✨ NEW: Additional Instructions** - Customize ALL sections with natural language prompts
  - Control study design elements (e.g., "Include telemedicine visits")
  - Specify population requirements (e.g., "Target elderly age 65+")
  - Add biomarker/diagnostic needs (e.g., "Require PD-L1 testing")
  - Include safety measures (e.g., "COVID-19 vaccination required")
  - Customize assessments, visits, and CRF forms
- **Optional**: Works perfectly without LLM in RAG-only mode

✅ **CRF/EDC Configuration**
- CDASH-compliant CRF schema generation
- Visit-form assignments
- Data type validation rules
- SDTM variable mappings

✅ **Clinical Rules Validation**
- Sample size validation by phase
- Endpoint requirements checking
- Eligibility criteria validation
- CDASH compliance verification

✅ **Multi-Format Export**
- CDISC ODM XML
- FHIR JSON (ResearchStudy, Questionnaire)
- CSV data dictionary
- Complete JSON export

## Generation Modes

The system supports three modes:

1. **RAG + LLM (Default)** ⭐ - Highest quality, uses vector database + OpenAI GPT-4
2. **RAG-Only** - Good quality, uses vector database only (no API costs)
3. **Template-Only** - Fast, uses predefined templates only

See [CONFIGURATION.md](CONFIGURATION.md) for details.

## Quick Start

### Prerequisites

- Python 3.9+
- pip
- *Optional*: OpenAI API key for LLM features

### Installation

1. Clone or download the project

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create environment file:
```bash
copy .env.example .env

# Optional: Add OpenAI API key for LLM features
# Edit .env and add: OPENAI_API_KEY=sk-your-key-here
```

4. Seed the RAG database (first time only):
```bash
python examples/seed_rag_direct.py
```

### Running the Application

**Option 1: Quick Launch (Opens Web UI)**
```bash
python launch_web.py
```
This will start the server and open the web interface in your browser.

**Option 2: Command Line**
```bash
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at:
- **Web UI**: http://localhost:8000/ 🆕
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API**: http://localhost:8000/api/v1/

## Web Interface 🆕

A beautiful, user-friendly web interface is now available!

### Features:
- ✨ Interactive protocol generation form
- 🔍 RAG similarity search
- 📊 Real-time RAG status monitoring
- 📥 Download protocols (JSON, ODM XML, FHIR JSON)
- 🌐 Complete API documentation

### Quick Start:
1. Start the server: `python launch_web.py`
2. Web UI opens automatically at http://localhost:8000/
3. Fill in the protocol form and click "Generate Protocol"
4. Download or export your protocol in multiple formats

**For detailed web interface documentation, see [web/README.md](web/README.md)**

### 🆕 Seed RAG Database (Recommended First Step)

```bash
# Populate vector database with sample protocols
curl -X POST "http://localhost:8000/api/v1/rag/seed"

# Or using the test script
python examples/test_rag.py seed
```

This adds 5 diverse sample protocols (Oncology, Cardiovascular, Rheumatology, Neurology, Diabetes) to the vector database for enhanced generation.

**For complete RAG documentation, see [RAG_GUIDE.md](RAG_GUIDE.md)**

## API Usage

### Core Endpoints

### 1. Generate Protocol

**POST** `/api/v1/generate`

Generate a complete clinical trial protocol and CRF schema from trial specifications. **Now uses RAG automatically** to retrieve similar protocols for enhanced generation.

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d @examples/example_request.json
```

See `examples/example_request.json` for a complete example.

**✨ NEW: Additional Instructions Field**

You can now provide custom instructions to guide AI generation across ALL sections of the protocol:

```json
{
  "sponsor": "BioTech Inc",
  "title": "Phase II Study...",
  "indication": "Non-Small Cell Lung Cancer",
  "phase": "PHASE_II",
  "additional_instructions": "Target elderly population age 65+. Require PD-L1 biomarker testing. Include telemedicine visits for remote monitoring. Use geriatric assessment tools."
}
```

**What gets customized:**
- ✓ Objectives (primary and secondary)
- ✓ Inclusion & Exclusion Criteria
- ✓ Study Design description
- ✓ Visit Schedule
- ✓ Clinical Assessments
- ✓ CRF Forms and fields

**Use cases:**
- COVID-19 safety measures
- Specific population requirements (elderly, pediatric, pregnant)
- Biomarker or diagnostic requirements
- Remote/telemedicine considerations
- Regulatory-specific requirements
- Special data collection needs

**Response includes:**
- `request_id`: Unique identifier for retrieval
- `protocol_structured`: Full structured protocol JSON
- `protocol_text`: Human-readable protocol narrative
- `crf_schema`: Complete CRF configuration
- `validation_status`: Validation results
- `overall_confidence`: Quality score

### 2. Validate Trial Spec

**POST** `/api/v1/validate`

Validate a trial specification without generating the full protocol.

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/validate" \
  -H "Content-Type: application/json" \
  -d @examples/example_request.json
```

### 3. Export Protocol

**POST** `/api/v1/export`

Export a generated protocol to various formats.

**Example (ODM XML):**
```bash
curl -X POST "http://localhost:8000/api/v1/export" \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "REQ-ABC123DEF456",
    "format": "odm_xml",
    "include_crf": true,
    "include_protocol": true
  }'
```

**Supported Formats:**
- `odm_xml` - CDISC ODM XML
- `fhir_json` - FHIR JSON Bundle
- `csv` - CSV Data Dictionary
- `json` - Complete JSON export

### 4. Retrieve Protocol

**GET** `/api/v1/protocols/{request_id}`

Retrieve a previously generated protocol.

### 5. List All Protocols

**GET** `/api/v1/protocols`

Get a summary of all generated protocols.

### 🆕 RAG Endpoints

### 6. Seed RAG Database
**POST** `/api/v1/rag/seed` - Populate database with sample protocols

### 7. Search Similar Protocols
**POST** `/api/v1/rag/search` - Find protocols similar to a trial spec

### 8. Add Protocol to RAG
**POST** `/api/v1/rag/add-example` - Add generated protocol to database

### 9. RAG Statistics
**GET** `/api/v1/rag/stats` - View database statistics

### 10. List/Get/Delete RAG Examples
**GET** `/api/v1/rag/examples` - List all examples  
**GET** `/api/v1/rag/examples/{doc_id}` - Get specific example  
**DELETE** `/api/v1/rag/examples/{doc_id}` - Delete example

**📖 See [RAG_GUIDE.md](RAG_GUIDE.md) for complete RAG documentation**

## Project Structure

```
AiPoc/
├── main.py                      # FastAPI application entry point
├── config.py                    # Application configuration
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── RAG_GUIDE.md                 # 🆕 RAG feature documentation
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py           # Pydantic data models
│   └── services/
│       ├── __init__.py
│       ├── generator.py         # Protocol & CRF generators (RAG-enhanced)
│       ├── validator.py         # Clinical rules validation
│       ├── exporter.py          # Multi-format exporters
│       ├── rag_service.py       # 🆕 RAG vector database service
│       └── sample_protocols.py  # 🆕 Sample protocol data
├── examples/
│   ├── example_request.json     # Sample trial spec
│   ├── example_response.json    # Sample generated output
│   ├── test_api.py              # API testing script
│   └── test_rag.py              # 🆕 RAG testing script
├── vector_db/                   # 🆕 ChromaDB storage (created on first use)
└── README.md
```

## Architecture Overview

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│         FastAPI Application                      │
│  ┌─────────────────────────────────────────┐    │
│  │   API Endpoints                         │    │
│  │  - Generate (RAG-enhanced)              │    │
│  │  - Validate                             │    │
│  │  - Export                               │    │
│  │  - RAG Management (8 endpoints)  🆕     │    │
│  └────────────┬────────────────────────────┘    │
│               ▼                                  │
│  ┌─────────────────────────────────────────┐    │
│  │   Orchestration Layer                   │    │
│  └────┬────────────────────────────────────┘    │
│       │                                          │
│       ▼                                          │
│  ┌─────────────────┐    ┌──────────────────┐    │
│  │   Generators    │◄───┤  RAG Service 🆕  │    │
│  │  - Protocol     │    │  - ChromaDB      │    │
│  │  - CRF          │    │  - Embeddings    │    │
│  └────┬────────────┘    │  - Similarity    │    │
│       │                 └──────────────────┘    │
│       ▼                                          │
│  ┌─────────────────┐                            │
│  │   Validators    │                            │
│  │  - Rules Engine │                            │
│  │  - CDASH Check  │                            │
│  └────┬────────────┘                            │
│       │                                          │
│       ▼                                          │
│  ┌─────────────────┐                            │
│  │   Exporters     │                            │
│  │  - ODM XML      │                            │
│  │  - FHIR JSON    │                            │
│  │  - CSV          │                            │
│  └─────────────────┘                            │
└──────────────────────────────────────────────────┘
```

## Data Models

### TrialSpecInput
Input specification for trial generation:
- Basic info: sponsor, title, indication, phase
- Design: study design, sample size, duration
- Endpoints: primary, secondary, exploratory
- Eligibility: inclusion/exclusion criteria
- Geography: region, number of sites

### ProtocolStructured
Complete structured protocol:
- Metadata: protocol ID, version, timestamps
- Design details: arms, objectives, endpoints
- Visit schedule and assessments
- Statistical plan
- Safety monitoring
- Protocol sections with provenance

### CRFSchema
EDC configuration:
- Forms with fields and data types
- Visit definitions and form assignments
- CDASH/SDTM mappings
- Validation rules

## Validation Rules

The system validates:
- **Sample Size**: Minimum by phase (Phase 1: 20, Phase 2: 40, Phase 3: 100)
- **Duration**: Minimum 4 weeks
- **Endpoints**: At least 1 primary, max 3 primary
- **Criteria**: Minimum inclusion/exclusion criteria
- **Visit Schedule**: Must include baseline
- **CRF Forms**: Required forms (Demographics, Adverse Events)
- **CDASH Compliance**: Variable mappings

## Standards Compliance

### CDISC Standards
- **CDASH**: Clinical Data Acquisition Standards Harmonization
- **ODM**: Operational Data Model (XML export)
- **SDTM**: Study Data Tabulation Model (variable mappings)

### FHIR Resources
- **ResearchStudy**: Protocol metadata
- **Questionnaire**: CRF forms

## Development Roadmap

### Phase 1: PoC (Current) ✅
✅ Template-based generation  
✅ Clinical rules validation  
✅ Multi-format export  
✅ REST API  

### Phase 2: ML Integration (In Progress)
✅ RAG for protocol retrieval 🆕  
✅ Vector database integration (ChromaDB) 🆕  
- [ ] Fine-tuned seq2seq models (T5/BART)
- [ ] Confidence scoring improvements
- [ ] LLM integration for generation

### Phase 3: Advanced Features
- [ ] Interactive protocol editing UI
- [ ] Version control and audit trails
- [ ] Collaboration features
- [ ] Advanced statistical plan generation
- [ ] Integration with EDC systems (REDCap, Medidata)
- [ ] RAG refinement with user feedback

### Phase 4: Production
- [ ] Database persistence (PostgreSQL)
- [ ] Authentication & authorization
- [ ] RBAC (Role-Based Access Control)
- [ ] 21 CFR Part 11 compliance
- [ ] Comprehensive logging & monitoring
- [ ] Model retraining pipelines

## Example Use Cases

### 1. Phase 2 Oncology Trial
Generate a complete protocol for a randomized, double-blind study evaluating a novel therapy in cancer patients.

### 2. Phase 3 Cardiovascular Study
Create multi-center trial protocol with extensive safety monitoring and interim analyses.

### 3. Rare Disease Study
Generate protocol with adaptive design and flexible enrollment criteria.

### 4. Bioequivalence Study
Create Phase 1 crossover study with PK endpoints.

## Testing

### Basic API Testing
```bash
# Validate trial spec
python examples/test_api.py validate

# Generate protocol
python examples/test_api.py generate

# Export to ODM XML
python examples/test_api.py export
```

### 🆕 RAG Testing
```bash
# Run all RAG tests
python examples/test_rag.py all

# Or individual tests
python examples/test_rag.py seed      # Seed database
python examples/test_rag.py search    # Search similar protocols
python examples/test_rag.py generate  # RAG-enhanced generation
python examples/test_rag.py stats     # View database stats
```

**See [docs/RAG_GUIDE.md](docs/RAG_GUIDE.md) for complete testing documentation**

## 📚 Documentation

All documentation has been organized in the `docs/` folder:

- **[docs/README.md](docs/README.md)** - Complete documentation index
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide
- **[INSTALL.md](INSTALL.md)** - Installation instructions
- **[docs/TESTING_SUMMARY.md](docs/TESTING_SUMMARY.md)** - Test coverage summary
- **[tests/README.md](tests/README.md)** - Testing guide
- **[docs/DEBUGGING.md](docs/DEBUGGING.md)** - Debugging strategies
- **[docs/LLM_INTEGRATION_GUIDE.md](docs/LLM_INTEGRATION_GUIDE.md)** - LLM integration
- **[docs/RAG_GUIDE.md](docs/RAG_GUIDE.md)** - RAG usage guide
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture
- **[docs/ROADMAP.md](docs/ROADMAP.md)** - Future plans

See the [documentation index](docs/README.md) for all available guides.

## Contributing

This is a Proof of Concept. For production use:
1. ✅ Add comprehensive unit tests (43+ tests added!)
2. Implement database persistence
3. Add authentication/authorization
4. Configure proper CORS policies
5. Add rate limiting
6. Implement proper error handling
7. Add comprehensive logging
8. Set up monitoring and alerting

## License

This is a Proof of Concept for demonstration purposes.

## Contact

For questions about clinical trial protocol generation or EDC configuration, consult with:
- Clinical operations team
- Biostatisticians
- Data management
- Regulatory affairs

## References

- [CDISC Standards](https://www.cdisc.org/)
- [FHIR Clinical Research](https://www.hl7.org/fhir/clinicalresearch-module.html)
- [ClinicalTrials.gov](https://clinicaltrials.gov/)
- [FDA Guidance on Clinical Trials](https://www.fda.gov/regulatory-information/search-fda-guidance-documents)
