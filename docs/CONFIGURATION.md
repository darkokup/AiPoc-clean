# Configuration Guide

## System Modes & Features

The AI Clinical Trial Protocol Generator operates in different modes depending on which features are enabled.

---

## Generation Modes

### Mode 1: Template-Only (Fastest, No Dependencies)

**Configuration:**
```python
protocol_generator = ProtocolTemplateGenerator(use_rag=False, use_llm=False)
```

**Features:**
- ✅ Uses predefined templates
- ✅ Fast generation (~1-2 seconds)
- ✅ No external dependencies
- ✅ No API costs
- ❌ No context from similar protocols
- ❌ No AI-enhanced content

**Use Cases:**
- Quick prototyping
- Offline development
- Cost-sensitive environments
- Testing template structure

---

### Mode 2: RAG-Enhanced (Recommended Default)

**Configuration:**
```python
protocol_generator = ProtocolTemplateGenerator(use_rag=True, use_llm=False)
```

**Features:**
- ✅ Vector search for similar protocols
- ✅ Context-aware generation
- ✅ Learns from 1,159+ real protocols
- ✅ Medium generation time (~2-4 seconds)
- ✅ No API costs (only local ChromaDB)
- ❌ No LLM-generated content

**Use Cases:**
- Production environments without OpenAI
- Cost-conscious deployments
- When AI API is unavailable
- Organizations wanting control over all content

**Requirements:**
```bash
pip install chromadb sentence-transformers
```

---

### Mode 3: RAG + LLM (Highest Quality) ⭐ **CURRENT DEFAULT**

**Configuration:**
```python
# In main.py (line 45)
protocol_generator = ProtocolTemplateGenerator(use_rag=True, use_llm=True)
```

**Features:**
- ✅ Vector search for similar protocols
- ✅ AI-generated objectives and criteria
- ✅ Professional, indication-specific content
- ✅ Regulatory-compliant language
- ✅ Highest quality output
- ⚠️ Slower generation (~5-10 seconds)
- ⚠️ Requires OpenAI API key
- ⚠️ API costs (~$0.01-0.03 per protocol)

**Use Cases:**
- Production deployments
- High-quality protocol requirements
- When AI enhancement is valued
- Organizations with OpenAI budget

**Requirements:**
```bash
pip install chromadb sentence-transformers openai

# Create .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

---

## Current Configuration

### Main Application (main.py)

**Line 45:**
```python
protocol_generator = ProtocolTemplateGenerator(use_rag=True, use_llm=True)
```

This means:
- ✅ **RAG is ENABLED** - Uses vector database with 1,159 real protocols
- ✅ **LLM is ENABLED** - Uses OpenAI GPT-4 for enhanced content generation
- ✅ **Graceful Fallback** - If OpenAI API key is missing, automatically falls back to RAG-only mode

### Startup Messages

**With OpenAI API Key:**
```
✓ RAG Service initialized with 1159 protocol examples
✓ RAG enabled for protocol generation
✓ LLM enabled for AI-enhanced protocol generation
```

**Without OpenAI API Key:**
```
✓ RAG Service initialized with 1159 protocol examples
✓ RAG enabled for protocol generation
⚠ LLM initialization failed: OpenAI API key not configured. Falling back to template-only mode.
```

---

## Environment Variables

### Required for All Modes

```bash
# API Configuration (defaults work fine)
API_HOST=0.0.0.0
API_PORT=8000
API_ENVIRONMENT=development

# Storage Paths (defaults work fine)
VECTOR_DB_PATH=./vector_db
ARTIFACTS_PATH=./artifacts
```

### Required for RAG Mode

```bash
# Automatically created if missing
VECTOR_DB_PATH=./vector_db
```

### Required for LLM Mode

```bash
# REQUIRED: Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-your-actual-key-here

