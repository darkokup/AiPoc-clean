# OpenAI LLM Integration Guide

## Overview

This guide shows how to integrate OpenAI's GPT models into the Clinical Trial Protocol Generator for AI-enhanced content generation.

## 🎯 What the LLM Integration Adds

**Before (Template + RAG only):**
- Static templates with variable substitution
- RAG retrieves similar protocols for context
- No actual AI text generation

**After (Template + RAG + LLM):**
- AI-generated protocol sections based on trial specifications
- Context-aware content using RAG examples
- Professional clinical trial language
- Regulatory-compliant content (ICH-GCP, CDISC)

## 📋 Step-by-Step Integration

### 1. Install OpenAI Package

Add to `requirements.txt`:
```bash
openai==1.54.0
```

Install the package:
```powershell
pip install openai
```

### 2. Get OpenAI API Key

1. Sign up at https://platform.openai.com/
2. Navigate to API Keys section
3. Create new secret key
4. Copy the key (starts with `sk-`)

### 3. Configure Environment

Create `.env` file in project root:
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-api-key-here

# Other settings (optional)
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

**Important**: Add `.env` to `.gitignore` to avoid committing your API key!

### 4. Files Already Created

✅ `app/services/llm_service.py` - OpenAI integration service
✅ `app/services/generator.py` - Updated to use LLM

The LLM service includes:
- `enhance_protocol_section()` - Enhance any protocol section with AI
- `generate_objectives()` - AI-generated primary/secondary objectives
- `generate_inclusion_criteria()` - AI-generated inclusion criteria
- `generate_exclusion_criteria()` - AI-generated exclusion criteria

### 5. Enable LLM in Main Application

The generator automatically detects if OpenAI is configured:

```python
# In main.py or your code
from app.services.generator import ProtocolTemplateGenerator

# This will auto-enable LLM if OPENAI_API_KEY is set
generator = ProtocolTemplateGenerator(
    use_rag=True,   # Use RAG for similar protocols
    use_llm=True    # Use LLM for AI generation (new!)
)
```

### 6. Test the Integration

Run the server:
```powershell
python main.py
```

Expected console output:
```
✓ RAG enabled for protocol generation
✓ LLM enabled for AI-enhanced protocol generation
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Generate a protocol via API:
```powershell
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -d '{
  "title": "AI-Enhanced Phase II Oncology Trial",
  "sponsor": "Research Institute",
  "phase": "Phase II",
  "indication": "Non-Small Cell Lung Cancer",
  "design": "Randomized, double-blind, placebo-controlled",
  "sample_size": 150,
  "duration_weeks": 52
}'
```

You should see in logs:
```
✓ Objectives generated using LLM
```

## 🔧 How It Works

### Architecture Flow

```
User Request
    ↓
1. RAG Service retrieves similar protocols from vector DB
    ↓
2. LLM Service receives:
   - Trial specifications
   - Template structure
   - Similar protocol examples (from RAG)
    ↓
3. OpenAI GPT-4 generates professional content
    ↓
4. Fallback to templates if LLM fails
    ↓
Generated Protocol
```

### Example: Objectives Generation

**Template-Only Mode:**
```python
objectives = {
    "primary": "To evaluate the efficacy of the study intervention in patients with NSCLC.",
    "secondary": "To assess the safety and tolerability of the study intervention."
}
```

**LLM-Enhanced Mode:**
```python
# LLM generates contextual, detailed objectives:
objectives = {
    "primary": "To evaluate the objective response rate (ORR) of [intervention] compared to placebo in patients with previously treated advanced non-small cell lung cancer (NSCLC) as assessed by RECIST v1.1 criteria.",
    "secondary": "To assess progression-free survival (PFS), overall survival (OS), duration of response, disease control rate, safety and tolerability including incidence of treatment-emergent adverse events, and patient-reported outcomes using EORTC QLQ-C30."
}
```

### Code Example

```python
# In llm_service.py
def generate_objectives(self, trial_spec, rag_context):
    """Generate AI-enhanced objectives."""
    
    # Build prompt with trial details + RAG context
    prompt = f"""Generate objectives for a clinical trial.
    
    Trial: {trial_spec['title']}
    Phase: {trial_spec['phase']}
    Indication: {trial_spec['indication']}
    
    Similar protocol examples:
    {rag_context}
    
    Generate professional primary and secondary objectives..."""
    
    # Call OpenAI
    response = self.client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a clinical trial expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    return json.loads(response.choices[0].message.content)
