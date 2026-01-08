# Setting Up the Clean Project

This is a clean version of the project with all secrets and sensitive data removed. Follow these steps to set it up:

## 1. Set Up Environment Variables

Copy the example environment file and add your own secrets:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` and add your configuration:

```env
# Generate a secure SECRET_KEY (never use the default!)
SECRET_KEY=your-generated-secret-key-here

# Optional: Add OpenAI API key for LLM features
OPENAI_API_KEY=sk-your-key-here

# Database password (change from default!)
POSTGRES_PASSWORD=your-secure-password
```

### Generate a Secure Secret Key

```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or using openssl
openssl rand -hex 32
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Initialize the Database

First time only - seed the RAG database with sample protocols:

```bash
python examples/seed_rag_direct.py
```

## 4. Run the Application

### Quick Launch (Web UI)
```bash
python launch_web.py
```

### API Server Only
```bash
python main.py
```

### Using Docker
```bash
# Set environment variables first!
docker-compose up
```

## Important Security Notes

⚠️ **NEVER commit your `.env` file to Git!**

The `.gitignore` file is already configured to exclude:
- `.env` and `.env.local`
- Database files
- Vector database
- Models directory
- Cache files

✅ **Before deploying to production:**
1. Read [SECURITY.md](SECURITY.md) for complete security guidelines
2. Change all default passwords
3. Generate a new SECRET_KEY
4. Use HTTPS
5. Enable proper authentication
6. Review CORS settings

## Getting Started

For detailed documentation, see:
- [README.md](README.md) - Main documentation
- [SECURITY.md](SECURITY.md) - Security guidelines
- [CONFIGURATION.md](docs/CONFIGURATION.md) - Configuration options
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide

## Questions?

If you have questions or find security issues, please:
1. For security issues: Contact maintainers directly (do not open public issues)
2. For general questions: Open a GitHub issue
