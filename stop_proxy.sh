#!/usr/bin/env bash
# Stop running All-in-One Proxy Server
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$DIR/proxy.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Stopping proxy server (PID: $PID)..."
        kill "$PID"
        sleep 1
        if ps -p "$PID" > /dev/null 2>&1; then
            kill -9 "$PID"
        fi
        echo "Proxy server stopped."
    else
        echo "PID file found, but process $PID is not running."
    fi
    rm -f "$PID_FILE"
else
    # Fallback search
    PIDS=$(pgrep -f "server.py 8080")
    if [ -n "$PIDS" ]; then
        echo "Killing proxy processes: $PIDS"
        kill $PIDS
    else
        echo "No running proxy server found."
    fi
fi
