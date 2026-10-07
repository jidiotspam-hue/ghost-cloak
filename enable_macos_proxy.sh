#!/usr/bin/env bash
# Enables macOS system HTTP & HTTPS proxy pointing to 127.0.0.1:8080
INTERFACE="${1:-Wi-Fi}"
PORT="${2:-8080}"

echo "Enabling macOS HTTP & HTTPS proxy for interface '$INTERFACE' to 127.0.0.1:$PORT..."
networksetup -setwebproxy "$INTERFACE" 127.0.0.1 "$PORT"
networksetup -setsecurewebproxy "$INTERFACE" 127.0.0.1 "$PORT"

echo "Current status for $INTERFACE:"
networksetup -getwebproxy "$INTERFACE"
networksetup -getsecurewebproxy "$INTERFACE"
echo ""
echo "Proxy successfully enabled. To disable run: ./disable_macos_proxy.sh"
