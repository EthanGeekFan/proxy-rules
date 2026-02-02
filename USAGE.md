# Usage Guide

## Quick Start

```bash
# Generate all configs
./run.sh

# Generate specific config only
./run.sh --shadowrocket-gfw    # GFW bypass config
./run.sh --shadowrocket-china  # China media apps config
./run.sh --glinet              # GL.iNet VPN policy
```

## Output Files

### 1. `shadowrocket-gfw.conf` (For use in China)
- **Purpose**: Route GFW-blocked traffic to US home
- **Size**: ~4,700 domains
- **Usage**: Import into Shadowrocket app when you're in China
- **Examples**: google.com, youtube.com, twitter.com, facebook.com, etc.

### 2. `shadowrocket-china.conf` (For use in US)
- **Purpose**: Route Chinese media apps to China home for geo-unblocking
- **Size**: ~230 domains
- **Usage**: Import into Shadowrocket app when you're in the US
- **Apps covered**:
  - NetEase Cloud Music (网易云音乐)
  - Kugou/Kuwo Music (酷狗/酷我音乐) - similar to QQ Music
  - iQiyi (爱奇艺)
  - Tencent Video (腾讯视频)
  - BiliBili (哔哩哔哩)
  - Youku (优酷)

**Example domains**:
```
bilibili.com
bilibili.tv
music.163.com (NetEase Music)
iqiyi.com
v.qq.com (Tencent Video)
kugou.com
kuwo.cn
youku.com
```

### 3. `glinet-gfw.txt` (For GL.iNet router in China)
- **Purpose**: Route GFW-blocked traffic to US home
- **Size**: ~4,700 domains (same list as shadowrocket-gfw)
- **Usage**: Upload to GL.iNet router at VPN > VPN Policy
- **Format**: Plain text, one domain per line

## Adding Custom Domains

### For Chinese Apps (Ximalaya, QQ Music, etc.)

Edit `data/custom-china.txt`:
```
# Ximalaya (喜马拉雅)
ximalaya.com
xmcdn.com

# QQ Music specific domains (if KugouKuwo doesn't cover it)
y.qq.com
qq.music.qq.com
```

Then regenerate:
```bash
./run.sh --shadowrocket-china
```

### For Additional GFW-Blocked Sites

Edit `data/custom-gfw.txt`:
```
# Your custom blocked domains
myservice.com
api.myservice.com
```

Then regenerate:
```bash
./run.sh --shadowrocket-gfw
./run.sh --glinet
```

## Shadowrocket Configuration

### Setup for China (GFW Bypass)
1. In Shadowrocket, add your US WireGuard server as a proxy
2. Import `shadowrocket-gfw.conf`
3. Set the proxy to your US home WireGuard
4. Enable Shadowrocket
5. All GFW-blocked domains will route through US, others direct

### Setup for US (China Media Unblock)
1. In Shadowrocket, add your China WireGuard server as a proxy
2. Import `shadowrocket-china.conf`
3. Set the proxy to your China home WireGuard
4. Enable Shadowrocket
5. Only Chinese media apps route through China, others direct

## GL.iNet Router Setup

1. Login to GL.iNet router web interface
2. Go to VPN > VPN Clients
3. Add your US WireGuard server configuration
4. Go to VPN > VPN Policy
5. Upload `glinet-gfw.txt` as the policy file
6. Enable "Based on the domain name" policy
7. Clients connected to this router will have GFW-blocked traffic routed through US

## Updating Rules

The script caches downloaded lists in `cache/` directory. To force update:

```bash
# Delete cache and regenerate
rm -rf cache/*
./run.sh
```

## Troubleshooting

**Q: Some apps still show "content not available in your region"**
- Add the specific domains to `data/custom-china.txt`
- Use your browser's network inspector to find API domains
- Regenerate the config

**Q: Too many domains are being proxied**
- Check if the rule order is correct (specific rules before FINAL)
- Shadowrocket configs have FINAL,DIRECT at the end

**Q: GL.iNet policy not working**
- Make sure VPN client is connected
- Check that policy mode is "Based on the domain name"
- Some routers may need IP addresses instead of domains (future enhancement)
