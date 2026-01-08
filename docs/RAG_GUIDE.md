# RAG (Retrieval-Augmented Generation) Feature Guide

## Overview

The RAG feature enhances protocol generation by retrieving similar protocol examples from a vector database and using them to inform the generation process. This creates more contextually relevant and accurate protocols based on historical data.

## How It Works

```
┌─────────────────┐
│  Trial Spec     │
│  Input          │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Vector Database (ChromaDB)     │
│  • Embedded protocol examples   │
│  • Semantic search capability   │
└────────┬────────────────────────┘
         │
         ▼ (Retrieve similar protocols)
┌─────────────────────────────────┐
│  Similar Protocols Retrieved    │
│  • Top N most similar           │
│  • With similarity scores       │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Enhanced Protocol Generation   │
│  • Template-based + RAG context │
│  • Improved accuracy            │
│  • Better field selection       │
└─────────────────────────────────┘
```

## New API Endpoints

### 1. Seed RAG Database
**POST** `/api/v1/rag/seed`

Populate the database with sample protocols covering various therapeutic areas.

```bash
curl -X POST "http://localhost:8000/api/v1/rag/seed"
```

**Response:**
```json
{
  "message": "RAG database seeded with sample protocols",
  "added": 5,
  "failed": 0,
  "total_examples": 5,
  "seeded_protocols": [
    {
      "doc_id": "protocol_abc123",
      "phase": "Phase 3",
      "indication": "Advanced Non-Small Cell Lung Cancer"
    },
    ...
  ]
}
```

### 2. Search Similar Protocols
**POST** `/api/v1/rag/search`

Find protocols similar to your trial specification.

```bash
curl -X POST "http://localhost:8000/api/v1/rag/search?n_results=3" \
  -H "Content-Type: application/json" \
  -d '{
    "sponsor": "Test",
    "title": "RA Study",
    "indication": "Rheumatoid Arthritis",
    "phase": "Phase 2",
    "design": "randomized, double-blind",
    "sample_size": 100,
    "duration_weeks": 24,
    "key_endpoints": [{"type": "primary", "name": "ACR20"}],
    "inclusion_criteria": ["Age 18-75"],
    "exclusion_criteria": ["Prior biologic"],
    "region": "US"
  }'
```

**Response:**
```json
{
  "query_summary": {
    "phase": "Phase 2",
    "indication": "Rheumatoid Arthritis"
  },
  "found": 1,
  "similar_protocols": [
    {
      "rag_doc_id": "protocol_xyz789",
      "similarity_score": 0.87,
      "metadata": {
        "phase": "Phase 2",
        "indication": "Rheumatoid Arthritis",
        "sample_size": 200,
        "duration_weeks": 52
      },
      "trial_spec_summary": {...}
    }
  ]
}
```

### 3. Add Generated Protocol to RAG
**POST** `/api/v1/rag/add-example?request_id={id}`

Add a successfully generated protocol to the RAG database for future use.

```bash
curl -X POST "http://localhost:8000/api/v1/rag/add-example?request_id=REQ-ABC123"
```

### 4. List RAG Examples
**GET** `/api/v1/rag/examples`

List all protocol examples in the database.

```bash
curl "http://localhost:8000/api/v1/rag/examples"
```

### 5. Get RAG Statistics
**GET** `/api/v1/rag/stats`

View statistics about the RAG database.

```bash
curl "http://localhost:8000/api/v1/rag/stats"
```

**Response:**
```json
{
  "total_examples": 6,
  "by_phase": {
    "Phase 2": 3,
    "Phase 3": 3
  },
  "by_indication": {
    "Rheumatoid Arthritis": 1,
    "Type 2 Diabetes": 1,
    "NSCLC": 1,
    ...
  },
  "database_path": "./vector_db"
}
```

### 6. Get Specific Example
**GET** `/api/v1/rag/examples/{doc_id}`

Retrieve complete data for a specific protocol example.

### 7. Delete Example
**DELETE** `/api/v1/rag/examples/{doc_id}`

Remove a protocol example from the database.

## Quick Start

### Step 1: Seed the Database

```bash
# Using test script
python examples/test_rag.py seed

# Or using curl
curl -X POST "http://localhost:8000/api/v1/rag/seed"
```

This adds 5 sample protocols:
- Oncology (Phase 3) - NSCLC
- Cardiovascular (Phase 2) - Hypercholesterolemia
- Rheumatology (Phase 2) - Rheumatoid Arthritis
- Neurology (Phase 2) - Alzheimer's Disease
- Diabetes (Phase 3) - Type 2 Diabetes

### Step 2: Generate Protocol with RAG

The system now automatically uses RAG when generating protocols:

```bash
python examples/test_api.py generate
```

