# Debugging Guide for AI Protocol Generator

## Quick Start - VS Code Debugger

1. **Set breakpoints** by clicking left of line numbers in VS Code
2. Press **F5** or click "Run and Debug" → "FastAPI: Debug Server"
3. The debugger will:
   - Start the FastAPI server on http://localhost:8000
   - Stop at your breakpoints
   - Let you inspect variables, step through code, etc.

## Debugging Methods

### 1. VS Code Integrated Debugger ⭐ RECOMMENDED

**Setup Complete!** Just use the configurations in `.vscode/launch.json`:

- **"FastAPI: Debug Server"** - Debug the main API server
- **"FastAPI: Debug Current File"** - Debug any Python file you have open
- **"Python: Debug Test File"** - Debug test files in examples/

**How to use:**
1. Open the file you want to debug (e.g., `main.py` or `app/services/generator.py`)
2. Set breakpoints by clicking left of line numbers
3. Press **F5** → Select "FastAPI: Debug Server"
4. Make API requests to http://localhost:8000
5. Debugger will pause at breakpoints

**Keyboard shortcuts:**
- `F5` - Continue
- `F10` - Step over
- `F11` - Step into
- `Shift+F11` - Step out
- `Shift+F5` - Stop debugging

### 2. Enable Debug Logging

Add to your `.env` file:
```
DEBUG=true
```

Then check the console output for detailed logs:
```bash
uvicorn main:app --reload
```

### 3. Python Debugger (pdb) - Manual Breakpoints

Add this line anywhere in your code:
```python
import pdb; pdb.set_trace()
```

Or use the newer `breakpoint()`:
```python
breakpoint()  # Python 3.7+
```

When code hits this line, you'll get an interactive debugger in the terminal.

**pdb commands:**
- `n` (next) - Execute current line
- `s` (step) - Step into function
- `c` (continue) - Continue execution
- `p variable` - Print variable value
- `pp variable` - Pretty-print variable
- `l` (list) - Show code context
- `w` (where) - Show stack trace
- `q` (quit) - Exit debugger

### 4. FastAPI Interactive Docs Debugging

1. Start the server: `uvicorn main:app --reload`
2. Open http://localhost:8000/docs
3. Use "Try it out" to test endpoints
4. Check the Response section for errors
5. Check the terminal for stack traces

### 5. curl/Postman Debugging

Test endpoints directly:
```bash
# Test protocol generation
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d @examples/example_request.json

# Test with verbose output
curl -v -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d @examples/example_request.json
```

### 6. Debug Specific Components

**Generator Service:**
```python
# In app/services/generator.py, add:
logger = logging.getLogger(__name__)

def generate_structured_protocol(self, spec: TrialSpecInput):
    logger.debug(f"Starting protocol generation for {spec.indication}")
    breakpoint()  # Pause here
    # ... rest of code
```

**LLM Service:**
```python
# In app/services/llm_service.py, add:
def generate_objectives(self, trial_spec, rag_context, additional_instructions=None):
    logger.debug(f"Generating objectives with instructions: {additional_instructions}")
    breakpoint()
    # ... rest of code
```

**RAG Service:**
```python
# In app/services/rag_service.py, add:
def retrieve_similar_protocols(self, trial_spec, n_results=3):
    logger.debug(f"Searching for {n_results} similar protocols")
    breakpoint()
    # ... rest of code
```

## Common Debugging Scenarios

### Debugging API Requests

1. Set breakpoint in `main.py` at line 106 (`async def generate_protocol`)
2. Start debugger (F5)
3. Make request from web UI or curl
4. Inspect `trial_spec` variable to see what was received
5. Step through validation, generation, etc.

### Debugging LLM Generation

1. Set breakpoint in `app/services/generator.py` at line 306 (objectives generation)
2. Check if `additional_instructions` is passed correctly
3. Step into `llm_service.generate_objectives()` to see the prompt
4. Inspect the LLM response

### Debugging RAG Retrieval

1. Set breakpoint in `app/services/generator.py` at line 188
2. Check what similar protocols were retrieved
3. Inspect `similar_protocols` variable
4. See if similarity scores are reasonable

### Debugging Frontend Issues

1. Open browser DevTools (F12)
2. Go to Network tab
3. Make request from web UI
4. Check:
   - Request payload (what was sent)
   - Response (what was received)
   - Status code (200, 400, 500, etc.)
5. Check Console tab for JavaScript errors

## Environment Variables for Debugging

Add to `.env`:
```bash
# Enable debug mode
DEBUG=true

# OpenAI API (if using LLM)
OPENAI_API_KEY=sk-your-key-here

# Detailed logging
PYTHONUNBUFFERED=1
LOG_LEVEL=DEBUG
```

## Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <process_id> /F

# Or use different port
uvicorn main:app --reload --port 8001
```

### Breakpoints not working
- Make sure you selected "FastAPI: Debug Server" configuration
- Ensure `"justMyCode": false` in launch.json (already configured)
- Check that file paths are correct

### LLM not generating
- Check `.env` has valid `OPENAI_API_KEY`
- Check logs for API errors
- Try setting breakpoint in `app/services/llm_service.py` line 40

### RAG not finding protocols
- Check database exists: `python examples/check_rag_status.py`
- Seed database: `python examples/seed_rag_direct.py`
- Check logs for ChromaDB errors

## Best Practices

1. **Use VS Code debugger** for complex issues (stepping through code)
2. **Use logging** for tracking flow without stopping execution
3. **Use FastAPI docs** for quick API testing
4. **Use pdb** for quick one-off debugging in terminal
5. **Check logs first** before setting breakpoints

## Testing with Debugger

Run test files with debugger:
```bash
# Option 1: Open test file, press F5, select "Debug Current File"
# Option 2: Terminal
python examples/test_additional_instructions_simple.py
```

Set breakpoint in test file to debug specific scenarios.

## Example Debug Session

1. **Goal**: Debug why additional_instructions aren't appearing in output
2. **Steps**:
   ```
   a. Set breakpoint in main.py line 130 (generate_protocol)
   b. Start debugger (F5)
   c. Submit request with additional_instructions from web UI
   d. When breakpoint hits, inspect trial_spec.additional_instructions
   e. Step into (F11) generate_structured_protocol
   f. Step through to line 306 where objectives are generated
   g. Step into generate_objectives
   h. Check if additional_instructions parameter is received
   i. Check the prompt being sent to LLM
   j. Check the response from LLM
   ```

3. **What to look for**:
   - Is `additional_instructions` null or has value?
   - Is it being passed to LLM methods?
   - Is it in the prompt string?
   - What does LLM return?

## Quick Debug Checklist

- [ ] Set breakpoint at entry point (e.g., `generate_protocol`)
- [ ] Start debugger (F5)
- [ ] Trigger the code path you want to debug
- [ ] Inspect variables in Debug sidebar
- [ ] Step through code (F10/F11)
- [ ] Check Call Stack to understand execution flow
- [ ] Check Logs in terminal for additional info

Happy debugging! 🐛
