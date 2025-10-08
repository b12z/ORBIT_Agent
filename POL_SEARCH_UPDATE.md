# $POL KOL Search Update

## ✅ Changes Made

Updated the scraper to search for `$POL KOL` posts with engagement thresholds:
- **Cashtag**: `$POL` (Polygon token mentions)
- **KOL terms**: `KOL OR "key opinion leader" OR influencer`
- **Min Replies**: 10
- **Min Favorites**: 10

---

## 🔍 Search Query Structure

### X API v2 Query
```
($POL) (KOL OR "key opinion leader" OR influencer) min_replies:10 min_faves:10 -is:reply -is:retweet
```

### Breakdown
1. **Topics**: `($POL)` - Searches for tweets mentioning $POL
2. **KOL Terms**: `(KOL OR "key opinion leader" OR influencer)` - Must contain KOL-related terms
3. **Engagement**: `min_replies:10 min_faves:10` - Server-side filtering for engagement
4. **Exclusions**: `-is:reply -is:retweet` - No replies or retweets

---

## 📝 Updated Files

### 1. `src/x_search.py`
- ✅ Added `min_replies` and `min_faves` parameters to `search_kol_recent()`
- ✅ Server-side engagement filtering using X API v2 operators
- ✅ Client-side validation as backup
- ✅ Added engagement metrics to results (`reply_count`, `like_count`)
- ✅ Better logging showing query and results

### 2. `src/dev_once.py`
- ✅ Changed default topic from `web3 growth,KOL,gaming` to `$POL`
- ✅ Added `MIN_REPLIES` env var (default: 10)
- ✅ Added `MIN_FAVES` env var (default: 10)
- ✅ Added `SEARCH_HOURS` env var (default: 12)
- ✅ Passes engagement parameters to search function

### 3. `.github/workflows/schedule-3x.yml`
- ✅ Changed default TOPICS from `web3` to `$POL`
- ✅ Added `MIN_REPLIES` workflow variable (default: 10)
- ✅ Added `MIN_FAVES` workflow variable (default: 10)
- ✅ Added `SEARCH_HOURS` workflow variable (default: 12)

---

## 🚀 How to Use

### Local Testing

**1. Test query structure (no API calls):**
```bash
python test_pol_search.py
```

**2. Test with real API (1 API call):**
```bash
python test_pol_search.py --live
```

**3. Run full flow with OpenAI (dry run):**
```bash
. .venv/bin/activate
TOPICS="$POL" DRY_RUN=true MAX_POSTS=1 python -m src.smoke_scrape
```

**4. Use Makefile:**
```bash
# Dry run (no posting)
make smoke-dry TOPICS=$POL

# Real run (will post)
make smoke TOPICS=$POL
```

---

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TOPICS` | `$POL` | Search topics (cashtags, hashtags, keywords) |
| `MIN_REPLIES` | `10` | Minimum number of replies required |
| `MIN_FAVES` | `10` | Minimum number of likes/favorites required |
| `SEARCH_HOURS` | `12` | Time window in hours |
| `MAX_POSTS` | `1` | Maximum number of posts to process |
| `DRY_RUN` | `true` | If true, don't actually post |

---

### Custom Search Examples

**Search for $ETH KOL posts:**
```bash
TOPICS="$ETH" python -m src.smoke_scrape
```

**Multiple topics:**
```bash
TOPICS="$POL,$MATIC" python -m src.smoke_scrape
```

**Higher engagement threshold:**
```bash
TOPICS="$POL" MIN_REPLIES=50 MIN_FAVES=100 python -m src.smoke_scrape
```

**Longer time window:**
```bash
TOPICS="$POL" SEARCH_HOURS=24 python -m src.smoke_scrape
```

---

## 📊 Filter Logic

### Server-Side (X API v2)
These filters are applied by Twitter's API before results are returned:
- ✅ `min_replies:10` - Tweets with at least 10 replies
- ✅ `min_faves:10` - Tweets with at least 10 likes
- ✅ `-is:reply` - Exclude reply tweets
- ✅ `-is:retweet` - Exclude retweets

### Client-Side (Python)
Additional validation after receiving results:
- ✅ Followers >= 10,000
- ✅ Reply count >= min_replies (double-check)
- ✅ Like count >= min_faves (double-check)
- ✅ Created within time window (hours)
- ✅ Valid tweet ID and text

---

## 🔍 X API v2 Operators Reference

| Operator | Example | Description |
|----------|---------|-------------|
| Cashtag | `$POL` | Search for token mentions |
| Hashtag | `#web3` | Search for hashtags |
| Text | `KOL` | Search for text matches |
| Quoted phrase | `"key opinion leader"` | Exact phrase match |
| OR | `KOL OR influencer` | Match any term |
| AND | `$POL KOL` | Match all terms (implicit) |
| Exclude | `-is:reply` | Exclude matches |
| Min replies | `min_replies:10` | Minimum reply count |
| Min favorites | `min_faves:10` | Minimum like count |
| Min retweets | `min_retweets:10` | Minimum retweet count |