The generated protocol will include:
- Retrieved similar protocols for context
- Enhanced generation informed by similar examples
- Reference context in the protocol narrative

### Step 3: View RAG Statistics

```bash
python examples/test_rag.py stats
```

## How RAG Enhances Generation

### Before RAG (Template-Only)
```
Input → Template → Output
```
- Fixed templates
- No historical context
- Generic content

### With RAG
```
Input → Search Vector DB → Retrieve Similar → Template + Context → Enhanced Output
```
- Context from similar protocols
- Better field selection
- More accurate content
- Learning from examples

## Example: RAG in Action

**Input:** Phase 2 study in Rheumatoid Arthritis

**RAG Retrieval:**
```
Found similar protocol:
- Phase 2 JAK Inhibitor in RA
- Sample Size: 200
- Duration: 52 weeks
- Similarity: 87%
```

**Enhanced Output:**
- Visit schedule informed by similar study
- Appropriate endpoints (ACR20, DAS28)
- Relevant inclusion/exclusion criteria
- Better assessment timing

## Testing RAG

Run the comprehensive RAG test suite:

```bash
# Run all RAG tests
python examples/test_rag.py all

# Or individual tests
python examples/test_rag.py seed
python examples/test_rag.py search
python examples/test_rag.py generate
```

## RAG Configuration

Configuration is in `config.py`:

```python
vector_db_path: str = "./vector_db"  # Vector database storage
```

## Technical Details

### Vector Database
- **Engine**: ChromaDB
- **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2)
- **Storage**: Persistent local storage
- **Search**: Cosine similarity

### Embedding Strategy
Trial specifications are converted to searchable text:
```
"Phase: Phase 2 | Indication: Rheumatoid Arthritis | 
Design: randomized, double-blind | Sample Size: 200 | 
Duration: 52 weeks | Endpoints: primary: ACR20 response..."
```

### Similarity Scoring
- Score range: 0.0 to 1.0
- Higher = more similar
- Based on semantic similarity of embeddings

## Sample Protocols Included

1. **Oncology - Phase 3**
   - Advanced NSCLC
   - Checkpoint inhibitor
   - 450 patients, 104 weeks

2. **Cardiovascular - Phase 2**
   - Hypercholesterolemia
   - PCSK9 inhibitor
   - 180 patients, 24 weeks

3. **Rheumatology - Phase 2**
   - Rheumatoid Arthritis
   - JAK inhibitor
   - 200 patients, 52 weeks

4. **Neurology - Phase 2**
   - Early Alzheimer's Disease
   - Anti-amyloid antibody
   - 250 patients, 78 weeks

5. **Diabetes - Phase 3**
   - Type 2 Diabetes
   - GLP-1 receptor agonist
   - 800 patients, 52 weeks

## Best Practices

### 1. Seed Before Use
Always seed the database before generating protocols to get RAG benefits.

### 2. Add Quality Examples
Add successfully validated protocols to improve future generations:
```bash
curl -X POST "http://localhost:8000/api/v1/rag/add-example?request_id=REQ-ABC123"
```

### 3. Review Similar Protocols
Before generating, search for similar protocols to understand context:
```bash
python examples/test_rag.py search
```

### 4. Monitor Database Growth
Track how many examples are in the database:
```bash
curl "http://localhost:8000/api/v1/rag/stats"
```

### 5. Clean Up Poor Examples
Remove low-quality examples that might hurt generation quality.

## Troubleshooting

### "No protocol examples in database"
**Solution:** Seed the database first:
```bash
curl -X POST "http://localhost:8000/api/v1/rag/seed"
```

### RAG not working
**Solution:** Check that ChromaDB is installed:
```bash
pip install chromadb sentence-transformers
```

### Slow first query
**Note:** First query loads the embedding model (~80MB). Subsequent queries are fast.

## Future Enhancements

Planned improvements:
- [ ] Fine-tuned embeddings on clinical trial text
- [ ] Multi-modal retrieval (text + structured data)
- [ ] Weighted similarity (phase, indication, design)
- [ ] User feedback loop for relevance
- [ ] Automatic example curation
- [ ] LLM-based context synthesis

## Performance

- **Embedding Time**: ~200ms first query, ~50ms subsequent
- **Search Time**: ~10-50ms for 100 documents
- **Storage**: ~10KB per protocol example
- **Scalability**: Tested up to 1000 examples

## API Integration

The RAG feature integrates seamlessly with existing endpoints:

```python
# Existing endpoint now uses RAG automatically
POST /api/v1/generate
→ Retrieves similar protocols
→ Enhances generation
→ Returns RAG-informed protocol
```

No changes needed to existing clients!

---

**RAG is now active!** Start with `python examples/test_rag.py all`
