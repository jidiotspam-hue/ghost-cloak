#!/usr/bin/env bash
# Launches ScreenCloak: Dual-layer graphics-level cloaked browser
# Excludes real browsing from digital screen capture (Zoom, Teams, Discord, GoGuardian, Screen Sharing)
# Displays an authentic Decoy tab (Google Docs, Canvas, etc.) to digital observers
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -f "$DIR/ScreenCloak" ]; then
    echo "Compiling ScreenCloak binary..."
    swiftc -O "$DIR/ScreenCloak.swift" -framework Cocoa -framework WebKit -o "$DIR/ScreenCloak"
fi

echo "=========================================================="
echo "  ScreenCloak: Hardware Graphics Level Window Cloak"
echo "=========================================================="
echo "  • Physical Monitor: Displays Ghost Browser (Proxy / YouTube)"
echo "  • Digital Observer: Captures Decoy Layer (Google Docs / Canvas)"
echo "  • Boss / Panic Key: Press ESC to instantly hide Ghost layer"
echo "=========================================================="

"$DIR/ScreenCloak" "$@" &
echo "ScreenCloak running in background! [PID: $!]"
