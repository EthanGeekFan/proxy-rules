#!/bin/bash
# Enable system proxy for mitmproxy capture

# Get the network service name (usually "Wi-Fi" or "Ethernet")
SERVICE=$(networksetup -listallnetworkservices | grep -v asterisk | grep -E "Wi-Fi|Ethernet" | head -n 1)

if [ -z "$SERVICE" ]; then
    echo "❌ Could not find Wi-Fi or Ethernet service"
    exit 1
fi

echo "📡 Enabling proxy on: $SERVICE"

# Enable HTTP proxy
networksetup -setwebproxy "$SERVICE" 127.0.0.1 8080

# Enable HTTPS proxy
networksetup -setsecurewebproxy "$SERVICE" 127.0.0.1 8080

echo "✅ Proxy enabled: 127.0.0.1:8080"
echo ""
echo "Next steps:"
echo "1. Make sure mitmproxy is running: mitmweb --web-port 8081"
echo "2. Install certificate: http://mitm.it"
echo "3. Open Ximalaya app"
echo "4. View requests: http://localhost:8081"
echo ""
echo "When done, run: ./scripts/disable-proxy.sh"