# OPTIONAL: Choose model (defaults to gpt-4o)
# OPENAI_MODEL=gpt-4o          # Best quality (default)
# OPENAI_MODEL=gpt-4o-mini     # Faster, cheaper
# OPENAI_MODEL=gpt-3.5-turbo   # Cheapest, lower quality
```

### Disabling ChromaDB Telemetry (Optional)

```bash
# Suppress ChromaDB usage statistics warnings
ANONYMIZED_TELEMETRY=False
```

---

## How to Enable/Disable Features

### Disable LLM (Keep RAG)

**Edit main.py line 45:**
```python
# Before (current)
protocol_generator = ProtocolTemplateGenerator(use_rag=True, use_llm=True)

# After (RAG-only)
protocol_generator = ProtocolTemplateGenerator(use_rag=True, use_llm=False)
```

**Restart server:**
```bash
# Stop server (Ctrl+C)
python main.py
```

**Result:**
- Saves OpenAI API costs
- Still benefits from 1,159 real protocol examples
- Slightly faster generation
- Good quality output

---

### Disable Both (Template-Only)

**Edit main.py line 45:**
```python
# Template-only mode
protocol_generator = ProtocolTemplateGenerator(use_rag=False, use_llm=False)
```

**Result:**
- Fastest generation
- No external dependencies
- Basic protocol quality
- Good for development/testing

---

### Enable LLM Without OpenAI Key

**The system gracefully handles this:**

1. **Configuration in main.py:**
   ```python
   protocol_generator = ProtocolTemplateGenerator(use_rag=True, use_llm=True)
   ```

2. **Missing OpenAI API key:**
   ```
   ⚠ LLM initialization failed: OpenAI API key not configured.
      Falling back to template-only mode.
   ```

3. **Automatic fallback:**
   - System continues running
   - Uses RAG-only mode
   - No errors or crashes
   - Protocols still generated successfully

**This is the CURRENT behavior** - LLM is enabled in code, but falls back if API key is missing.

---

## Per-Request Configuration

### Via API

You can also control modes per request using custom headers or parameters (requires code modification):

```python
# Example custom implementation
@app.post("/api/v1/generate")
async def generate_protocol(
    trial_spec: TrialSpecInput,
    use_llm: bool = Query(default=True, description="Use LLM enhancement")
):
    # Create generator for this request
    generator = ProtocolTemplateGenerator(use_rag=True, use_llm=use_llm)
    protocol = generator.generate_structured_protocol(trial_spec)
    return protocol
```

**Usage:**
```bash
# With LLM
POST /api/v1/generate?use_llm=true

# Without LLM (faster, cheaper)
POST /api/v1/generate?use_llm=false
```

---

## Performance Comparison

| Mode | Generation Time | Cost/Protocol | Quality | Use Case |
|------|----------------|---------------|---------|----------|
| Template-Only | ~1-2 sec | $0.00 | ⭐⭐⭐ | Development, testing |
| RAG-Only | ~2-4 sec | $0.00 | ⭐⭐⭐⭐ | Production (cost-sensitive) |
| RAG + LLM | ~5-10 sec | $0.01-0.03 | ⭐⭐⭐⭐⭐ | Production (quality-focused) |

---

## Cost Analysis (LLM Mode)

### OpenAI Pricing (November 2025)

| Model | Input Cost | Output Cost | Per Protocol | Use Case |
|-------|-----------|-------------|--------------|----------|
| gpt-4o | $2.50/1M tokens | $10.00/1M tokens | ~$0.025 | Best quality |
| gpt-4o-mini | $0.15/1M tokens | $0.60/1M tokens | ~$0.008 | Good quality |
| gpt-3.5-turbo | $0.50/1M tokens | $1.50/1M tokens | ~$0.002 | Basic quality |

### Estimated Monthly Costs

**Low Volume (10 protocols/day):**
- gpt-4o: ~$7.50/month
- gpt-4o-mini: ~$2.40/month
- gpt-3.5-turbo: ~$0.60/month

**Medium Volume (50 protocols/day):**
- gpt-4o: ~$37.50/month
- gpt-4o-mini: ~$12.00/month
- gpt-3.5-turbo: ~$3.00/month

**High Volume (200 protocols/day):**
- gpt-4o: ~$150/month
- gpt-4o-mini: ~$48/month
- gpt-3.5-turbo: ~$12/month

**Note:** RAG mode costs $0 regardless of volume!

---

## Verification Commands

### Check Current Configuration

```bash
# Check which features are enabled
python -c "from main import protocol_generator; \
    print(f'RAG enabled: {protocol_generator.use_rag}'); \
    print(f'LLM enabled: {protocol_generator.use_llm}')"
