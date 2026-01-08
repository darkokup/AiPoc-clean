# 🎨 Web Interface Visual Guide

## Overview

The Clinical Trial Protocol Generator web interface provides an intuitive way to generate CDISC-compliant protocols with RAG-enhanced AI.

## Interface Layout

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│     🧬 AI Clinical Trial Protocol Generator                │
│     Generate CDISC-compliant clinical trial protocols      │
│     with RAG-enhanced AI                                    │
│                                                             │
│  [✓ RAG Enabled] [✓ CDASH] [✓ FHIR Export] [✓ ODM XML]   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [📝 Generate Protocol] [🔍 RAG Search] [🌐 API Endpoints] │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                                                        │  │
│  │  RAG Status: ● Online (5 protocols)                   │  │
│  │                                                        │  │
│  │  Sponsor: [_________________________________]          │  │
│  │                                                        │  │
│  │  Protocol Title: [____________________________]       │  │
│  │                                                        │  │
│  │  Indication: [_______________________________]        │  │
│  │                                                        │  │
│  │  Phase: [Phase 2 ▼]    Region: [US ▼]               │  │
│  │                                                        │  │
│  │  Study Design: [__________________________]           │  │
│  │                                                        │  │
│  │  Sample Size: [____]  Duration (weeks): [____]       │  │
│  │                                                        │  │
│  │  Primary Endpoint: [_________________________]        │  │
│  │                                                        │  │
│  │  Inclusion Criteria:                                  │  │
│  │  [_________________________________________]           │  │
│  │  [_________________________________________]           │  │
│  │                                                        │  │
│  │  Exclusion Criteria:                                  │  │
│  │  [_________________________________________]           │  │
│  │  [_________________________________________]           │  │
│  │                                                        │  │
│  │          [  🚀 Generate Protocol  ]                   │  │
│  │                                                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Tabs Explained

### 📝 Generate Protocol Tab

**Purpose**: Create new clinical trial protocols using AI + RAG

**Key Features**:
- Real-time RAG status indicator
- Form validation
- Progress spinner during generation
- Success message with protocol details
- Download/export buttons

**Workflow**:
```
Fill Form → Submit → RAG Search → Generate → Download
```

### 🔍 RAG Search Tab

**Purpose**: Search for similar protocols in the vector database

**Key Features**:
- Semantic similarity search
- Adjustable number of results (1-10)
- Similarity scores displayed as percentages
- Protocol metadata preview

**Use Cases**:
- Find similar historical protocols
- Validate protocol design choices
- Explore database contents
- Check similarity before generation

### 🌐 API Endpoints Tab

**Purpose**: Quick reference for API integration

**Key Features**:
- Complete endpoint list
- HTTP methods (GET, POST, DELETE)
- Organized by category:
  - Core Endpoints
  - RAG Endpoints
  - Export Endpoints
- Link to interactive Swagger docs

## Color Scheme

```css
Primary Gradient: #667eea → #764ba2 (Purple/Blue)
Background: White
Sections: Light gray (#f8f9fa)
Borders: #e9ecef
Success: Green (#28a745)
Error: Red (#dc3545)
Info: Blue (#007bff)
```

## Status Indicators

### RAG Status Badge

```
● Online (5 protocols)    ← Green badge
● Offline                 ← Red badge
● Checking...            ← Gray badge
```

### HTTP Method Badges

```
GET     ← Green
POST    ← Blue
DELETE  ← Red
```

## Result Display

After successful protocol generation:

```
┌──────────────────────────────────────────────────┐
│  ✅ Protocol Generated Successfully!             │
│                                                  │
│  Request ID: REQ-ABC123                         │
│  Protocol ID: PROT-EAB569FD                     │
│  Confidence Score: 97.0%                        │
│  RAG Retrieved: 3 similar protocols             │
│                                                  │
│  [📥 Download Full Protocol]                    │
│  [📄 Export ODM XML]                            │
│  [🏥 Export FHIR JSON]                          │
└──────────────────────────────────────────────────┘
```

## Search Results Display

After RAG similarity search:

```
┌──────────────────────────────────────────────────┐
│  Search Results                                  │
│                                                  │
│  Found: 3 similar protocol(s)                   │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 1. Rheumatoid Arthritis                    │ │
│  │    Phase: Phase 2                          │ │
│  │    Similarity: 38.8%                       │ │
│  │    Sample Size: 200 | Duration: 52 weeks  │ │
│  │    ID: protocol_869a70ff6297               │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ 2. Early Alzheimer's Disease               │ │
│  │    Phase: Phase 2                          │ │
│  │    Similarity: -6.7%                       │ │
│  │    Sample Size: 250 | Duration: 78 weeks  │ │
│  │    ID: protocol_b1be78323613               │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
└──────────────────────────────────────────────────┘
```

