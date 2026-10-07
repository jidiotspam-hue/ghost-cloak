#!/usr/bin/env bash
# Disables macOS system HTTP & HTTPS proxy
INTERFACE="${1:-Wi-Fi}"

echo "Disabling macOS HTTP & HTTPS proxy for interface '$INTERFACE'..."
networksetup -setwebproxystate "$INTERFACE" off
networksetup -setsecurewebproxystate "$INTERFACE" off

echo "Current status for $INTERFACE:"
networksetup -getwebproxy "$INTERFACE"
networksetup -getsecurewebproxy "$INTERFACE"
echo ""
echo "Proxy successfully disabled."
