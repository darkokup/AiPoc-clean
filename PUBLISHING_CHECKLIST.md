# GitHub Publishing Checklist

Follow this checklist to safely publish the clean version to GitHub.

## Pre-Publishing Checks

- [x] Clean copy created at `f:\CodeTests\AiPoc-clean`
- [x] All secrets removed and replaced with environment variables
- [x] Security documentation added
- [x] .gitignore properly configured
- [ ] Final review of all files completed

## Final Review (DO THIS NOW)

```bash
cd f:\CodeTests\AiPoc-clean

# Search for potential secrets one more time
grep -r "sk-" . --exclude-dir=.git
grep -r "api[_-]key.*=.*['\"]" . --exclude-dir=.git
grep -r "password.*=.*['\"]" . --exclude-dir=.git
```

Windows PowerShell:
```powershell
cd f:\CodeTests\AiPoc-clean

# Search for potential secrets
Select-String -Path * -Pattern "sk-" -Exclude *.md
Select-String -Path * -Pattern "api.*key.*=.*[`"']" -Exclude *.md
```

## Publishing Steps

### 1. Initialize Git Repository

```bash
cd f:\CodeTests\AiPoc-clean
git init
git add .
git status  # Review what will be committed
```

**STOP**: Review the `git status` output. Make sure:
- No `.env` files are staged
- No database files are staged
- No secrets are staged

### 2. Create Initial Commit

```bash
git commit -m "Initial commit - AI-Powered Clinical Trial Protocol Generator

- RAG + LLM enhanced protocol generation
- Multi-format export (ODM, FHIR, CSV)
- Clinical validation rules
- Web UI and REST API
- Comprehensive security documentation"
```

### 3. Create GitHub Repository

1. Go to https://github.com/new
2. Choose repository name (e.g., `clinical-trial-protocol-generator`)
3. **DO NOT** check "Initialize this repository with a README"
4. Choose Public or Private
5. Click "Create repository"

### 4. Push to GitHub

```bash
# Replace with your repository URL
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git

git branch -M main
git push -u origin main
```

### 5. Configure GitHub Security

#### Enable Security Features
1. Go to repository Settings → Security & analysis
2. Enable:
   - ✅ Dependency graph
   - ✅ Dependabot alerts
   - ✅ Dependabot security updates
   - ✅ Secret scanning
   - ✅ Code scanning (CodeQL)

#### Add Branch Protection (Recommended)
1. Go to Settings → Branches
2. Add rule for `main` branch:
   - ✅ Require pull request reviews
   - ✅ Require status checks to pass
   - ✅ Require branches to be up to date

### 6. Customize Repository

#### Add Topics/Tags
Settings → Topics, add relevant tags:
- `clinical-trials`
- `protocol-generation`
- `rag`
- `llm`
- `healthcare`
- `fastapi`
- `python`
- `cdisc`
- `fhir`
- `ai`

#### Update Description
Add a short description in repository settings:
```
AI-powered clinical trial protocol generator using RAG + LLM. Generates structured protocols, EDC configurations, and exports to CDISC ODM, FHIR formats.
```

#### Add Website (Optional)
If you deploy a demo, add the URL in repository settings.

### 7. Create Release (Optional)

1. Go to Releases → Create a new release
2. Tag: `v0.1.0`
3. Title: `Initial Release - Clean Public Version`
4. Description:
   ```
   ## First Public Release
   
   Clean version of the Clinical Trial Protocol Generator with all secrets removed.
   
   ### Features
   - RAG + LLM enhanced protocol generation
   - Support for 1,159+ real protocol examples
   - Multi-format export (ODM, FHIR, CSV)
   - Clinical validation rules
   - Web UI and REST API
   
   ### Getting Started
   See [SETUP.md](SETUP.md) for installation instructions.
   
   ### Security
   This release includes comprehensive security documentation. 
   See [SECURITY.md](SECURITY.md) for guidelines.
   ```

### 8. Verify Publication

Clone your published repository in a fresh location and test:

```bash
cd /tmp  # or any test location
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME

# Follow SETUP.md instructions
cp .env.example .env
# Add your own keys to .env
pip install -r requirements.txt
python examples/seed_rag_direct.py
python launch_web.py
```

## Post-Publishing Tasks

### Documentation
- [ ] Add badges to README (build status, license, etc.)
- [ ] Create GitHub wiki (optional)
- [ ] Add examples to repository
- [ ] Create video tutorial (optional)

### Community
- [ ] Add LICENSE file (if not present)
- [ ] Add CODE_OF_CONDUCT.md
- [ ] Add issue templates
- [ ] Add discussion forum (GitHub Discussions)

### CI/CD
- [ ] Verify security workflow runs correctly
- [ ] Add test workflow
- [ ] Add deployment workflow (if applicable)

### Monitoring
- [ ] Watch for security alerts
- [ ] Monitor issues
- [ ] Respond to pull requests

## Important Reminders

⚠️ **NEVER push the original directory** (`f:\CodeTests\AiPoc`)

⚠️ **NEVER commit**:
- `.env` files
- API keys
- Passwords
- Database files with real data
- Personal information

✅ **ALWAYS**:
- Review changes before committing (`git diff`)
- Use environment variables for secrets
- Update .env.example when adding new config
- Follow security guidelines

## If Something Goes Wrong

### If you accidentally pushed secrets:

1. **Immediately rotate all exposed credentials**
   - Change API keys
   - Change passwords
   - Revoke tokens

2. **Contact GitHub Support**
   - Request cache clearing if needed
   - They can help remove sensitive data from history

3. **Do NOT try to fix with force push**
   - History remains in Git
   - Other clones may still have the secrets

4. **Create a new repository**
   - Use the clean copy
   - New repository with no history

5. **Learn from it**
   - Set up pre-commit hooks
   - Use secret scanning tools locally
   - Double-check before pushing

## Need Help?

- GitHub Docs: https://docs.github.com
- Git Basics: https://git-scm.com/doc
- Security Best Practices: See [SECURITY.md](SECURITY.md)

---

**Ready to publish?** Check all items above, then proceed with confidence! 🚀
