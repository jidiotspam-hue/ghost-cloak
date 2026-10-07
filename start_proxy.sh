#!/usr/bin/env bash
# Start the All-in-One Proxy Server in background or foreground
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${1:-8080}"
PID_FILE="$DIR/proxy.pid"
LOG_FILE="$DIR/proxy.log"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Proxy server is already running with PID $PID on port $PORT"
        echo "Dashboard: http://127.0.0.1:$PORT/"
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

echo "Starting proxy server on port $PORT..."
python3 "$DIR/server.py" "$PORT" > "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"
sleep 1

if ps -p "$PID" > /dev/null 2>&1; then
    echo "=========================================================="
    echo "Proxy server successfully started! [PID: $PID]"
    echo "=========================================================="
    echo "• Web Browser UI: http://127.0.0.1:$PORT/"
    echo "• Forward Proxy:  127.0.0.1:$PORT"
    echo "• Log file:       $LOG_FILE"
    echo "=========================================================="
    echo "To stop: ./stop_proxy.sh"
else
    echo "Failed to start proxy. Check $LOG_FILE for details."
    cat "$LOG_FILE"
    exit 1
fi
