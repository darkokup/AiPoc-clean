# Contributing to Clinical Trial Protocol Generator

Thank you for considering contributing to this project! This document provides guidelines for contributing.

## Security First

⚠️ **CRITICAL**: Never commit secrets, API keys, passwords, or sensitive data to the repository.

Before committing:
- [ ] Review your changes for hardcoded secrets
- [ ] Ensure `.env` files are in `.gitignore`
- [ ] Use environment variables for all sensitive data
- [ ] Run `git diff` to check what you're about to commit

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Follow [SETUP.md](SETUP.md) to configure your environment
4. Create a new branch for your feature/fix

## Development Workflow

### Setting Up Your Development Environment

```bash
# Clone your fork
git clone https://github.com/your-username/project-name.git
cd project-name

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up your .env file (NEVER commit this!)
cp .env.example .env
# Edit .env with your own keys
```

### Making Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes
   - Write clean, documented code
   - Follow existing code style
   - Add tests for new features
   - Update documentation as needed

3. Test your changes:
   ```bash
   # Run tests
   pytest tests/

   # Run specific tests
   pytest tests/test_your_feature.py
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

### Commit Message Guidelines

Use conventional commits format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

Example:
```
feat: add RAG integration for protocol generation

- Implemented ChromaDB vector store
- Added semantic search functionality
- Updated generation pipeline to use RAG
```

### Submitting a Pull Request

1. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Go to the original repository on GitHub

3. Click "New Pull Request"

4. Select your fork and branch

5. Fill in the PR template:
   - Describe what changes you made
   - Why you made them
   - How to test them
   - Link any related issues

6. Submit the PR

## Code Review Process

- Maintainers will review your PR
- Address any feedback or requested changes
- Once approved, your PR will be merged

## Coding Standards

### Python Style
- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and small
- Use meaningful variable names

### File Organization
```
app/
├── services/       # Business logic
├── models/         # Data models
└── __init__.py

tests/              # Test files
docs/               # Documentation
examples/           # Example scripts
```

### Testing
- Write tests for new features
- Maintain test coverage
- Test edge cases
- Use pytest fixtures for setup

### Documentation
- Update README.md if adding features
- Add docstrings to new functions
- Update relevant docs/ files
- Include examples where helpful

## Types of Contributions

### Bug Reports
- Use GitHub Issues
- Describe the bug clearly
- Include steps to reproduce
- Share error messages and logs
- Mention your environment (OS, Python version)

### Feature Requests
- Use GitHub Issues
- Explain the use case
- Describe the desired behavior
- Consider implementation approaches

### Code Contributions
- Bug fixes
- New features
- Performance improvements
- Documentation improvements
- Test coverage improvements

### Documentation
- Fix typos or clarify unclear sections
- Add examples
- Improve setup instructions
- Translate documentation

## Security Issues

🔒 **DO NOT** open public issues for security vulnerabilities.

Instead:
1. Email the maintainers directly
2. Include details about the vulnerability
3. Wait for a response before disclosure
4. Allow time for a fix to be developed

## Questions?

- Open a GitHub Discussion for questions
- Check existing issues before creating new ones
- Be respectful and constructive

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Thank You!

Your contributions help make this project better for everyone. We appreciate your time and effort! 🎉
