#!/usr/bin/env python3
"""
Analyze mitmproxy flow dump for location detection patterns.

Usage:
    # After capturing with mitmproxy, export flows:
    mitmdump -r ~/.mitmproxy/flows -w ximalaya.flow

    # Then analyze:
    python scripts/analyze-traffic.py ximalaya.flow
"""

import sys
import json
from pathlib import Path

try:
    from mitmproxy import io
    from mitmproxy.exceptions import FlowReadException
except ImportError:
    print("❌ mitmproxy not installed. Install with: pip install mitmproxy")
    sys.exit(1)

# Keywords to search for location detection
LOCATION_KEYWORDS = [
    'country', 'region', 'city', 'location', 'geo', 'ip',
    'latitude', 'longitude', 'cn', 'china', 'us', 'usa',
    'allowed', 'available', 'blocked', 'restricted'
]

GEO_SERVICES = [
    'ip-api.com', 'ipapi.co', 'geoip', 'ipinfo.io',
    'api.country.is', 'freegeoip', 'ip2location'
]


def analyze_flow_file(flow_file: str):
    """Analyze mitmproxy flow dump for location detection."""

    if not Path(flow_file).exists():
        print(f"❌ File not found: {flow_file}")
        return

    print(f"📊 Analyzing: {flow_file}")
    print("=" * 70)

    ximalaya_requests = []
    geo_api_requests = []
    location_responses = []

    try:
        with open(flow_file, "rb") as f:
            flow_reader = io.FlowReader(f)

            for flow in flow_reader.stream():
                if not hasattr(flow, 'request'):
                    continue

                request = flow.request
                response = flow.response if hasattr(flow, 'response') else None

                # Check if it's Ximalaya domain
                is_ximalaya = 'ximalaya' in request.host or 'xmcdn' in request.host

                # Check if it's a geo API
                is_geo_api = any(geo in request.host for geo in GEO_SERVICES)

                if is_ximalaya:
                    ximalaya_requests.append({
                        'url': request.url,
                        'method': request.method,
                        'host': request.host,
                        'path': request.path,
                        'response': response
                    })

                if is_geo_api:
                    geo_api_requests.append({
                        'url': request.url,
                        'host': request.host,
                        'response': response
                    })

                # Check response for location data
                if response:
                    # Check headers
                    for header, value in response.headers.items():
                        header_lower = header.lower()
                        if any(kw in header_lower for kw in ['country', 'region', 'geo', 'location']):
                            location_responses.append({
                                'url': request.url,
                                'type': 'header',
                                'key': header,
                                'value': value
                            })

                    # Check response body
                    try:
                        if response.content:
                            content = response.content.decode('utf-8', errors='ignore')
                            content_lower = content.lower()

                            if any(kw in content_lower for kw in LOCATION_KEYWORDS):
                                # Try to parse as JSON
                                try:
                                    json_data = json.loads(content)
                                    location_responses.append({
                                        'url': request.url,
                                        'type': 'json',
                                        'data': json_data,
                                        'is_ximalaya': is_ximalaya
                                    })
                                except:
                                    # Not JSON, but contains location keywords
                                    if len(content) < 1000:  # Only show small responses
                                        location_responses.append({
                                            'url': request.url,
                                            'type': 'text',
                                            'snippet': content[:500],
                                            'is_ximalaya': is_ximalaya
                                        })
                    except:
                        pass

    except FlowReadException as e:
        print(f"❌ Error reading flow file: {e}")
        return

    # Print results
    print(f"\n📱 Ximalaya Requests: {len(ximalaya_requests)}")
    print("-" * 70)
    if ximalaya_requests:
        for req in ximalaya_requests[:20]:  # Show first 20
            status = req['response'].status_code if req['response'] else '---'
            print(f"  [{req['method']}] {status} - {req['url']}")
        if len(ximalaya_requests) > 20:
            print(f"  ... and {len(ximalaya_requests) - 20} more")
    else:
        print("  ℹ️  No Ximalaya requests found")

    print(f"\n🌍 Geo API Requests: {len(geo_api_requests)}")
    print("-" * 70)
    if geo_api_requests:
        for req in geo_api_requests:
            print(f"  🚨 FOUND: {req['url']}")
            if req['response']:
                try:
                    content = req['response'].content.decode('utf-8', errors='ignore')
                    print(f"     Response: {content[:200]}")
                except:
                    pass
    else:
        print("  ✅ No external geo API calls detected")

    print(f"\n🔍 Location Data in Responses: {len(location_responses)}")
    print("-" * 70)
    if location_responses:
        for loc in location_responses[:15]:  # Show first 15
            if loc['type'] == 'header':
                print(f"  📋 Header: {loc['key']}: {loc['value']}")
                print(f"     URL: {loc['url']}")
            elif loc['type'] == 'json':
                marker = "🚨 XIMALAYA" if loc['is_ximalaya'] else "ℹ️ "
                print(f"  {marker} JSON Response: {loc['url']}")
                print(f"     Data: {json.dumps(loc['data'], indent=6, ensure_ascii=False)[:300]}")
            elif loc['type'] == 'text':
                marker = "🚨 XIMALAYA" if loc['is_ximalaya'] else "ℹ️ "
                print(f"  {marker} Text Response: {loc['url']}")
                print(f"     Snippet: {loc['snippet'][:200]}")
            print()
    else:
        print("  ℹ️  No obvious location data found")

    # Summary
    print("\n" + "=" * 70)
    print("📝 Summary:")
    print(f"  • Total Ximalaya requests: {len(ximalaya_requests)}")
    print(f"  • Geo API calls: {len(geo_api_requests)}")
    print(f"  • Responses with location data: {len(location_responses)}")

    if geo_api_requests:
        print("\n🚨 ALERT: App is calling external geo IP services!")
        print("   These should be routed through your China proxy")

    if location_responses:
        ximalaya_loc = [r for r in location_responses if r.get('is_ximalaya')]
        if ximalaya_loc:
            print("\n🚨 ALERT: Ximalaya API is returning location data!")
            print("   Check if these API endpoints need to be proxied")

    print("\n💡 Next steps:")
    print("  1. Review domains listed above")
    print("  2. Add missing domains to data/custom-china.txt")
    print("  3. Regenerate config: ./run.sh --shadowrocket-china")
    print("  4. Re-test Ximalaya app")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/analyze-traffic.py <flow-file>")
        print("\nExample:")
        print("  mitmdump -r ~/.mitmproxy/flows -w ximalaya.flow")
        print("  python scripts/analyze-traffic.py ximalaya.flow")
        sys.exit(1)

    analyze_flow_file(sys.argv[1])
