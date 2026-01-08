# Project Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Applications                       │
│  (Web UI, EDC Systems, Clinical Operations Tools)              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway / Load Balancer                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       FastAPI Application                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Endpoints Layer                    │  │
│  │  • /api/v1/generate  • /api/v1/validate                  │  │
│  │  • /api/v1/export    • /api/v1/protocols                 │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                      │
│  ┌────────────────────────▼─────────────────────────────────┐  │
│  │              Orchestration & Business Logic              │  │
│  │  • Request validation  • Error handling                  │  │
│  │  • Service coordination • Response formatting            │  │
│  └────────────────────────┬─────────────────────────────────┘  │
└───────────────────────────┼──────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  Generator   │   │  Validator   │   │   Exporter   │
│   Service    │   │   Service    │   │   Service    │
├──────────────┤   ├──────────────┤   ├──────────────┤
│ • Protocol   │   │ • Trial Spec │   │ • ODM XML    │
│   Generator  │   │   Validation │   │ • FHIR JSON  │
│ • CRF        │   │ • Protocol   │   │ • CSV        │
│   Generator  │   │   Validation │   │ • JSON       │
│ • Narrative  │   │ • CRF Schema │   │              │
│   Generator  │   │   Validation │   │              │
│              │   │ • CDASH      │   │              │
│              │   │   Compliance │   │              │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
    ┌──────────────────┐    ┌──────────────────┐
    │   Data Layer     │    │  External APIs   │
    ├──────────────────┤    ├──────────────────┤
    │ • Templates      │    │ • LLM Services   │
    │ • Rules Engine   │    │   (Future)       │
    │ • Vocabularies   │    │ • Vector DB      │
    │ • Storage        │    │   (Future RAG)   │
    └──────────────────┘    └──────────────────┘
```

## Component Details

### 1. API Layer (`main.py`)
- **FastAPI application** with automatic OpenAPI documentation
- **CORS middleware** for cross-origin requests
- **RESTful endpoints** following best practices
- **Error handling** with appropriate HTTP status codes
- **Request/Response validation** via Pydantic

### 2. Data Models (`app/models/schemas.py`)
- **Pydantic models** for type safety and validation
- **TrialSpecInput**: Input specification for trial generation
- **ProtocolStructured**: Complete protocol representation
- **CRFSchema**: EDC configuration with forms and fields
- **GenerationResult**: Complete output package
- **ValidationResult**: Validation status and messages

### 3. Generator Service (`app/services/generator.py`)

#### ProtocolTemplateGenerator
- Generates structured protocol JSON
- Creates human-readable narrative text
- Builds visit schedules based on duration
- Generates assessments and statistical plans
- Template-based with rule-driven logic

#### CRFGenerator
- Creates CDASH-compliant CRF schemas
- Generates standard forms (Demographics, Vitals, AE)
- Maps fields to CDASH/SDTM variables
- Assigns forms to visits
- Adds validation rules

### 4. Validator Service (`app/services/validator.py`)

#### ClinicalRulesValidator
Enforces clinical trial best practices:
- **Sample size rules**: Phase-appropriate minimums
- **Endpoint requirements**: Primary endpoint required
- **Eligibility criteria**: Minimum inclusion/exclusion
- **Visit schedule**: Baseline visit required
- **CDASH compliance**: Variable mapping checks
- **Field validation**: Data type rules

### 5. Exporter Service (`app/services/exporter.py`)

#### ProtocolExporter
Supports multiple formats:
- **ODM XML**: CDISC Operational Data Model v1.3
- **FHIR JSON**: ResearchStudy and Questionnaire resources
- **CSV**: Data dictionary for EDC import
- **JSON**: Complete structured export

## Data Flow

### Protocol Generation Flow

```
1. Client Request
   └─> POST /api/v1/generate with TrialSpecInput

2. Input Validation
   └─> ClinicalRulesValidator.validate_trial_spec()
   └─> Returns ValidationResult

