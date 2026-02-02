# Quick Start: Analyze Ximalaya Location Detection

Complete step-by-step guide to intercept and analyze Ximalaya traffic.

## Prerequisites

```bash
# Install mitmproxy
brew install mitmproxy

# Or if you prefer a GUI alternative:
# Download Proxyman: https://proxyman.io
# Download Charles: https://www.charlesproxy.com
```

## Step-by-Step Analysis

### Step 1: Start Intercepting Traffic

```bash
# Start mitmproxy with web interface
mitmweb --web-port 8081

# This will:
# - Start proxy on port 8080
# - Open web UI at http://localhost:8081
```

Keep this terminal running.

### Step 2: Enable System Proxy

**Option A: Use script (recommended)**
```bash
# In a new terminal, in this project folder:
./scripts/enable-proxy.sh
```

**Option B: Manual**
1. System Settings → Network → Wi-Fi → Details → Proxies
2. Check "Web Proxy (HTTP)" and "Secure Web Proxy (HTTPS)"
3. Server: `127.0.0.1`, Port: `8080`

### Step 3: Install Certificate (First Time Only)

```bash
# 1. Visit in Safari:
open http://mitm.it

# 2. Click the Apple icon → Download certificate
# 3. Double-click downloaded .pem file
# 4. Add to "System" keychain
# 5. Open Keychain Access:
open -a "Keychain Access"

# 6. Find "mitmproxy" in System keychain
# 7. Double-click → Trust → "Always Trust"
# 8. Close and enter your password
```

### Step 4: Test It's Working

```bash
# Visit any website in Safari:
open https://www.google.com

# You should see the request appear in:
open http://localhost:8081
```

If you see the google.com request, it's working!

### Step 5: Run Ximalaya App

1. Open Ximalaya Mac app
2. Try to play content or browse
3. Watch requests appear in http://localhost:8081

### Step 6: Look for Location Detection

In the mitmweb interface (http://localhost:8081):

**Filter for Ximalaya only:**
```
~d ximalaya | ~d xmcdn
```

**Search for location keywords:**
Use the search box to find:
- `country`
- `region`
- `geo`
- `location`
- `403` (forbidden error)
- `451` (unavailable)

**Check these:**
- ✅ Are there requests to geo IP services? (ip-api.com, ipinfo.io, etc.)
- ✅ Do API responses contain country/region data?
- ✅ Are there failed requests (403/451)?
- ✅ Check response headers for X-Country, CF-IPCountry, etc.

### Step 7: Export and Analyze

```bash
# In a new terminal:

# Export captured flows
mitmdump -r ~/.mitmproxy/flows -w ximalaya.flow

# Run automated analysis
python scripts/analyze-traffic.py ximalaya.flow
```

This will show you:
- All Ximalaya domains contacted
- Any geo IP API calls
- Responses containing location data
- Specific URLs to add to your proxy rules

### Step 8: Cleanup

```bash
# Disable system proxy
./scripts/disable-proxy.sh

# Or manual:
# System Settings → Network → Wi-Fi → Proxies → Uncheck all
```

## What You're Looking For

### 🚨 Red Flags (Need to Proxy)

1. **Geo IP API Calls**
```
GET https://ip-api.com/json
Response: {"country": "US", "countryCode": "US"}
```
→ Add domain to custom-china.txt

2. **API Region Check**
```
GET https://api.ximalaya.com/check/region
Response: {"region": "US", "available": false}
```
→ Add api.ximalaya.com to custom-china.txt

3. **CDN with Geo Headers**
```
GET https://cdn.xmcdn.com/audio/123.mp3
Response headers: CF-IPCountry: US
```
→ Already in rules, but check if routing through proxy

4. **Different Response Based on IP**
Same request from different IPs returns different data
→ All ximalaya.com/xmcdn.com must go through proxy

### ✅ What's OK

1. **User preferences** - Language, timezone settings
2. **Content metadata** - Audio info, playlists
3. **Analytics** - Usage stats (unless they block based on this)

## Common Findings

Based on other Chinese apps, Ximalaya likely uses:

1. **Server-side IP check** - Backend checks your IP against GeoIP database
2. **CDN edge location** - Cloudflare/CDN serves different content per region
3. **API region endpoint** - Explicit `/region` or `/geo` API call
4. **License check** - Content licensing restricted by region

## Troubleshooting

### No traffic appearing in mitmweb?

```bash
# Check proxy is enabled:
networksetup -getwebproxy Wi-Fi

# Should show: 127.0.0.1:8080

# Test with curl:
curl -x http://127.0.0.1:8080 http://example.com
```

### Certificate errors in Ximalaya?

The app might use **certificate pinning**. This prevents mitmproxy from intercepting HTTPS.

**Workaround:**
Use tcpdump to see domains without decrypting:

```bash
# Capture Ximalaya traffic
sudo tcpdump -i any -n 'host ximalaya.com or host xmcdn.com' -w ximalaya.pcap

# View in terminal
sudo tcpdump -r ximalaya.pcap -A | grep -i "host:\|HTTP"

# Or open in Wireshark:
wireshark ximalaya.pcap
```

### Still can't find the issue?

Try comparing:
1. Capture traffic while using Ximalaya **without** proxy (shows blocked)
2. Capture traffic while using Ximalaya **with** China proxy (should work)
3. Compare the two captures to see what's different

```bash
# Capture 1: No proxy
mitmweb --web-port 8081
# Use app, export as: ximalaya-blocked.flow

# Capture 2: With China proxy active in Shadowrocket
mitmweb --web-port 8081
# Use app, export as: ximalaya-working.flow

# Compare
diff <(mitmdump -r ximalaya-blocked.flow) <(mitmdump -r ximalaya-working.flow)
```

## Quick Commands Reference

```bash
# Start interception
mitmweb --web-port 8081

# Enable proxy
./scripts/enable-proxy.sh

# Install cert
open http://mitm.it

# View requests
open http://localhost:8081

# Export flows
mitmdump -r ~/.mitmproxy/flows -w ximalaya.flow

# Analyze
python scripts/analyze-traffic.py ximalaya.flow

# Disable proxy
./scripts/disable-proxy.sh
```

## Next Steps After Finding Domains

Once you identify the problematic domains:

```bash
# Add to custom domains
echo "api.location.ximalaya.com" >> data/custom-china.txt
echo "geo.ximalaya.com" >> data/custom-china.txt

# Regenerate config
./run.sh --shadowrocket-china

# Re-import to Shadowrocket and test
```

## Alternative: GUI Tools

If you prefer GUI:

### Proxyman (Recommended for Mac)
```bash
# Install
brew install --cask proxyman

# Or download from:
open https://proxyman.io
```

1. Open Proxyman
2. Install certificate (Proxyman guides you)
3. Enable proxy (automatic)
4. Use Ximalaya app
5. Search for location keywords in Proxyman

### Charles Proxy
```bash
# Install
brew install --cask charles

# Or download from:
open https://www.charlesproxy.com
```

Similar workflow to Proxyman.

## Need Help?

If you find the domains but Ximalaya still doesn't work:
1. Share the domains you found
2. Check if DNS is also going through proxy
3. Verify GPS/Location Services is disabled for the app
4. Try `FINAL,PROXY` instead of `FINAL,DIRECT` as a test
