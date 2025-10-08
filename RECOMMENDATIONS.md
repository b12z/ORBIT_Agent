# Recommendations: Fix 401 & Avoid Rate Limits

## 🎯 Executive Summary

**Problem**: Your GitHub Actions workflow gets 401 Unauthorized from X API  
**Root Cause**: Invalid/missing OAuth1 credentials  
**Solution**: Validate credentials + add proper secrets + use safe testing  
**Risk Level**: ✅ LOW - Our approach uses minimal API calls  

---

## 🔍 What I Found

### The Error
```
x_search KOL error: 401 {'title': 'Unauthorized', 'type': 'about:blank', 'status': 401, 'detail': 'Unauthorized'}
```

### Root Causes
1. **Missing GitHub Secrets**: The workflow expects these secrets:
   - `X_API_KEY` (not set or expired)
   - `X_API_KEY_SECRET` (not set or expired)
   - `X_ACCESS_TOKEN` (not set or expired)
   - `X_ACCESS_SECRET` (not set or expired)

2. **Workflow Configuration**: `schedule-3x.yml` uses OAuth1, but credentials aren't valid

3. **No Validation**: Workflow jumps straight to API calls without checking auth first

---

## ✅ What I Built For You

### 1. Credential Validator (`validate_x_auth.py`)
- ✅ Checks all required env vars are present
- ✅ Tests auth with minimal API call (1 request)
- ✅ Shows rate limit status
- ✅ Provides clear error messages

**Usage:**
```bash
python -m src.validate_x_auth
```

### 2. Safe Testing Tool (`test_scrape_safe.py`)
Four test modes with increasing API usage:

| Mode | API Calls | Use Case |
|------|-----------|----------|
| `validate` | 1 | Check credentials only |
| `mock` | 0 | Test logic with fake data |
| `minimal` | 1 | Verify API access |
| `limited` | 2-3 | Full flow test |

**Usage:**
```bash
TEST_MODE=validate python -m src.test_scrape_safe
TEST_MODE=mock python -m src.test_scrape_safe
TEST_MODE=minimal python -m src.test_scrape_safe
TEST_MODE=limited python -m src.test_scrape_safe
```

### 3. Improved Error Handling (`x_search.py`)
- ✅ Validates credentials before use
- ✅ Better error messages with helpful hints
- ✅ Rate limit detection and retry logic
- ✅ Context-aware troubleshooting tips

### 4. GitHub Actions Test Workflow (`test-x-api.yml`)
- ✅ Validates credentials safely
- ✅ Runs mock tests (0 API calls)
- ✅ Minimal API test (1 call)
- ✅ Can be triggered manually

### 5. Documentation
- ✅ `QUICKSTART.md` - Fast solution guide
- ✅ `TESTING.md` - Complete testing guide
- ✅ `RECOMMENDATIONS.md` - This file

---

## 🚀 Recommended Action Plan

### Phase 1: Local Validation (5 minutes)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env.local with your credentials
cat > .env.local << EOF
API_KEY=your_consumer_key
API_KEY_SECRET=your_consumer_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_SECRET=your_access_token_secret
OPENAI_API_KEY=your_openai_key
EOF

# 3. Validate credentials
python -m src.validate_x_auth
```

**Expected output:**
```
✅ Authentication successful!
   Authenticated as: @your_username
```

If this fails → Fix credentials before proceeding to Phase 2

---

### Phase 2: Configure GitHub Secrets (2 minutes)

1. Go to your repo on GitHub
2. Settings → Secrets and variables → Actions
3. Add these **Repository Secrets**:
   - `X_API_KEY`
   - `X_API_KEY_SECRET`
   - `X_ACCESS_TOKEN`
   - `X_ACCESS_SECRET`
   - `OPENAI_API_KEY`

Get credentials from: [developer.twitter.com](https://developer.twitter.com) → Your App → Keys & Tokens

---

### Phase 3: Test in GitHub Actions (3 minutes)

```bash
# Option 1: GitHub UI
# Go to Actions → "Test X API Credentials" → Run workflow

# Option 2: GitHub CLI
gh workflow run test-x-api.yml

# Check status
gh run list --workflow=test-x-api.yml --limit 1

