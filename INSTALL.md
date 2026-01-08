# Installation and Setup Instructions

## Complete Setup Guide

### Step 1: Verify Python Installation

```powershell
# Check Python version (requires 3.9+)
python --version

# If Python is not installed, download from python.org
# Recommended: Python 3.11 or 3.12
```

### Step 2: Create Virtual Environment (Recommended)

```powershell
# Navigate to project directory
cd F:\CodeTests\AiPoc

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get an execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# This will install:
# - FastAPI and Uvicorn (web framework)
# - Pydantic (data validation)
# - SQLAlchemy (database support)
# - LXML (XML processing)
# - FHIR resources (FHIR support)
# - Testing tools (pytest)
# - And all other dependencies
```

### Step 4: Configure Environment

```powershell
# Copy the example environment file
copy .env.example .env

# Edit .env if needed (optional for PoC)
notepad .env
```

### Step 5: Verify Installation

```powershell
# Test imports
python -c "import fastapi; import pydantic; print('✓ Dependencies installed successfully')"

# Check project structure
python -c "import os; print('✓ Project structure OK' if os.path.exists('main.py') else '✗ main.py not found')"
```

### Step 6: Run the Application

```powershell
# Start the server
python main.py

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

### Step 7: Verify API is Running

**Option 1: Browser**
- Open: http://localhost:8000
- Should see API information

**Option 2: Interactive Docs**
- Open: http://localhost:8000/docs
- Should see Swagger UI

**Option 3: Command Line**
```powershell
# Test health endpoint
curl http://localhost:8000/health

# Or using PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/health" | Select-Object -Expand Content
```

### Step 8: Run Example Test

```powershell
# Run the test script
python examples/test_api.py all

# This will:
# 1. Test health check
# 2. Validate trial spec
# 3. Generate protocol
# 4. Export to multiple formats
# 5. List protocols
```

### Step 9: View Generated Files

After running the test, check the `examples/` folder:
```powershell
# List generated files
ls examples/

# You should see:
# - example_response.json (full generated protocol)
# - *_ODM.xml (CDISC ODM export)
# - *_FHIR.json (FHIR export)
# - *_DataDictionary.csv (CSV export)
```

## Alternative: Docker Installation

If you prefer Docker:

```powershell
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop containers
docker-compose down
```

## Troubleshooting

### Issue: "Import error: pydantic_settings"
**Solution:**
```powershell
pip install --upgrade pydantic pydantic-settings
```

### Issue: "Port 8000 already in use"
**Solution:**
```powershell
# Option 1: Use different port
uvicorn main:app --port 8001

# Option 2: Find and stop process using port 8000
netstat -ano | findstr :8000
# Note the PID and kill it
taskkill /PID <PID> /F
```

### Issue: "Module not found"
**Solution:**
```powershell
# Ensure you're in the correct directory
cd F:\CodeTests\AiPoc

# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Permission denied" when activating venv
**Solution:**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Dependencies take too long to install
**Solution:**
```powershell
# Use a minimal install for testing (without ML libraries)
pip install fastapi uvicorn pydantic pydantic-settings python-multipart
pip install lxml jinja2 sqlalchemy python-dotenv

# This installs core dependencies only
# Skip TensorFlow, transformers, etc. for PoC testing
```

## Verification Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Server starts without errors (`python main.py`)
- [ ] Interactive docs accessible (http://localhost:8000/docs)
- [ ] Health endpoint responds (http://localhost:8000/health)
- [ ] Example test runs successfully (`python examples/test_api.py all`)
- [ ] Export files generated in `examples/` folder

## Quick Test Commands

```powershell
# 1. Health check
curl http://localhost:8000/health

# 2. Generate protocol (short version)
curl -X POST http://localhost:8000/api/v1/generate `
  -H "Content-Type: application/json" `
  -d '{
    "sponsor": "Test Pharma",
    "title": "Test Study",
    "indication": "Test Disease",
    "phase": "Phase 2",
    "design": "randomized, double-blind",
    "sample_size": 100,
    "duration_weeks": 12,
    "key_endpoints": [{"type": "primary", "name": "Test endpoint"}],
    "inclusion_criteria": ["Age 18-65"],
    "exclusion_criteria": ["Pregnancy"],
    "region": "US"
  }'

# 3. List protocols
curl http://localhost:8000/api/v1/protocols
```

## Performance Notes

- **First request**: May take 2-3 seconds (FastAPI initialization)
- **Subsequent requests**: ~100-500ms typical response time
- **Generation time**: ~500ms for typical protocol
- **Memory usage**: ~200-300 MB for PoC version

## Development Mode

```powershell
# Run with auto-reload for development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests with pytest
pytest tests/ -v

# Run with debug logging
uvicorn main:app --reload --log-level debug
```

## Production Deployment

For production deployment:
1. Set `API_ENVIRONMENT=production` in .env
2. Use a proper database (PostgreSQL)
3. Set up authentication
4. Configure HTTPS/TLS
5. Use a production ASGI server (Gunicorn + Uvicorn workers)
6. Set up monitoring and logging
7. Configure rate limiting
8. Set proper CORS origins

## Next Steps After Installation

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Try the examples**: Run `python examples/test_api.py all`
3. **Read the docs**: Check README.md and QUICKSTART.md
4. **Customize**: Edit `examples/example_request.json` and generate
5. **Review outputs**: Check generated files in `examples/`
6. **Plan integration**: Consider how to integrate with your systems

## Getting Help

- **Documentation**: README.md, QUICKSTART.md, ARCHITECTURE.md
- **API Docs**: http://localhost:8000/docs (when server is running)
- **Example Files**: Check `examples/` folder
- **Test Script**: `examples/test_api.py` shows all API usage

## Minimum System Requirements

- **OS**: Windows 10+, macOS 10.14+, Linux
- **Python**: 3.9 or higher
- **RAM**: 2 GB minimum (4 GB recommended)
- **Disk**: 1 GB free space
- **Network**: Internet connection for pip install

## Recommended System

- **Python**: 3.11 or 3.12
- **RAM**: 8 GB
- **CPU**: Multi-core processor
- **Disk**: SSD with 5 GB free space

---

**You're all set! Start the server with `python main.py` and visit http://localhost:8000/docs**