```

## 💰 Cost Considerations

### OpenAI Pricing (as of Nov 2025)

**GPT-4o (Recommended):**
- Input: $2.50 / 1M tokens
- Output: $10.00 / 1M tokens

**GPT-3.5-turbo (Budget option):**
- Input: $0.50 / 1M tokens
- Output: $1.50 / 1M tokens

### Estimated Cost Per Protocol

Each protocol generation uses approximately:
- 1,500 input tokens (trial spec + RAG context + prompts)
- 2,000 output tokens (generated content)

**GPT-4o cost per protocol:** ~$0.024 (2.4 cents)
**GPT-3.5-turbo cost:** ~$0.004 (0.4 cents)

**For 1,000 protocols per month:**
- GPT-4o: ~$24/month
- GPT-3.5-turbo: ~$4/month

## 🔒 Security Best Practices

### 1. Protect Your API Key

Never commit API keys to Git:
```bash
# .gitignore
.env
*.env
.env.*
```

### 2. Use Environment Variables

```python
# config.py already handles this:
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: Optional[str] = None  # Reads from OPENAI_API_KEY env var
    
    class Config:
        env_file = ".env"
```

### 3. Rate Limiting

Add rate limiting to prevent API abuse:
```python
# In llm_service.py (optional enhancement)
from time import sleep
import os

class LLMService:
    def __init__(self):
        self.requests_per_minute = 60
        self.last_request_time = 0
```

### 4. Error Handling

The service includes graceful fallback:
```python
try:
    # Try LLM generation
    result = llm_service.generate_objectives(...)
except Exception as e:
    # Fallback to template
    print(f"⚠ LLM failed, using template: {e}")
    result = template_objectives
```

## 🎛️ Configuration Options

### Change GPT Model

Edit `app/services/llm_service.py`:
```python
class LLMService:
    def __init__(self):
        # Options: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
        self.model = "gpt-4o"  # Change here
```

### Adjust Temperature (Creativity)

```python
response = self.client.chat.completions.create(
    model=self.model,
    temperature=0.7,  # 0.0 = deterministic, 1.0 = creative
    # Lower (0.3-0.5) for factual medical content
    # Higher (0.7-0.9) for creative descriptions
)
```

### Control Output Length

```python
response = self.client.chat.completions.create(
    model=self.model,
    max_tokens=2000,  # Maximum response length
)
```

## 🧪 Testing LLM Integration

### Test 1: Check LLM Availability

```python
from app.services.llm_service import is_llm_available

if is_llm_available():
    print("✓ LLM is configured and ready")
else:
    print("✗ LLM not available (check API key)")
```

### Test 2: Generate Sample Objectives

Create `examples/test_llm.py`:
```python
from app.services.llm_service import get_llm_service

llm = get_llm_service()

trial_spec = {
    "title": "Phase II Diabetes Trial",
    "phase": "Phase II",
    "indication": "Type 2 Diabetes Mellitus",
    "design": "Randomized controlled trial"
}

objectives = llm.generate_objectives(trial_spec)
print("Primary:", objectives["primary"])
print("Secondary:", objectives["secondary"])
```

Run:
```powershell
python examples/test_llm.py
```

### Test 3: Full Protocol with LLM

```powershell
# Start server
python main.py

