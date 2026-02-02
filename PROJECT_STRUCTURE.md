# Project Structure

```
proxy-rules/
├── run.sh                      # Main entry point - run this!
├── README.md                   # Project overview
├── USAGE.md                    # Detailed usage instructions
├── PROJECT_STRUCTURE.md        # This file
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
│
├── scripts/
│   └── generate.py            # Main generation script
│                              # - Fetches GFW list
│                              # - Fetches Chinese media rules
│                              # - Generates Shadowrocket configs
│                              # - Generates GL.iNet policy
│
├── data/                      # Source data (manually maintained)
│   ├── custom-china.txt       # Your custom Chinese app domains
│   │                          # Add Ximalaya, QQ Music, etc. here
│   └── custom-gfw.txt         # Your custom GFW-blocked domains
│
├── cache/                     # Downloaded community lists (auto)
│   ├── gfwlist.txt           # Cached GFW list
│   ├── china-media-*.list    # Cached app rules from blackmatrix7
│   └── ...
│
├── output/                    # Generated configs (auto)
│   ├── shadowrocket-gfw.conf       # For China: route blocked → US
│   ├── shadowrocket-china.conf     # For US: route media → China
│   └── glinet-gfw.txt              # For GL.iNet: route blocked → US
│
└── venv/                      # Python virtual environment (auto)
```

## File Descriptions

### User-Facing Files

| File | Purpose | When to Use |
|------|---------|-------------|
| `run.sh` | Generate all configs | Every time you want to update rules |
| `data/custom-china.txt` | Add custom Chinese app domains | When you need apps not in blackmatrix7 |
| `data/custom-gfw.txt` | Add custom blocked domains | When you need sites not in GFW list |
| `output/shadowrocket-gfw.conf` | Import to Shadowrocket (China) | When in China |
| `output/shadowrocket-china.conf` | Import to Shadowrocket (US) | When in US |
| `output/glinet-gfw.txt` | Upload to GL.iNet router | Setup router in China |

### Generated/Cache Files

These are automatically created - no need to edit manually:

- `cache/*` - Downloaded community lists (deleted to force refresh)
- `output/*` - Generated configs (overwritten each run)
- `venv/` - Python virtual environment (created on first run)

## Data Flow

```
┌─────────────────────┐
│   Data Sources      │
├─────────────────────┤
│ - GFW List (GitHub) │
│ - blackmatrix7      │
│ - custom-*.txt      │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │  generate.py │
    │              │
    │ 1. Fetch     │
    │ 2. Parse     │
    │ 3. Merge     │
    │ 4. Format    │
    └──────┬───────┘
           │
           ▼
    ┌─────────────────────┐
    │  Output Configs     │
    ├─────────────────────┤
    │ - shadowrocket-*.conf│
    │ - glinet-gfw.txt    │
    └─────────────────────┘
```

## Customization Points

### 1. Change Apps (scripts/generate.py)

Edit `CHINA_MEDIA_APPS` list:
```python
CHINA_MEDIA_APPS = [
    "NetEaseMusic",
    "KugouKuwo",
    # Add more from:
    # https://github.com/blackmatrix7/ios_rule_script/tree/master/rule/Shadowrocket
]
```

### 2. Add Custom Domains (data/*.txt)

Add domains to:
- `data/custom-china.txt` - Chinese apps
- `data/custom-gfw.txt` - Blocked sites

### 3. Change Data Sources (scripts/generate.py)

Modify URLs:
```python
GFWLIST_URL = "..."
BLACKMATRIX7_BASE = "..."
```

## Future Enhancements

Possible additions:
- [ ] Domain to IP resolution for GL.iNet (some models need IPs)
- [ ] Clash/Surge config generation
- [ ] Auto-update script with cron
- [ ] Web UI for managing custom domains
- [ ] China IP list (route by destination IP instead of domain)
