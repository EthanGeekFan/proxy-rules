#!/bin/bash
# Disable system proxy after analysis

# Get the network service name
SERVICE=$(networksetup -listallnetworkservices | grep -v asterisk | grep -E "Wi-Fi|Ethernet" | head -n 1)

if [ -z "$SERVICE" ]; then
    echo "❌ Could not find Wi-Fi or Ethernet service"
    exit 1
fi

echo "📡 Disabling proxy on: $SERVICE"

# Disable HTTP proxy
networksetup -setwebproxystate "$SERVICE" off

# Disable HTTPS proxy
networksetup -setsecurewebproxystate "$SERVICE" off

echo "✅ Proxy disabled"
echo "Your network is back to normal"