# Generate protocol (will use LLM if configured)
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -d @test_protocol.json
```

Check logs for:
```
✓ RAG enabled
✓ LLM enabled
✓ Objectives generated using LLM
```

## 🐛 Troubleshooting

### Issue: "Import openai could not be resolved"

**Solution:**
```powershell
pip install openai
```

### Issue: "OpenAI API key not configured"

**Solution:**
1. Check `.env` file exists
2. Verify `OPENAI_API_KEY=sk-...` is set
3. Restart the server to reload environment

### Issue: "Rate limit exceeded"

**Solution:**
- Wait 60 seconds
- Check your OpenAI account limits
- Upgrade to paid tier for higher limits

### Issue: "LLM initialization failed"

**Solution:**
```powershell
# Test OpenAI connection directly
python -c "from openai import OpenAI; import os; client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')); print(client.models.list())"
```

### Issue: "Context length exceeded"

**Solution:**
Reduce RAG context in prompts:
```python
# In llm_service.py
for i, protocol in enumerate(rag_context[:1], 1):  # Limit to 1 example instead of 2
```

## 🔄 Disable LLM (Use Template Mode)

### Temporary Disable

```python
generator = ProtocolTemplateGenerator(
    use_rag=True,
    use_llm=False  # Disable LLM, use templates only
)
```

### Permanent Disable

Remove or comment out in `.env`:
```bash
# OPENAI_API_KEY=sk-...
```

The system will automatically fall back to template mode:
```
⚠ LLM initialization failed: OpenAI API key not configured. Falling back to template-only mode.
```

## 📊 Monitoring Usage

### Track API Costs

Add to `llm_service.py`:
```python
def generate_objectives(self, ...):
    response = self.client.chat.completions.create(...)
    
    # Log usage
    usage = response.usage
    print(f"Tokens used: {usage.total_tokens} (${usage.total_tokens * 0.00001:.4f})")
```

### View OpenAI Dashboard

1. Go to https://platform.openai.com/usage
2. View daily/monthly usage and costs
3. Set billing alerts

## 🚀 Advanced Features

### Custom System Prompts

Modify the expert persona:
```python
system_prompt = """You are a senior clinical trial protocol writer with:
- 15+ years experience in oncology trials
- Deep knowledge of FDA/EMA guidelines
- Expertise in ICH-GCP, CDISC standards
- Publications in major medical journals

Always write in professional, regulatory-compliant language."""
```

### Few-Shot Learning

Add examples to improve output:
```python
prompt = f"""Here are examples of excellent objectives:

Example 1:
Primary: To evaluate the ORR of pembrolizumab vs chemotherapy...
Secondary: To assess PFS, OS, safety, and QoL...

Example 2:
Primary: To determine the maximum tolerated dose...
Secondary: To characterize pharmacokinetics...

Now generate objectives for: {trial_spec}"""
```

### Streaming Responses

For real-time UI updates:
```python
stream = self.client.chat.completions.create(
    model=self.model,
    messages=messages,
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        yield chunk.choices[0].delta.content
```

## 📚 Next Steps

1. **Test with your API key**: Follow steps 1-6 above
2. **Generate sample protocols**: Use web UI or API
3. **Compare outputs**: Generate same protocol with/without LLM
4. **Fine-tune prompts**: Edit `llm_service.py` to customize behavior
5. **Monitor costs**: Track usage in OpenAI dashboard
6. **Add more LLM features**: Expand to other sections (background, statistical plan, etc.)

## 🎓 Learning Resources

- **OpenAI API Docs**: https://platform.openai.com/docs
- **Prompt Engineering**: https://platform.openai.com/docs/guides/prompt-engineering
- **ICH-GCP Guidelines**: https://www.ich.org/page/efficacy-guidelines
- **CDISC Standards**: https://www.cdisc.org/standards

---

## Quick Start Summary

```powershell
# 1. Install
pip install openai

# 2. Configure
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# 3. Run
python main.py

# 4. Test
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -d @test_spec.json

# 5. Check logs for:
# ✓ LLM enabled for AI-enhanced protocol generation
# ✓ Objectives generated using LLM
```

That's it! Your protocol generator now has AI superpowers! 🚀
