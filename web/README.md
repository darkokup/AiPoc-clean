# Web Interface for Clinical Trial Protocol Generator

This web interface provides a user-friendly way to interact with the AI Clinical Trial Protocol Generator API with RAG capabilities.

## Features

✨ **Protocol Generator**
- Interactive form for creating trial specifications
- Real-time validation
- RAG status indicator
- Download generated protocols
- Export to multiple formats (ODM XML, FHIR JSON)

🔍 **RAG Similarity Search**
- Search for similar protocols in the vector database
- View similarity scores
- Browse protocol examples

🌐 **API Documentation**
- Complete list of available endpoints
- Quick reference for API integration

## Quick Start

### 1. Start the Server

Make sure the FastAPI server is running:

```bash
python main.py
```

The server will start on `http://localhost:8000`

### 2. Access the Web Interface

Open your browser and navigate to:

**http://localhost:8000/**

Or directly to the UI:

**http://localhost:8000/ui/**

### 3. Alternative: Interactive API Docs

FastAPI provides automatic interactive documentation:

**http://localhost:8000/docs** - Swagger UI  
**http://localhost:8000/redoc** - ReDoc

## Using the Web Interface

### Generate a Protocol

1. Click on the **"📝 Generate Protocol"** tab
2. Fill in the required fields:
   - **Sponsor**: Organization conducting the trial
   - **Protocol Title**: Full title of the study
   - **Indication**: Disease or condition being studied
   - **Phase**: Clinical trial phase (1-4)
   - **Study Design**: e.g., "randomized, double-blind, placebo-controlled"
   - **Sample Size**: Number of participants
   - **Duration**: Study duration in weeks
   - **Primary Endpoint**: Main outcome measure
   - **Inclusion/Exclusion Criteria**: One per line

3. Click **"🚀 Generate Protocol"**

4. The system will:
   - Search the RAG vector database for similar protocols
   - Generate a new protocol using templates + RAG context
   - Validate against clinical rules
   - Display results with confidence score

5. Download or export the protocol:
   - **Download Full Protocol**: JSON with complete data
   - **Export ODM XML**: CDISC ODM format
   - **Export FHIR JSON**: FHIR ResearchStudy + Questionnaire

### Search Similar Protocols

1. Click on the **"🔍 RAG Search"** tab
2. Enter search criteria:
   - **Indication**: Disease or condition
   - **Phase**: Trial phase (optional)
   - **Results**: Number of similar protocols to retrieve (1-10)

3. Click **"🔍 Search Similar Protocols"**

4. View results with:
   - Similarity scores
   - Protocol metadata
   - Sample sizes and durations

### View API Endpoints

Click on the **"🌐 API Endpoints"** tab to see:
- All available API endpoints
- HTTP methods (GET, POST, DELETE)
- Endpoint descriptions
- Link to interactive Swagger docs

## Example Workflow

### Example 1: Rheumatoid Arthritis Study

```
Sponsor: Pharma Research Institute
Title: Phase 2 Study of JAK Inhibitor in Rheumatoid Arthritis
Indication: Rheumatoid Arthritis
Phase: Phase 2
Design: randomized, double-blind, placebo-controlled
Sample Size: 200
Duration: 52 weeks
Primary Endpoint: ACR20 response at Week 24
Inclusion Criteria:
  - Age 18-75 years
  - Active RA with inadequate response to MTX
  - DAS28 score ≥ 3.2
Exclusion Criteria:
  - Prior biologic therapy
  - Active infection
  - Malignancy within 5 years
```

### Example 2: Oncology Study

```
Sponsor: Oncology Clinical Research
Title: Phase 3 Study of Checkpoint Inhibitor in NSCLC
Indication: Advanced Non-Small Cell Lung Cancer
Phase: Phase 3
Design: randomized, open-label, active-controlled
Sample Size: 450
Duration: 104 weeks
Primary Endpoint: Overall Survival (OS)
Inclusion Criteria:
  - Age ≥ 18 years
  - Histologically confirmed NSCLC
  - Stage IV disease
  - ECOG PS 0-1
Exclusion Criteria:
  - Prior checkpoint inhibitor therapy
  - Active autoimmune disease
  - Untreated brain metastases
```

## RAG Status Indicator

The web interface shows the RAG system status:

- 🟢 **Online (X protocols)**: Vector database is active with X examples
- 🔴 **Offline**: Vector database is not available

If RAG is offline:
1. Check that the server is running
2. Seed the database: `python examples/test_rag_simple.py`
3. Or use the API: `POST http://localhost:8000/api/v1/rag/seed`

## Browser Compatibility

Tested and working on:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Edge 90+
- ✅ Safari 14+

## Troubleshooting

### "Error: Failed to fetch"
**Problem**: Cannot connect to API server  
**Solution**: Make sure `python main.py` is running on port 8000

### "RAG Status: Offline"
**Problem**: Vector database not initialized  
**Solution**: Run `python examples/test_rag_simple.py` to seed the database

### "CORS Error"
**Problem**: Browser blocking cross-origin requests  
**Solution**: The server already has CORS enabled. If using a different port, update `API_BASE` in the HTML file.

### Downloads not working
**Problem**: Browser blocking downloads  
**Solution**: Allow downloads from localhost in browser settings

## Customization

### Change API URL

Edit `index.html` and modify the `API_BASE` constant:

```javascript
const API_BASE = 'http://localhost:8000';  // Change this
```

### Add More Fields

To add custom fields to the form:

1. Add HTML form elements in the form section
2. Update the `requestData` object in the submit handler
3. Ensure the backend API accepts the new fields

### Styling

All styles are in the `<style>` section. You can:
- Change colors by modifying hex codes
- Adjust gradient: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- Modify fonts, spacing, shadows, etc.

## Security Notes

⚠️ **This is a development/demo interface**

For production use:
- Implement authentication
- Use HTTPS
- Validate all inputs server-side
- Implement rate limiting
- Restrict CORS to specific origins
- Add CSRF protection
- Sanitize all user inputs

## Integration with Existing Systems

The web interface calls the same REST API as any other client. You can:

1. **Embed in existing applications**: Use an iframe
2. **White-label**: Customize branding and colors
3. **Extend functionality**: Add custom JavaScript
4. **Mobile-responsive**: Already works on tablets and phones

## API Response Format

When you generate a protocol, the API returns:

```json
{
  "request_id": "REQ-ABC123",
  "protocol_structured": { ... },
  "protocol_text": "...",
  "crf_schema": { ... },
  "validation_status": "passed",
  "overall_confidence": 0.97,
  "rag_retrieved": 3,
  "templates_used": ["standard_protocol_v1"],
  "generation_time_seconds": 2.5
}
```

## Support

For issues or questions:
- Check the API docs: http://localhost:8000/docs
- Review the RAG guide: `RAG_GUIDE.md`
- Run tests: `python examples/test_rag.py all`
- Check status: `python examples/check_rag_status.py`

---

**Built with**: HTML5, CSS3, JavaScript (Vanilla)  
**No external dependencies**: Works offline after loading  
**License**: MIT (for demo purposes)
