# Quick Start: Fix 401 Errors

## 🚨 Current Problem

Your GitHub Actions workflow is failing with:
```
401 {'title': 'Unauthorized', ...}
```

This means **X API credentials are missing or invalid**.

---

## ✅ Solution (3 Steps)

### Step 1: Test Credentials Locally

```bash
# Install dependencies if needed
pip install -r requirements.txt

# Validate your credentials
python -m src.validate_x_auth
```

**Expected output:**
```
✅ Authentication successful!
   Authenticated as: @your_username
```

If this fails, your credentials need to be fixed **before** trying GitHub Actions.

---

### Step 2: Configure GitHub Secrets

Go to: **GitHub → Your Repo → Settings → Secrets and variables → Actions**

Add these secrets:

| Secret Name | Description | Where to get it |
|------------|-------------|-----------------|
| `X_API_KEY` | Consumer Key | [developer.twitter.com](https://developer.twitter.com) → Your App → Keys & Tokens |
| `X_API_KEY_SECRET` | Consumer Secret | Same place |
| `X_ACCESS_TOKEN` | Access Token | Same place |
| `X_ACCESS_SECRET` | Access Token Secret | Same place |
| `OPENAI_API_KEY` | OpenAI Key | [platform.openai.com](https://platform.openai.com/api-keys) |

---

### Step 3: Test in GitHub Actions

```bash
# Via GitHub UI:
Actions → "Test X API Credentials" → Run workflow

# Or via GitHub CLI:
gh workflow run test-x-api.yml
```

This runs **safe tests** (only 2 API requests) to verify everything works.

---

## 📊 Rate Limit Safety

Our testing approach is **extremely conservative**:

| Test | API Calls | Risk Level |
|------|-----------|------------|
| `validate_x_auth` | 1 | ✅ Minimal |
| Mock test | 0 | ✅ None |
| Minimal test | 1 | ✅ Minimal |
| Limited test | 2-3 | ✅ Very Low |

**X API v2 limit**: 450 requests per 15 minutes  
**Our workflow**: ~2 requests per run  
**Safe to run**: Every few minutes (but we run 3x daily)

---

## 🔧 Troubleshooting

### Still getting 401 after setting secrets?

1. **Check API access level**
   - Go to [developer.twitter.com](https://developer.twitter.com)
   - Ensure you have **Elevated access** (not just Essential)
   - v2 endpoints require Elevated access

2. **Regenerate tokens**
   - Sometimes tokens expire or get revoked
   - Generate new ones in X Developer Portal
   - Update GitHub Secrets

3. **Verify app permissions**
   - Your app needs **Read and Write** permissions
   - Check in X Developer Portal → App Settings

4. **Local testing**
   ```bash
   # Create .env.local file with your credentials
   echo "API_KEY=your_key" > .env.local
   echo "API_KEY_SECRET=your_secret" >> .env.local
   echo "X_ACCESS_TOKEN=your_token" >> .env.local
   echo "X_ACCESS_SECRET=your_token_secret" >> .env.local
   
   # Test
   python -m src.validate_x_auth
   ```

---

## 📚 More Details

See [TESTING.md](TESTING.md) for:
- Complete testing guide
- All test modes
- Best practices
- Rate limiting details

---

## ⚡ Quick Commands

```bash
# Local validation
python -m src.validate_x_auth

# Mock test (no API)
TEST_MODE=mock python -m src.test_scrape_safe

# Safe API test
TEST_MODE=minimal python -m src.test_scrape_safe

# GitHub Actions test
gh workflow run test-x-api.yml

# Check workflow status
gh run list --workflow=test-x-api.yml

# View logs
gh run view --log
```

---

## 🎯 After Fixing

Once credentials work:

1. ✅ Local validation passes
2. ✅ GitHub Actions test passes
3. ✅ Enable `schedule-3x.yml` workflow
4. ✅ Monitor first few runs
5. ✅ Enjoy automated posting! 🚀

