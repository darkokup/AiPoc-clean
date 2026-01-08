# Security Guidelines

## Before Deploying to Production

### 1. Environment Variables

**CRITICAL**: Never commit secrets to version control. All sensitive data must be in environment variables.

Required environment variables:
- `SECRET_KEY` - Generate a strong random key (e.g., using `openssl rand -hex 32`)
- `OPENAI_API_KEY` - Your OpenAI API key (if using LLM features)
- `POSTGRES_PASSWORD` - Strong database password (if using PostgreSQL)
- `DATABASE_URL` - Full database connection string with credentials

### 2. Generate Secure Keys

```bash
# Generate a secure SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or using openssl
openssl rand -hex 32
```

### 3. File Permissions

Ensure `.env` files are never committed:
- `.env` is in `.gitignore`
- Set restrictive permissions: `chmod 600 .env` (Unix/Linux)

### 4. Database Security

- Never use default passwords
- Use strong, unique passwords
- Enable SSL/TLS for database connections in production
- Restrict database access by IP when possible

### 5. API Security

- Change `SECRET_KEY` from default value
- Use HTTPS in production
- Implement rate limiting
- Enable CORS only for trusted domains

### 6. Docker Security

- Don't expose unnecessary ports
- Use Docker secrets for sensitive data
- Run containers as non-root user
- Regularly update base images

## Reporting Security Issues

If you discover a security vulnerability, please email the maintainers directly. Do not open a public issue.

## Security Checklist

Before going to production:

- [ ] Changed all default passwords
- [ ] Generated new SECRET_KEY
- [ ] Set up OPENAI_API_KEY if using LLM features
- [ ] Configured environment variables (not hardcoded)
- [ ] Enabled HTTPS
- [ ] Configured proper CORS settings
- [ ] Set up database with strong password
- [ ] Reviewed and restricted API access
- [ ] Enabled logging and monitoring
- [ ] Configured backup strategy
