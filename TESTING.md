# Safe API Testing Guide

This guide helps you test the X API integration safely without hitting rate limits.

## The Problem

The GitHub Actions workflow is failing with:
```
x_search KOL error: 401 {'title': 'Unauthorized', ...}
x_search error: 401 {'title': 'Unauthorized', ...}
```

This means the X API credentials are either:
1. Not configured in GitHub Secrets
2. Invalid or expired
3. Lack proper permissions

## Recommended Testing Approach

### Step 1: Validate Credentials (NO API calls)

First, verify your credentials are present:

```bash
# Local testing
python -m src.validate_x_auth

# With custom env file
python -m src.validate_x_auth
```

This checks:
- ✅ All required environment variables are set
- ✅ Credentials work with a minimal API call (`/users/me`)
- ✅ Current rate limit status

**Rate Limit Cost: 1 request** (safest option)

---

### Step 2: Test with Mock Data (NO API calls)

Test your flow logic without touching the API:

```bash
TEST_MODE=mock python -m src.test_scrape_safe
```

This:
- Uses fake tweet data
- Tests reply generation
- Verifies flow logic
- **Costs: 0 API requests** ✅

---

### Step 3: Minimal API Test (1 request)

Make ONE real API call to verify everything works:

```bash
TEST_MODE=minimal python -m src.test_scrape_safe
```

**Rate Limit Cost: 1 request**

---

### Step 4: Limited Full Test (2-3 requests)

Test the complete flow with minimal API usage:

```bash
TEST_MODE=limited TOPICS=web3 MAX_POSTS=1 DRY_RUN=true python -m src.test_scrape_safe
```

**Rate Limit Cost: 2-3 requests**

---

## Required Environment Variables

### For OAuth 1.0a (used by `smoke_scrape.py`):

```bash
API_KEY=your_api_key
API_KEY_SECRET=your_api_key_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_SECRET=your_access_secret
```

### For OpenAI (reply generation):

```bash
OPENAI_API_KEY=your_openai_key
```

---

## GitHub Actions Setup

### Configure Secrets

Go to: **Settings → Secrets and variables → Actions**

Add these **Repository Secrets**:

1. `X_API_KEY` - Your X API Consumer Key
2. `X_API_KEY_SECRET` - Your X API Consumer Secret  
3. `X_ACCESS_TOKEN` - Your X Access Token
4. `X_ACCESS_SECRET` - Your X Access Token Secret
5. `OPENAI_API_KEY` - Your OpenAI API key

### Test in GitHub Actions

Once secrets are configured, trigger manually:

```bash
# Via GitHub UI:
Actions → Schedule 3x Autopost → Run workflow

# Or via CLI:
gh workflow run schedule-3x.yml
```

---

## Troubleshooting

### 401 Unauthorized Error

**Possible causes:**

1. **Missing credentials** in GitHub Secrets
   - ✅ Solution: Add all required secrets
   
2. **Expired tokens**
   - ✅ Solution: Regenerate tokens in X Developer Portal
   
3. **Wrong API access level**
   - ✅ Solution: Ensure you have v2 API access (requires Elevated access)

4. **Revoked app permissions**
   - ✅ Solution: Check app permissions in X Developer Portal

### How to Get New Credentials

1. Go to [developer.twitter.com](https://developer.twitter.com)
2. Navigate to your app
3. Go to "Keys and tokens" tab
4. Regenerate tokens if needed
5. Ensure you have **OAuth 1.0a** enabled
6. Copy all 4 credentials

### Rate Limit Status

X API v2 rate limits (Free tier):
- `/tweets/search/recent`: **450 requests per 15 min**
- `/users/me`: **75 requests per 15 min**

Our workflow uses ~2-3 requests per run, so:
- **Safe frequency**: Every 8 hours (3x daily) ✅
- **Maximum frequency**: Every 2-3 minutes (not recommended)

---

## Best Practices

### ✅ DO:
- Start with `validate` mode
- Use `mock` mode for development
- Test locally before pushing
- Keep `MAX_POSTS=1` for testing
- Use `DRY_RUN=true` initially

### ❌ DON'T:
- Run without validating credentials first
- Test directly in production
- Set high `MAX_POSTS` values
- Skip mock testing
- Ignore 429 rate limit errors

---

## Quick Reference

| Test Mode | API Calls | Use Case |
|-----------|-----------|----------|
| `validate` | 1 | Check credentials work |
| `mock` | 0 | Test flow logic |
| `minimal` | 1 | Verify API access |
| `limited` | 2-3 | Full integration test |

---

## Example Workflow

```bash
# 1. Validate credentials
python -m src.validate_x_auth

# 2. Test with mocks
TEST_MODE=mock python -m src.test_scrape_safe

# 3. Single API test
TEST_MODE=minimal python -m src.test_scrape_safe

# 4. Full test (dry run)
TEST_MODE=limited DRY_RUN=true python -m src.test_scrape_safe

# 5. Deploy to GitHub Actions
git add .
git commit -m "Fix credentials"
git push

# 6. Test in Actions (manually trigger first)
```

---

## Support

If you continue to see 401 errors after:
1. ✅ Validating credentials locally
2. ✅ Setting GitHub Secrets
3. ✅ Regenerating tokens

Then check:
- X API access level (need Elevated for v2)
- App permissions (read + write)
- Token expiration dates
- IP restrictions (if any)

