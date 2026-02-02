# China Access Guide

## Problem: GitHub Raw URLs Blocked

When running this script from China, you may encounter:
- **Very slow downloads** from `raw.githubusercontent.com`
- **Connection timeouts** or failures
- **Empty or corrupted files**

This happens because GitHub's raw content domain is affected by the Great Firewall.

## Solution: Use jsDelivr CDN

jsDelivr is a free, open-source CDN that mirrors GitHub repositories and is **fully accessible from China**.

### Quick Usage

```bash
# Add --use-jsdelivr flag
./run.sh --use-jsdelivr

# Examples
./run.sh --use-jsdelivr                          # Generate all
./run.sh --use-jsdelivr --shadowrocket-china     # China media only
./run.sh --use-jsdelivr --shadowrocket-gfw       # GFW bypass only
```

## URL Conversion Reference

The `--use-jsdelivr` flag automatically converts these URLs:

### GFW List

**GitHub Raw (blocked/slow):**
```
https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt
```

**jsDelivr (China-accessible):**
```
https://cdn.jsdelivr.net/gh/gfwlist/gfwlist@master/gfwlist.txt
```

### Chinese App Rules

**GitHub Raw:**
```
https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/NetEaseMusic/NetEaseMusic.list
```

**jsDelivr:**
```
https://cdn.jsdelivr.net/gh/blackmatrix7/ios_rule_script@master/rule/Shadowrocket/NetEaseMusic/NetEaseMusic.list
```

## Pattern

```
GitHub:   raw.githubusercontent.com/{user}/{repo}/{branch}/{path}
jsDelivr: cdn.jsdelivr.net/gh/{user}/{repo}@{branch}/{path}
```

Notice: `/{branch}/` becomes `@{branch}/`

## Other China-Accessible Alternatives

If jsDelivr is also slow, you can manually edit `scripts/generate.py` and try:

### 1. Fastgit (China mirror)
```python
GFWLIST_URL = "https://raw.fastgit.org/gfwlist/gfwlist/master/gfwlist.txt"
BLACKMATRIX7_BASE = "https://raw.fastgit.org/blackmatrix7/ios_rule_script/master/rule"
```

### 2. GitClone (China mirror)
```python
GFWLIST_URL = "https://gitclone.com/github.com/gfwlist/gfwlist/raw/master/gfwlist.txt"
BLACKMATRIX7_BASE = "https://gitclone.com/github.com/blackmatrix7/ios_rule_script/raw/master/rule"
```

### 3. Statically (CDN)
```python
GFWLIST_URL = "https://cdn.statically.io/gh/gfwlist/gfwlist/master/gfwlist.txt"
BLACKMATRIX7_BASE = "https://cdn.statically.io/gh/blackmatrix7/ios_rule_script/master/rule"
```

## Making jsDelivr Default

If you're **always** running from China, edit `scripts/generate.py`:

```python
# Line ~30, change:
USE_JSDELIVR = False  # Change to True

# To:
USE_JSDELIVR = True   # Now jsDelivr is default
```

Then you can run without the flag:
```bash
./run.sh  # Uses jsDelivr automatically
```

## Verification

To verify which URLs are being used, check the console output:

```bash
./run.sh --use-jsdelivr
```

You should see:
```
Using jsDelivr CDN (China-accessible)
============================================================
Proxy Rules Generator
============================================================

[1/3] Fetching GFW blocked domains...
  Downloading: https://cdn.jsdelivr.net/gh/gfwlist/gfwlist@master/gfwlist.txt
```

## Troubleshooting

**Still slow?**
- jsDelivr may have rate limits; wait a few minutes
- Try clearing cache: `rm -rf cache/*`
- Consider downloading files manually and placing in `cache/` folder

**Errors about 404 or invalid files?**
- The repository structure may have changed
- Check if the app name is correct in `CHINA_MEDIA_APPS`
- Visit https://cdn.jsdelivr.net/gh/blackmatrix7/ios_rule_script@master/rule/Shadowrocket/ to browse available apps
