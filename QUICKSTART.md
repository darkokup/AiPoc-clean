# Quick Start Guide

## Getting Started in 5 Minutes

### 1. Install Dependencies

```powershell
# Create a virtual environment (recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Server

```powershell
python main.py
```

The API will start at `http://localhost:8000`

### 3. Open Interactive Docs

Navigate to: **http://localhost:8000/docs**

This provides a Swagger UI where you can test all endpoints interactively.

### 4. Test the API

Option A: **Use the interactive docs** (easiest)
- Go to http://localhost:8000/docs
- Click on `POST /api/v1/generate`
- Click "Try it out"
- Use the example request body
- Click "Execute"

Option B: **Use the test script**

```powershell
# Run all tests
python examples/test_api.py all

# Or run individual tests
python examples/test_api.py generate
python examples/test_api.py export
```

Option C: **Use curl**

```powershell
# Generate protocol
curl -X POST "http://localhost:8000/api/v1/generate" `
  -H "Content-Type: application/json" `
  -d "@examples/example_request.json"
```

## Example Request

Minimal example:

```json
{
  "sponsor": "Acme Pharma",
  "title": "Phase II Study of Drug X",
  "indication": "Disease Y",
  "phase": "Phase 2",
  "design": "randomized, double-blind, placebo-controlled",
  "sample_size": 100,
  "duration_weeks": 24,
  "key_endpoints": [
    {
      "type": "primary",
      "name": "Change in symptom score at week 24"
    }
  ],
  "inclusion_criteria": [
    "Age 18-65",
    "Confirmed diagnosis of Disease Y"
  ],
  "exclusion_criteria": [
    "Severe comorbidities",
    "Pregnancy"
  ],
  "region": "US/EU"
}
```

## What You'll Get

The API returns:
- ✅ **Structured Protocol** (JSON with all sections)
- ✅ **Narrative Protocol** (Human-readable text)
- ✅ **CRF Schema** (Forms, fields, visit schedule)
- ✅ **Validation Results** (Errors, warnings, compliance checks)
- ✅ **Export Options** (ODM XML, FHIR JSON, CSV)

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/generate` | POST | Generate complete protocol + CRF |
| `/api/v1/validate` | POST | Validate trial spec only |
| `/api/v1/export` | POST | Export to ODM/FHIR/CSV |
| `/api/v1/protocols` | GET | List all generated protocols |
| `/api/v1/protocols/{id}` | GET | Retrieve specific protocol |

## Next Steps

1. **Customize the example** - Edit `examples/example_request.json`
2. **Generate your protocol** - Run the generate endpoint
3. **Export to formats** - Try ODM XML, FHIR JSON, or CSV
4. **Review validation** - Check warnings and suggestions
5. **Iterate** - Modify and regenerate as needed

## Troubleshooting

**Port already in use?**
```powershell
# Change port in .env or run with custom port
uvicorn main:app --port 8001
```

**Import errors?**
```powershell
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

**Database errors?**
```powershell
# This PoC uses in-memory storage, no database setup needed
```

## Key Features to Try

1. **Multi-arm studies** - Add multiple treatment arms
2. **Complex endpoints** - Primary, secondary, exploratory
3. **CDASH compliance** - CRF fields mapped to CDASH variables
4. **Visit schedules** - Auto-generated based on duration
5. **Export formats** - CDISC ODM XML, FHIR, CSV data dictionary

## Production Considerations

For production use, you'll need to:
- [ ] Set up PostgreSQL database
- [ ] Configure authentication (OAuth2/JWT)
- [ ] Add HTTPS/TLS
- [ ] Set up proper logging
- [ ] Configure CORS properly
- [ ] Add rate limiting
- [ ] Implement audit trails
- [ ] Set up monitoring

See README.md for full documentation.
