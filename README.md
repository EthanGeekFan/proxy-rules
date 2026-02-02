# Proxy Rules Manager

Manage routing rules for Shadowrocket and GL.iNet router.

## Setup

### Network Topology
- **US Home**: WireGuard server in California
- **China Home**: GL.iNet router with WireGuard client (connects to US) and WireGuard server
- **Mobile/Laptop**: Shadowrocket connects to both nodes

### Rules Generated

1. **`shadowrocket-gfw.conf`** - Routes GFW-blocked traffic to US home (for use in China)
2. **`shadowrocket-china.conf`** - Routes Chinese media apps to China home (for use in US)
3. **`glinet-gfw.txt`** - VPN policy for GL.iNet to route blocked traffic to US

## Usage

```bash
# Generate all configs
./run.sh

# Generate specific configs
./run.sh --shadowrocket-gfw
./run.sh --shadowrocket-china
./run.sh --glinet

# For users in China (use jsDelivr CDN)
./run.sh --use-jsdelivr
```

## Output Files

- `output/shadowrocket-gfw.conf` - Import into Shadowrocket
- `output/shadowrocket-china.conf` - Import into Shadowrocket
- `output/glinet-gfw.txt` - Upload to GL.iNet router VPN Policy

## Running from China

GitHub raw URLs may be blocked. Use jsDelivr CDN:

```bash
./run.sh --use-jsdelivr
```

See [CHINA_ACCESS.md](CHINA_ACCESS.md) for details.

## Debugging: Why Apps Still Detect Wrong Location?

If Chinese apps still think you're not in China:

**Quick fix**: Try adding missing domains to `data/custom-china.txt`

**Deep analysis**: Intercept and analyze app traffic to find how it detects location:

```bash
# See quick start guide
cat QUICK_START_ANALYSIS.md

# Or full guide
cat ANALYZE_XIMALAYA.md
```

Tools and scripts included:
- `scripts/enable-proxy.sh` - Enable system proxy for traffic capture
- `scripts/disable-proxy.sh` - Disable proxy after analysis
- `scripts/analyze-traffic.py` - Automated analysis of captured traffic

## Data Sources

- GFW blocked domains: [gfwlist](https://github.com/gfwlist/gfwlist)
- Chinese media apps: [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)
