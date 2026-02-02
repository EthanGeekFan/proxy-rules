# Analyze Ximalaya Location Detection

This guide helps you intercept and analyze Ximalaya Mac app's network traffic to find out how it determines your location.

## Tools We'll Use

### Option 1: mitmproxy (Recommended - Free)
- Intercepts HTTP/HTTPS traffic
- Web interface for easy browsing
- Command-line for filtering
- Can export requests

### Option 2: Proxyman (GUI - Free trial)
- Beautiful Mac-native UI
- Easy to use
- Good for beginners

### Option 3: Charles Proxy (GUI - Paid)
- Industry standard
- Easy filtering

## Setup: mitmproxy

### 1. Install mitmproxy

```bash
# Using Homebrew
brew install mitmproxy

# Verify installation
mitmproxy --version
```

### 2. Start mitmweb (Web Interface)

```bash
# Start the proxy on port 8080 with web interface
mitmweb --web-port 8081
```

This opens:
- **Proxy**: `http://localhost:8080` (for routing traffic)
- **Web UI**: `http://localhost:8081` (for viewing requests)

### 3. Configure Mac System Proxy

**Option A: Manual (Temporary)**
1. System Settings → Network → Wi-Fi → Details
2. Proxies tab → Check "Web Proxy (HTTP)" and "Secure Web Proxy (HTTPS)"
3. Set both to:
   - Server: `127.0.0.1`
   - Port: `8080`
4. Click OK

**Option B: Using Script (Easier)**

Run this to enable proxy:
```bash
./scripts/enable-proxy.sh
```

Run this to disable after:
```bash
./scripts/disable-proxy.sh
```

### 4. Install mitmproxy CA Certificate

For HTTPS decryption:

1. With mitmproxy running, visit: http://mitm.it in Safari
2. Click "Apple" icon → Download certificate
3. Double-click the downloaded certificate
4. Add to "System" keychain
5. Open Keychain Access → System → Find "mitmproxy"
6. Double-click → Trust → "Always Trust"

### 5. Run Ximalaya App

1. Open Ximalaya Mac app
2. Try to play content or browse
3. Watch requests appear in mitmweb UI (http://localhost:8081)

### 6. Analyze Traffic

Look for these location detection methods:

#### A. IP Geolocation API Calls
Search for domains like:
- `ip-api.com`
- `ipapi.co`
- `geoip.*`
- `ipinfo.io`
- `api.country.is`
- Any API returning `country`, `region`, `city`

#### B. Location Headers in Responses
Look for headers:
- `X-Country-Code`
- `X-Region`
- `CF-IPCountry` (Cloudflare)
- `X-Geo-*`

#### C. Location Data in Response Bodies
Search responses for:
- `"country": "US"`
- `"region": "California"`
- `"geo":`
- `"location":`

#### D. DNS-based Detection
Check if responses differ based on DNS resolver location.

## Analysis Workflow

### 1. Filter Ximalaya Domains

In mitmweb, use filter:
```
~d ximalaya.com | ~d xmcdn.com
```

### 2. Export Captured Traffic

```bash
# Export to file for analysis
mitmdump -r ~/.mitmproxy/flows -w ximalaya-capture.flow
```

### 3. Search for Keywords

In mitmweb search box, try:
- `country`
- `region`
- `location`
- `geo`
- `ip`
- `china`
- `403` (forbidden status)
- `451` (unavailable for legal reasons)

## Common Location Detection Methods

### 1. IP Geolocation
```json
GET https://api.service.com/geoip
Response: {"country": "US", "allowed": false}
```

**Fix**: Ensure ALL traffic goes through China proxy

### 2. DNS Geolocation
Different responses based on DNS server location.

**Fix**: Use Chinese DNS servers (223.5.5.5)

### 3. CDN Edge Location
CDN returns different content based on edge server.

**Fix**: Route CDN domains through proxy

### 4. API Region Check
```json
GET https://api.ximalaya.com/user/region
Response: {"region": "US", "access": "denied"}
```

**Fix**: Add API domain to proxy rules

## Quick Analysis Commands

### Using grep on captured traffic

```bash
# Search for location-related keywords in all requests
mitmdump -r ~/.mitmproxy/flows | grep -i "country\|region\|location\|geo"

# Filter only ximalaya domains
mitmdump -r ~/.mitmproxy/flows | grep -i "ximalaya\|xmcdn"

# Find 403/451 responses
mitmdump -r ~/.mitmproxy/flows | grep "403\|451"
```

## Alternative: tcpdump + Wireshark

For lower-level packet analysis:

```bash
# Capture traffic to/from ximalaya
sudo tcpdump -i any -w ximalaya.pcap host ximalaya.com or host xmcdn.com

# Open in Wireshark
wireshark ximalaya.pcap
```

In Wireshark:
1. Filter: `http.host contains "ximalaya" or dns.qry.name contains "ximalaya"`
2. Follow HTTP Stream
3. Look for location data in responses

## Alternative: Proxyman (GUI)

If you prefer a GUI:

1. Download from: https://proxyman.io
2. Install & trust certificate (Proxyman helps with this)
3. Enable macOS proxy
4. Use Ximalaya app
5. Search requests for location-related keywords

**Advantages**:
- Beautiful UI
- Easy filtering
- Automatic HTTPS decryption
- Request/response preview

## What to Look For

After capturing traffic, create a report:

1. **Domains contacted**: List all domains
2. **Location APIs**: Any geolocation service calls?
3. **Response data**: Any country/region in responses?
4. **Failed requests**: Any 403/451 errors?
5. **Headers**: Any geo-related headers?

## Adding Findings to Proxy Rules

Once you find the domains checking location:

```bash
# Add to custom-china.txt
echo "api.location-check.ximalaya.com" >> data/custom-china.txt

# Regenerate config
./run.sh --shadowrocket-china
```

## Cleanup

After analysis:

```bash
# Disable system proxy
./scripts/disable-proxy.sh

# Or manually:
# System Settings → Network → Wi-Fi → Proxies → Uncheck all
```

## Troubleshooting

**Certificate not trusted?**
- Keychain Access → System → mitmproxy → Get Info → Trust → Always Trust

**No traffic appearing?**
- Check system proxy is set to 127.0.0.1:8080
- Make sure mitmweb is running
- Try visiting http://example.com in Safari (should appear in mitmweb)

**HTTPS shows as "unknown"?**
- Certificate not installed/trusted
- Some apps use certificate pinning (can't be intercepted)

**Certificate Pinning?**
If Ximalaya uses certificate pinning, mitmproxy won't work. Signs:
- SSL errors in app
- No HTTPS requests visible
- App refuses to connect

In this case, use:
- Wireshark/tcpdump (can see domains but not decrypt)
- System-level analysis (DNS queries, IP connections)
