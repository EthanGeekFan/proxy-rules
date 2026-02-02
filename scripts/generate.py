#!/usr/bin/env python3
"""
Generate proxy routing rules for Shadowrocket and GL.iNet router.
"""

import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path
from typing import Set, List
import requests

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
CACHE_DIR = PROJECT_ROOT / "cache"
OUTPUT_DIR = PROJECT_ROOT / "output"
DATA_DIR = PROJECT_ROOT / "data"

# Ensure directories exist
CACHE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Data sources
GFWLIST_URL = "https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt"
BLACKMATRIX7_BASE = "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule"

# Chinese media apps to include
# Note: Add/remove apps as needed. Check available apps at:
# https://github.com/blackmatrix7/ios_rule_script/tree/master/rule/Shadowrocket
CHINA_MEDIA_APPS = [
    "NetEaseMusic",   # 网易云音乐
    "KugouKuwo",      # 酷狗酷我 (Tencent Music - similar to QQ Music)
    "iQIYI",          # 爱奇艺
    "TencentVideo",   # 腾讯视频
    "BiliBili",       # B站
    "Youku",          # 优酷
    # Note: Ximalaya (喜马拉雅) not available in blackmatrix7, add custom domains to custom-china.txt
]


def fetch_url(url: str, cache_file: str = None) -> str:
    """Fetch URL content with optional caching."""
    if cache_file:
        cache_path = CACHE_DIR / cache_file
        if cache_path.exists():
            print(f"  Using cached: {cache_file}")
            return cache_path.read_text(encoding='utf-8')

    print(f"  Downloading: {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    content = response.text

    if cache_file:
        cache_path = CACHE_DIR / cache_file
        cache_path.write_text(content, encoding='utf-8')

    return content


def load_custom_domains(filename: str) -> Set[str]:
    """Load custom domains from data file."""
    filepath = DATA_DIR / filename
    domains = set()

    if not filepath.exists():
        return domains

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            domains.add(line)

    return domains


def parse_gfwlist() -> Set[str]:
    """Parse GFW list and return set of domains."""
    print("\n[1/3] Fetching GFW blocked domains...")

    content = fetch_url(GFWLIST_URL, "gfwlist.txt")

    # Decode base64
    try:
        decoded = base64.b64decode(content).decode('utf-8')
    except:
        decoded = content

    domains = set()
    for line in decoded.split('\n'):
        line = line.strip()

        # Skip comments and empty lines
        if not line or line.startswith('!') or line.startswith('['):
            continue

        # Remove URL schemes and patterns
        line = re.sub(r'^@@', '', line)  # Remove whitelist marker
        line = re.sub(r'^\|\|', '', line)  # Remove domain anchor
        line = re.sub(r'^\|', '', line)    # Remove start anchor
        line = re.sub(r'\|$', '', line)    # Remove end anchor
        line = re.sub(r'^https?://', '', line)  # Remove scheme
        line = re.sub(r'/.*$', '', line)   # Remove path
        line = re.sub(r'\*', '', line)     # Remove wildcards

        # Extract domain
        if '.' in line and not line.startswith('.'):
            # Clean domain
            domain = line.split(':')[0]  # Remove port
            domain = domain.strip('.')

            if domain and len(domain) > 3:  # Basic validation
                domains.add(domain)

    # Add custom domains
    custom = load_custom_domains("custom-gfw.txt")
    if custom:
        print(f"  Added {len(custom)} custom domains")
        domains.update(custom)

    print(f"  Total: {len(domains)} blocked domains")
    return domains


def fetch_china_media_rules() -> Set[str]:
    """Fetch Chinese media app rules from blackmatrix7."""
    print("\n[2/3] Fetching Chinese media app rules...")

    all_domains = set()

    for app in CHINA_MEDIA_APPS:
        try:
            # Try Shadowrocket format first (domain-set)
            url = f"{BLACKMATRIX7_BASE}/Shadowrocket/{app}/{app}.list"
            print(f"  Fetching {app}...")
            content = fetch_url(url, f"china-media-{app}.list")

            # Parse Shadowrocket list format
            for line in content.split('\n'):
                line = line.strip()
                if not line or line.startswith('#') or line.startswith('//'):
                    continue

                # Extract domain from rules like:
                # DOMAIN-SUFFIX,music.163.com
                # DOMAIN,interface.music.163.com
                # DOMAIN-KEYWORD,netease
                parts = line.split(',')
                if len(parts) >= 2:
                    rule_type = parts[0].strip()
                    domain = parts[1].strip()

                    if rule_type in ['DOMAIN-SUFFIX', 'DOMAIN']:
                        all_domains.add(domain)
        except Exception as e:
            print(f"    Warning: Failed to fetch {app}: {e}")
            continue

    # Add custom domains
    custom = load_custom_domains("custom-china.txt")
    if custom:
        print(f"  Added {len(custom)} custom domains")
        all_domains.update(custom)

    print(f"  Total: {len(all_domains)} media app domains")
    return all_domains


def generate_shadowrocket_gfw(domains: Set[str]):
    """Generate Shadowrocket config for GFW-blocked domains (route to US)."""
    print("\n[3/3] Generating Shadowrocket GFW config...")

    output_file = OUTPUT_DIR / "shadowrocket-gfw.conf"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Shadowrocket Configuration\n")
        f.write("# Route GFW-blocked traffic to US home\n")
        f.write("# Usage: Import this file in Shadowrocket when in China\n\n")
        f.write("[General]\n")
        f.write("bypass-system = true\n")
        f.write("skip-proxy = 192.168.0.0/16, 10.0.0.0/8, 172.16.0.0/12, localhost, *.local\n")
        f.write("bypass-tun = 10.0.0.0/8, 100.64.0.0/10, 127.0.0.0/8, 169.254.0.0/16, 172.16.0.0/12, 192.0.0.0/24, 192.0.2.0/24, 192.88.99.0/24, 192.168.0.0/16, 198.18.0.0/15, 198.51.100.0/24, 203.0.113.0/24, 224.0.0.0/4, 255.255.255.255/32\n")
        f.write("dns-server = system, 8.8.8.8, 8.8.4.4\n\n")

        f.write("[Rule]\n")
        f.write("# GFW-blocked domains - route to US proxy\n")

        for domain in sorted(domains):
            f.write(f"DOMAIN-SUFFIX,{domain},PROXY\n")

        f.write("\n# Default: Direct connection\n")
        f.write("FINAL,DIRECT\n")

    print(f"  Created: {output_file}")
    print(f"  Rules: {len(domains)} domains")


def generate_shadowrocket_china(domains: Set[str]):
    """Generate Shadowrocket config for Chinese media apps (route to China)."""
    print("\nGenerating Shadowrocket China media config...")

    output_file = OUTPUT_DIR / "shadowrocket-china.conf"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Shadowrocket Configuration\n")
        f.write("# Route Chinese media apps to China home\n")
        f.write("# Usage: Import this file in Shadowrocket when in US\n")
        f.write("# Note: Configure proxy to point to your China WireGuard server\n\n")
        f.write("[General]\n")
        f.write("bypass-system = true\n")
        f.write("skip-proxy = 192.168.0.0/16, 10.0.0.0/8, 172.16.0.0/12, localhost, *.local\n")
        f.write("bypass-tun = 10.0.0.0/8, 100.64.0.0/10, 127.0.0.0/8, 169.254.0.0/16, 172.16.0.0/12, 192.0.0.0/24, 192.0.2.0/24, 192.88.99.0/24, 192.168.0.0/16, 198.18.0.0/15, 198.51.100.0/24, 203.0.113.0/24, 224.0.0.0/4, 255.255.255.255/32\n")
        f.write("dns-server = system\n\n")

        f.write("[Rule]\n")
        f.write("# Chinese media apps - route to China proxy\n")

        for domain in sorted(domains):
            f.write(f"DOMAIN-SUFFIX,{domain},PROXY\n")

        f.write("\n# Default: Direct connection (for data/content delivery)\n")
        f.write("FINAL,DIRECT\n")

    print(f"  Created: {output_file}")
    print(f"  Rules: {len(domains)} domains")


def generate_glinet_policy(domains: Set[str]):
    """Generate GL.iNet VPN policy file for GFW bypass."""
    print("\nGenerating GL.iNet VPN policy...")

    output_file = OUTPUT_DIR / "glinet-gfw.txt"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# GL.iNet VPN Policy\n")
        f.write("# Route GFW-blocked traffic to US home\n")
        f.write("# Upload this file to GL.iNet router: VPN > VPN Policy\n\n")

        for domain in sorted(domains):
            f.write(f"{domain}\n")

    print(f"  Created: {output_file}")
    print(f"  Rules: {len(domains)} domains")


def main():
    parser = argparse.ArgumentParser(description="Generate proxy routing rules")
    parser.add_argument('--shadowrocket-gfw', action='store_true', help='Generate Shadowrocket GFW config only')
    parser.add_argument('--shadowrocket-china', action='store_true', help='Generate Shadowrocket China config only')
    parser.add_argument('--glinet', action='store_true', help='Generate GL.iNet policy only')
    args = parser.parse_args()

    # If no specific target, generate all
    generate_all = not (args.shadowrocket_gfw or args.shadowrocket_china or args.glinet)

    print("=" * 60)
    print("Proxy Rules Generator")
    print("=" * 60)

    try:
        # Fetch GFW list
        if generate_all or args.shadowrocket_gfw or args.glinet:
            gfw_domains = parse_gfwlist()

            if generate_all or args.shadowrocket_gfw:
                generate_shadowrocket_gfw(gfw_domains)

            if generate_all or args.glinet:
                generate_glinet_policy(gfw_domains)

        # Fetch Chinese media rules
        if generate_all or args.shadowrocket_china:
            china_domains = fetch_china_media_rules()
            generate_shadowrocket_china(china_domains)

        print("\n" + "=" * 60)
        print("✓ Generation complete!")
        print("=" * 60)
        print(f"\nOutput files in: {OUTPUT_DIR}")
        print("\nNext steps:")
        print("1. Import shadowrocket-*.conf files into Shadowrocket app")
        print("2. Upload glinet-gfw.txt to GL.iNet router VPN Policy")

    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
