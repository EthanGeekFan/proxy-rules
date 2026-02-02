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
# Install dependencies
pip install -r requirements.txt

# Generate all configs
python scripts/generate.py

# Or generate specific configs
python scripts/generate.py --shadowrocket-gfw
python scripts/generate.py --shadowrocket-china
python scripts/generate.py --glinet
```

## Output Files

- `output/shadowrocket-gfw.conf` - Import into Shadowrocket
- `output/shadowrocket-china.conf` - Import into Shadowrocket
- `output/glinet-gfw.txt` - Upload to GL.iNet router VPN Policy

## Data Sources

- GFW blocked domains: [gfwlist](https://github.com/gfwlist/gfwlist)
- Chinese media apps: [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)