# View logs
gh run view --log
```

**Expected:** All steps pass ✅

---

### Phase 4: Enable Production Workflow

Once testing passes:

1. ✅ Verify `schedule-3x.yml` has correct secret names
2. ✅ Trigger manually first time
3. ✅ Check logs for any errors
4. ✅ Let it run on schedule (3x daily)

---

## 📊 Rate Limit Analysis

### Current X API v2 Limits (Free/Basic Tier)
- `/tweets/search/recent`: **450 requests per 15 min**
- `/users/me`: **75 requests per 15 min**

### Your Workflow Usage
- **Per run**: 2-3 API requests
- **Schedule**: 3x daily (every 8 hours)
- **Daily usage**: ~6-9 requests
- **% of limit**: < 1%

### Safety Margin
```
Daily requests:     9
Daily limit:        43,200 (450 * 96 intervals)
Usage:              0.02%
Cushion:            99.98%
```

**Conclusion**: ✅ **Extremely safe** - You could run 100x more frequently

---

## ⚠️ Rate Limit Best Practices

### ✅ DO:
1. **Always validate credentials first**
   - Use `validate_x_auth.py` before deployment
   - Check rate limits proactively

2. **Use mock testing for development**
   - Test logic without API calls
   - Save rate limit quota for production

3. **Monitor for 429 errors**
   - Workflow has automatic retry logic
   - Backs off exponentially on rate limits

4. **Start with dry runs**
   - Use `DRY_RUN=true` for testing
   - Only set to `false` when confident

5. **Check rate limits periodically**
   ```bash
   python -m src.validate_x_auth
   # Shows current rate limit status
   ```

### ❌ DON'T:
1. **Skip credential validation**
   - Always test locally first
   - Never assume GitHub secrets are correct

2. **Test directly in production**
   - Use `test-x-api.yml` workflow first
   - Verify locally before GitHub Actions

3. **Ignore error messages**
   - 401 = Fix credentials
   - 403 = Check permissions/access level
   - 429 = Rate limited (wait for reset)

4. **Bypass dry runs**
   - Always test with `DRY_RUN=true` first
   - Verify output before posting

5. **Set high MAX_POSTS**
   - Start with 1
   - Only increase when confident

---

## 🔧 Troubleshooting Guide

### Issue: 401 Unauthorized

**Symptoms:**
```
x_search KOL error: 401 {'title': 'Unauthorized', ...}
```

**Solutions:**
1. ✅ Run `python -m src.validate_x_auth` locally
2. ✅ Check credentials are correct
3. ✅ Regenerate tokens if needed
4. ✅ Verify GitHub Secrets are set
5. ✅ Check API access level (need Elevated)

---

### Issue: 403 Forbidden

**Symptoms:**
```
x_search error: 403 {'title': 'Forbidden', ...}
```

**Solutions:**
1. ✅ Check X API access level (Essential vs Elevated vs Premium)
2. ✅ Verify app permissions (need Read + Write)
3. ✅ Check if app is suspended
4. ✅ Ensure OAuth1 is enabled

---

### Issue: 429 Rate Limited

**Symptoms:**
```
x_search error: 429 {'title': 'Too Many Requests', ...}
```

**Solutions:**
1. ✅ Wait for rate limit reset (shown in error)
2. ✅ Check current limits: `python -m src.validate_x_auth`
3. ✅ Reduce frequency if needed
4. ✅ Workflow has automatic retry logic

**Note**: Very unlikely with your current usage (< 1% of quota)

---

## 📈 Next Steps

### Immediate (Today)
- [ ] Run `python -m src.validate_x_auth` locally
- [ ] Fix any credential issues
- [ ] Add secrets to GitHub
- [ ] Run `test-x-api.yml` workflow
- [ ] Verify all tests pass

### Short-term (This Week)
- [ ] Trigger `schedule-3x.yml` manually
- [ ] Monitor first few runs
- [ ] Check rate limit status
- [ ] Verify posts are working
- [ ] Let scheduled runs continue

### Long-term (Ongoing)
- [ ] Monitor for 401/403/429 errors
- [ ] Check rate limits monthly
- [ ] Rotate credentials periodically
- [ ] Update documentation as needed

---

## 💡 Pro Tips

1. **Always test locally first**
   - Saves GitHub Actions minutes
   - Faster debugging
   - Better error messages

2. **Use mock mode for rapid iteration**
   - Test logic changes instantly
   - No API quota consumption
   - Safe for experimentation

3. **Monitor rate limits proactively**
   - Run validator weekly
   - Check before major changes
   - Know your quota status

4. **Keep credentials secure**
   - Never commit to git
   - Use GitHub Secrets
   - Rotate periodically

5. **Document credential sources**
   - Note where each secret came from
   - Include regeneration instructions
   - Update when credentials change

---

## 📚 Additional Resources

- **X API Documentation**: [developer.twitter.com/en/docs](https://developer.twitter.com/en/docs)
- **Rate Limits**: [developer.twitter.com/en/docs/twitter-api/rate-limits](https://developer.twitter.com/en/docs/twitter-api/rate-limits)
- **OAuth 1.0a**: [developer.twitter.com/en/docs/authentication/oauth-1-0a](https://developer.twitter.com/en/docs/authentication/oauth-1-0a)

---

## 🎉 Summary

You now have:
- ✅ Credential validation tool
- ✅ Safe testing framework
- ✅ Improved error handling
- ✅ GitHub Actions test workflow
- ✅ Complete documentation
- ✅ Rate limit protection

**Rate Limit Risk**: ✅ **MINIMAL** (< 1% quota usage)  
**Safety Level**: ✅ **MAXIMUM** (validates before running)  
**Time to Fix**: ⏱️ **10 minutes** (follow Phase 1-3)

**Next Action**: Run `python -m src.validate_x_auth` 🚀