## Responsive Design

### Desktop (1200px+)
```
┌─────────────┬─────────────┐
│   Form      │   Form      │
│   Fields    │   Fields    │
│             │             │
└─────────────┴─────────────┘
```

### Tablet/Mobile (< 768px)
```
┌─────────────────────────┐
│   Form Fields           │
│                         │
│   Form Fields           │
│                         │
└─────────────────────────┘
```

## User Interactions

### Form Submission Flow

```
1. User fills form
   ↓
2. Click "Generate Protocol"
   ↓
3. Loading spinner appears
   ↓
4. API request sent (POST /api/v1/generate)
   ↓
5. RAG searches for similar protocols
   ↓
6. Protocol generated
   ↓
7. Results displayed with download buttons
   ↓
8. User downloads protocol
```

### Error Handling

```
Error: Failed to connect to API
┌──────────────────────────────────────────┐
│ ❌ Error: Failed to fetch. Make sure    │
│    the server is running at              │
│    http://localhost:8000                 │
└──────────────────────────────────────────┘
```

## Accessibility Features

- ✅ Keyboard navigation support
- ✅ Focus indicators on inputs
- ✅ Clear labels for all form fields
- ✅ High contrast text
- ✅ Responsive font sizes
- ✅ Descriptive error messages

## Browser DevTools Network Tab

Successful generation request:

```
POST http://localhost:8000/api/v1/generate
Status: 201 Created
Content-Type: application/json

Request Payload:
{
  "sponsor": "Pharma Research",
  "title": "Phase 2 RA Study",
  "indication": "Rheumatoid Arthritis",
  "phase": "Phase 2",
  ...
}

Response:
{
  "request_id": "REQ-ABC123",
  "protocol_structured": { ... },
  "validation_status": "passed",
  "overall_confidence": 0.97,
  ...
}
```

## Tips for Best User Experience

### ✨ Quick Tips Displayed on Hover:

- **Sponsor**: Organization conducting the trial (e.g., university, pharma company)
- **Phase**: Select appropriate phase based on development stage
- **Sample Size**: Should align with phase expectations (Phase 1: 20-100, Phase 2: 100-300, Phase 3: 300+)
- **Duration**: Consider disease, endpoints, and phase
- **Primary Endpoint**: Must be measurable and clinically meaningful
- **RAG Status**: Green means similar protocols will enhance your generation

### 🎯 Common Workflows:

**Workflow 1: First-Time User**
```
1. Check RAG status (should be Online)
2. Click "RAG Search" tab to explore examples
3. Return to "Generate Protocol" tab
4. Fill form with example data
5. Generate and download
```

**Workflow 2: Experienced User**
```
1. Fill form quickly
2. Generate protocol
3. Review confidence score
4. Export in needed format (ODM/FHIR)
5. Import to EDC system
```

**Workflow 3: Research Mode**
```
1. Use RAG Search extensively
2. Compare similar protocols
3. Design new protocol based on findings
4. Generate with high confidence
```

## Keyboard Shortcuts

While not explicitly coded, standard browser shortcuts work:

- **Tab**: Navigate between fields
- **Enter**: Submit form (when focused on input)
- **Ctrl+Click** (on links): Open in new tab
- **Ctrl+S**: Save page (downloads HTML)

## Future Enhancements

Planned visual improvements:

- [ ] Protocol preview panel
- [ ] Visit schedule visualizer
- [ ] Endpoint timeline diagram
- [ ] RAG similarity heatmap
- [ ] Protocol comparison view
- [ ] Export format preview
- [ ] Dark mode toggle
- [ ] Customizable themes

## Troubleshooting Visual Issues

### Problem: Buttons not clickable
**Solution**: Check if JavaScript is enabled

### Problem: Form not submitting
**Solution**: Check console for errors, verify server is running

### Problem: Styles look broken
**Solution**: Hard refresh (Ctrl+F5) to clear cache

### Problem: RAG status stuck on "Checking..."
**Solution**: Server not responding, restart with `python main.py`

---

**Design Philosophy**: Clean, modern, professional interface suitable for clinical research environments while remaining accessible and easy to use.