---

## 🧪 Testing Results

### Query Structure Test ✅
```bash
$ python test_pol_search.py

Generated X API v2 Query:
($POL) (KOL OR "key opinion leader" OR influencer) min_replies:10 min_faves:10 -is:reply -is:retweet

✅ Query structure validated
```

### OpenAI Flow Test ✅
```bash
$ python test_openai_flow.py

✅ Loaded .env.local
✅ OPENAI_API_KEY present
✅ Reply writer loaded
✅ Generated 2/2 replies successfully
```

---

## 📈 Rate Limit Impact

### Before (Generic Search)
- Query: `(web3 OR gaming) (KOL OR influencer) -is:reply -is:retweet`
- Results: Many low-engagement posts
- Needed client-side filtering

### After ($POL KOL with Engagement)
- Query: `($POL) (KOL OR influencer) min_replies:10 min_faves:10 -is:reply -is:retweet`
- Results: Only high-engagement KOL posts
- More targeted, fewer API calls needed

**Impact**: ✅ Same API quota usage, better quality results

---

## 🎯 Expected Results

Tweets matching all criteria:
1. ✅ Mentions `$POL` (Polygon token)
2. ✅ Contains KOL-related terms
3. ✅ Has at least 10 replies
4. ✅ Has at least 10 likes
5. ✅ From accounts with 10k+ followers
6. ✅ Posted within last 12 hours (configurable)
7. ✅ Not a reply or retweet

---

## 🔧 GitHub Actions Configuration

### Repository Variables (Optional)
Go to: **Settings → Secrets and variables → Actions → Variables**

| Variable | Default | Customize |
|----------|---------|-----------|
| `TOPICS` | `$POL` | Other tokens or topics |
| `MIN_REPLIES` | `10` | Increase for more selective |
| `MIN_FAVES` | `10` | Increase for viral posts |
| `SEARCH_HOURS` | `12` | Increase for broader search |

**Note**: If not set, defaults will be used.

---

## ✅ Verification Checklist

- [x] Query structure uses correct X API v2 syntax
- [x] Cashtag `$POL` is properly formatted
- [x] Engagement operators (`min_replies`, `min_faves`) are included
- [x] KOL terms are in query
- [x] Client-side validation matches server filters
- [x] Results include engagement metrics
- [x] Environment variables are configurable
- [x] GitHub Actions workflow updated
- [x] Local testing scripts created
- [x] Documentation complete

---

## 🚀 Next Steps

1. **Test locally:**
   ```bash
   python test_pol_search.py
   ```

2. **Test with real API (1 request):**
   ```bash
   python test_pol_search.py --live
   ```

3. **Deploy to GitHub Actions:**
   - Credentials already added ✅
   - Run workflow manually first
   - Monitor results

4. **Customize if needed:**
   - Adjust `MIN_REPLIES` / `MIN_FAVES` thresholds
   - Change `TOPICS` to other tokens
   - Modify `SEARCH_HOURS` window

---

## 📚 Resources

- **X API v2 Search Syntax**: [developer.twitter.com/en/docs/twitter-api/tweets/search](https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query)
- **Rate Limits**: 450 requests per 15 minutes (v2 Search endpoint)
- **Our Usage**: ~2-3 requests per run, 3x daily = ~9 requests/day (< 1% of quota)

