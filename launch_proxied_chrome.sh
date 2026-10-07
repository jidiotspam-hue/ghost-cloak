#!/usr/bin/env bash
# Launches a separate, clean Google Chrome window routed entirely through the proxy (127.0.0.1:8080)
# YouTube, Netflix, Google, Discord, and all websites work 100% natively without URL rewriting bugs!
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${1:-8080}"
URL="${2:-https://www.youtube.com}"

echo "Launching Google Chrome routed through proxy 127.0.0.1:$PORT..."
open -na "Google Chrome" --args \
  --proxy-server="http://127.0.0.1:$PORT" \
  --user-data-dir="/tmp/chrome_proxy_profile" \
  "$URL"

echo "Chrome launched! Traffic to $URL is routed through 127.0.0.1:$PORT."