3. Protocol Generation
   └─> ProtocolTemplateGenerator.generate_structured_protocol()
   └─> Creates ProtocolStructured object
   └─> ProtocolTemplateGenerator.generate_protocol_narrative()
   └─> Creates human-readable text

4. CRF Generation
   └─> CRFGenerator.generate_crf_schema()
   └─> Creates forms, fields, visits
   └─> Maps to CDASH/SDTM

5. Validation
   └─> Validate protocol structure
   └─> Validate CRF schema
   └─> Combine messages

6. Result Assembly
   └─> Create GenerationResult
   └─> Calculate confidence scores
   └─> Store in memory (or database)

7. Response
   └─> Return complete GenerationResult to client
```

### Export Flow

```
1. Client Request
   └─> POST /api/v1/export with ExportRequest

2. Retrieve Protocol
   └─> Fetch from storage by request_id

3. Format Conversion
   └─> ProtocolExporter.export()
   └─> Convert to requested format
   └─> ODM XML: Create XML tree with CDISC structure
   └─> FHIR JSON: Create resource bundle
   └─> CSV: Generate data dictionary
   └─> JSON: Serialize complete data

4. Response
   └─> Return formatted content with metadata
```

## Technology Stack

### Core Framework
- **FastAPI**: Modern, fast web framework
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server

### Data Processing
- **Python standard library**: XML generation, JSON handling
- **datetime**: Timestamp management

### Future Enhancements (Phase 2+)
- **TensorFlow/Keras**: ML model serving
- **Transformers**: T5/BART for text generation
- **ChromaDB/Milvus**: Vector database for RAG
- **SQLAlchemy**: Database ORM
- **PostgreSQL**: Persistent storage

## Security Considerations

### Current PoC
- ✓ Input validation via Pydantic
- ✓ CORS middleware (configure for production)
- ✓ Environment-based configuration

### Production Requirements
- [ ] Authentication (OAuth2/JWT)
- [ ] Authorization (RBAC)
- [ ] HTTPS/TLS encryption
- [ ] API rate limiting
- [ ] Input sanitization
- [ ] Audit logging
- [ ] Data encryption at rest
- [ ] 21 CFR Part 11 compliance

## Scalability

### Current Architecture
- In-memory storage (suitable for PoC/demo)
- Single-instance deployment
- Synchronous processing

### Production Architecture
```
┌─────────────────┐
│  Load Balancer  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───┐
│ API  │  │ API  │  (Multiple instances)
│ Pod  │  │ Pod  │
└───┬──┘  └──┬───┘
    │        │
    └────┬───┘
         ▼
┌─────────────────┐
│   PostgreSQL    │
│   (Primary +    │
│    Replicas)    │
└─────────────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───┐
│Vector│  │Object│
│  DB  │  │Store │
└──────┘  └──────┘
```

## Extension Points

### Adding New Validators
```python
# In app/services/validator.py
def validate_custom_rule(self, spec: TrialSpecInput) -> ValidationResult:
    # Add custom validation logic
    pass
```

### Adding New Export Formats
```python
# In app/services/exporter.py
def _export_custom_format(self, protocol, crf_schema):
    # Add new export format
    pass
```

### Adding ML Models
```python
# Future: app/services/ml_generator.py
class MLProtocolGenerator:
    def __init__(self, model_path: str):
        self.model = load_model(model_path)
    
    def generate_with_ml(self, spec: TrialSpecInput):
        # ML-based generation
        pass
```

## Monitoring and Observability

### Recommended Additions
- **Logging**: Structured logging with correlation IDs
- **Metrics**: Prometheus metrics for request rates, latencies
- **Tracing**: OpenTelemetry for distributed tracing
- **Health Checks**: Liveness and readiness probes
- **Dashboards**: Grafana dashboards for visualization

## Testing Strategy

### Current Tests
- Unit tests for core components
- API endpoint tests
- Model validation tests

### Production Testing
- [ ] Integration tests
- [ ] Load testing
- [ ] Security testing
- [ ] Compliance testing
- [ ] User acceptance testing
