# Ximalaya Analysis Results

## 🎯 Summary

Ximalaya blocks content based on **server-side IP geolocation**. When you request content, the server checks your IP address and returns error 927 if you're outside China.

## 📊 Traffic Analysis Findings

### The Blocking API Call

**Request:**
```
GET https://www.ximalaya.com/mobile-playpage/track/v3/baseInfo/1770010653359
```

**Response (Error 927):**
```json
{
  "ret": 927,
  "msg": "很抱歉，由于版权方要求，您所在的地区/国家暂时无法使用该资源",
  "extendInfo": {
    "msg": "应版权方要求，该资源仅限中国大陆及港澳台用户使用..."
  }
}
```

**Translation:**
- "Sorry, due to copyright requirements, this resource is unavailable in your region/country"
- "This resource is only available to users in mainland China, Hong Kong, Macau, and Taiwan"

## 🔍 How Location is Detected

**Method:** Server-side IP geolocation
- ✅ **Simple detection**: Server checks your request IP
- ✅ **No external geo APIs**: Ximalaya doesn't call third-party services
- ✅ **Domain-based**: All checks happen at `www.ximalaya.com`

**NOT used:**
- ❌ GPS/Location Services
- ❌ External geo-IP APIs (like ip-api.com)
- ❌ Client-side JavaScript location detection

## ✅ Solution

### 1. Ensure All Traffic Goes Through China Proxy

The domains are already in your config:
```
ximalaya.com  → Routes www.ximalaya.com, api.ximalaya.com, etc.
xmcdn.com     → Routes CDN content
```

### 2. Fix DNS Leaks (CRITICAL)

**Problem:** DNS queries can leak your real location even if HTTP traffic is proxied.

**Solution:** Updated config now uses Chinese DNS servers:
```
dns-server = 223.5.5.5, 223.6.6.6, 119.29.29.29
```

These are:
- `223.5.5.5` / `223.6.6.6` - Alibaba Public DNS (China)
- `119.29.29.29` - DNSPod (Tencent, China)

### 3. Re-import Updated Config

```bash
# Config already regenerated with Chinese DNS
# Import: output/shadowrocket-china.conf
```

In Shadowrocket:
1. Delete old `shadowrocket-china` config
2. Import new `output/shadowrocket-china.conf`
3. Set proxy to your **China WireGuard server**
4. Enable Shadowrocket
5. Test Ximalaya

## 🧪 Testing Checklist

### Verify Setup

**1. Check Proxy is Active:**
```
# In Shadowrocket, verify:
- Configuration: shadowrocket-china ✓
- Proxy: Your China WireGuard server
- Status: Connected
```

**2. Check DNS:**
```bash
# Test DNS resolution (should use Chinese DNS)
nslookup www.ximalaya.com 223.5.5.5
```

**3. Test Ximalaya:**
- Open Ximalaya Mac app
- Try to play restricted content
- Should work now!

### If Still Not Working

**Option 1: Temporarily Force All Traffic**

Edit `output/shadowrocket-china.conf`, change last line:
```
# From:
FINAL,DIRECT

# To:
FINAL,PROXY
```

This routes ALL traffic through China (helps debug if it's a domain issue).

**Option 2: Check Your IP**

While Shadowrocket is active:
```bash
# Check what IP websites see
curl https://api.ipify.org
# Should return your China home IP

# Or in browser:
open https://www.whatismyip.com
# Should show China location
```

**Option 3: Verify DNS Isn't Leaking**

```bash
# Check DNS leak
open https://dnsleaktest.com

# Should show Chinese DNS servers (223.5.5.5, etc.)
# NOT your ISP's US DNS
```

## 📝 Configuration Files

### Updated Config: shadowrocket-china.conf

```ini
[General]
# Use Chinese DNS servers to avoid DNS leaks
dns-server = 223.5.5.5, 223.6.6.6, 119.29.29.29

[Rule]
# Ximalaya domains
DOMAIN-SUFFIX,ximalaya.com,PROXY
DOMAIN-SUFFIX,xmcdn.com,PROXY

# Other Chinese media apps...
# (231 more domains)

# Default: Direct connection
FINAL,DIRECT
```

## 🎓 What We Learned

1. **Ximalaya uses simple IP-based geolocation**
   - Easier to bypass than GPS or complex methods
   - Just route traffic through China proxy

2. **DNS matters!**
   - DNS queries can leak location
   - Use Chinese DNS servers for Chinese apps

3. **DOMAIN-SUFFIX matching works**
   - `ximalaya.com` matches all subdomains
   - `www.ximalaya.com`, `api.ximalaya.com`, etc.

4. **No certificate pinning**
   - mitmproxy successfully intercepted HTTPS
   - Makes debugging much easier

## 🔧 Advanced: Monitor Future Changes

If Ximalaya changes their detection method, re-capture traffic:

```bash
# Start mitmproxy
mitmweb --web-port 8081

# Enable proxy
./scripts/enable-proxy.sh

# Use Ximalaya app

# Analyze
mitmdump -r ~/.mitmproxy/flows -w ximalaya.flow
python scripts/analyze-traffic.py ximalaya.flow

# Cleanup
./scripts/disable-proxy.sh
```

## ✅ Expected Result

After re-importing the config with Chinese DNS:
- ✅ Ximalaya should think you're in China
- ✅ All content should be playable
- ✅ No more error 927

## 🆘 Still Having Issues?

Check these common problems:

1. **Shadowrocket not active**
   - Verify green "connected" status

2. **Wrong proxy configured**
   - Make sure proxy points to **China** WireGuard, not US

3. **DNS still leaking**
   - Test at https://dnsleaktest.com
   - Should show Chinese DNS

4. **China proxy not working**
   - Test if your China WireGuard is accessible
   - Try: `ping <china-wireguard-ip>`

5. **Missing additional domains**
   - Some features might use other domains
   - Re-capture traffic to find them
   - Add to `data/custom-china.txt`
