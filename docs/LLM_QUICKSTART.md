# 🚀 Quick Start: OpenAI LLM Integration

## 3-Step Setup

### 1️⃣ Install Package
```powershell
pip install openai
```

### 2️⃣ Add API Key
Create `.env` file:
```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3️⃣ Test It
```powershell
python examples/test_llm.py
```

---

## What You Get

### Before (Template Only)
```
Primary: To evaluate the efficacy of the study intervention.
Secondary: To assess safety and tolerability.
```

### After (AI-Enhanced)
```
Primary: To evaluate the objective response rate (ORR) of Novel Therapy 
compared to standard of care in patients with previously treated advanced 
non-small cell lung cancer as assessed by RECIST v1.1 criteria at Week 24.

Secondary: To assess progression-free survival (PFS), overall survival (OS), 
duration of response, disease control rate, safety and tolerability including 
incidence and severity of treatment-emergent adverse events graded per CTCAE v5.0, 
and patient-reported outcomes using EORTC QLQ-C30 and QLQ-LC13 questionnaires.
```

---

## Files Created

✅ `app/services/llm_service.py` - OpenAI integration  
✅ `app/services/generator.py` - Updated with LLM support  
✅ `LLM_INTEGRATION_GUIDE.md` - Complete documentation  
✅ `examples/test_llm.py` - Test suite  
✅ `requirements.txt` - Updated with openai package  

---

## Usage

### Web Interface
1. Start server: `python main.py`
2. Open: http://localhost:8000/
3. Generate protocol - will automatically use LLM if configured

### API
```powershell
curl -X POST "http://localhost:8000/api/v1/generate" `
  -H "Content-Type: application/json" `
  -d '{
    "title": "Phase II Diabetes Study",
    "sponsor": "Research Institute",
    "phase": "Phase II",
    "indication": "Type 2 Diabetes",
    "design": "Randomized controlled trial",
    "sample_size": 100,
    "duration_weeks": 24
  }'
```

### Python Code
```python
from app.services.generator import ProtocolTemplateGenerator

# LLM auto-enabled if API key configured
generator = ProtocolTemplateGenerator(use_llm=True)
protocol = generator.generate_protocol(spec)
```

---

## Cost

**Per Protocol (~3,500 tokens):**
- GPT-4o: $0.024 (2.4 cents)
- GPT-3.5-turbo: $0.004 (0.4 cents)

**1,000 protocols/month:**
- GPT-4o: ~$24
- GPT-3.5-turbo: ~$4

---

## Troubleshooting

### ❌ "Import openai could not be resolved"
```powershell
pip install openai
```

### ❌ "OpenAI API key not configured"
1. Check `.env` file exists in project root
2. Verify `OPENAI_API_KEY=sk-...` is set (not commented)
3. Restart server

### ❌ "Rate limit exceeded"
- Wait 60 seconds
- Check OpenAI account limits
- Upgrade to paid tier

---

## Disable LLM (Optional)

### Temporary
```python
generator = ProtocolTemplateGenerator(use_llm=False)
```

### Permanent
Comment out in `.env`:
```bash
# OPENAI_API_KEY=sk-...
```

---

## Next Steps

1. ✅ Get API key from https://platform.openai.com/
2. ✅ Run `pip install openai`
3. ✅ Create `.env` with your API key
4. ✅ Run `python examples/test_llm.py`
5. ✅ Generate protocols via web UI or API
6. 📖 Read full guide: `LLM_INTEGRATION_GUIDE.md`

---

**Need Help?** See `LLM_INTEGRATION_GUIDE.md` for detailed documentation.