```

**Expected Output (current config):**
```
✓ RAG Service initialized with 1159 protocol examples
✓ RAG enabled for protocol generation
✓ LLM enabled for AI-enhanced protocol generation
RAG enabled: True
LLM enabled: True
```

### Check OpenAI API Key

```bash
# Check if OpenAI API key is configured
python -c "from config import settings; \
    print('API Key configured:', bool(settings.openai_api_key))"
```

### Test LLM Connection

```bash
# Run LLM test suite
pytest examples/test_llm.py -v
```

### Test RAG Status

```bash
# Check RAG database
python examples/check_rag_status.py
```

---

## Troubleshooting

### LLM Not Working

**Symptom:**
```
⚠ LLM initialization failed: OpenAI API key not configured.
```

**Solution:**
1. Get API key from https://platform.openai.com/api-keys
2. Add to `.env` file:
   ```bash
   OPENAI_API_KEY=sk-proj-your-key-here
   ```
3. Restart server:
   ```bash
   python main.py
   ```

### RAG Not Working

**Symptom:**
```
⚠ RAG initialization failed: ...
```

**Solution:**
1. Install ChromaDB:
   ```bash
   pip install chromadb sentence-transformers
   ```
2. Seed database:
   ```bash
   python examples/seed_rag_direct.py
   ```
3. Restart server

### Slow Generation

**Cause:** LLM mode takes 5-10 seconds per protocol

**Solutions:**
1. Switch to faster model:
   ```bash
   # In .env
   OPENAI_MODEL=gpt-4o-mini
   ```
2. Disable LLM for faster generation:
   ```python
   # In main.py
   protocol_generator = ProtocolTemplateGenerator(use_rag=True, use_llm=False)
   ```
3. Use caching (implement request caching)

### High OpenAI Costs

**Solutions:**
1. Switch to cheaper model (gpt-4o-mini or gpt-3.5-turbo)
2. Disable LLM for non-critical requests
3. Implement rate limiting
4. Use RAG-only mode
5. Cache frequently generated protocols

---

## Recommendations

### For Development

```python
# Fast, no dependencies
protocol_generator = ProtocolTemplateGenerator(use_rag=False, use_llm=False)
```

### For Production (Budget-Friendly)

```python
# Best quality without API costs
protocol_generator = ProtocolTemplateGenerator(use_rag=True, use_llm=False)
```

### For Production (Premium Quality)

```python
# Current default - highest quality
protocol_generator = ProtocolTemplateGenerator(use_rag=True, use_llm=True)
```

### For Mixed Workloads

Implement dynamic switching:
```python
# High-priority requests: RAG + LLM
# Regular requests: RAG-only
# Bulk operations: Template-only
```

---

## Summary

**Current Default Configuration (as of this update):**
- ✅ **RAG:** ENABLED (1,159 real protocols)
- ✅ **LLM:** ENABLED (OpenAI GPT-4)
- ✅ **Fallback:** Automatic to RAG-only if no API key
- ✅ **Mode:** Highest quality, context-aware, AI-enhanced

**To use the system:**
1. **No setup required** - Works in RAG-only mode without OpenAI
2. **For best quality** - Add `OPENAI_API_KEY` to `.env` file
3. **To reduce costs** - Edit `main.py` to disable LLM

**The system is designed to work in all scenarios with graceful degradation!**

---

*Last Updated: November 12, 2025*
*Default Configuration: RAG + LLM with graceful fallback*
