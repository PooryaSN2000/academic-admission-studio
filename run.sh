#!/bin/bash
# ==============================================================
# Academic Admission Studio - Launch Script for Linux & macOS
# ==============================================================

cd "$(dirname "$0")"

PORT=5050
URL="http://127.0.0.1:$PORT"

echo ""
echo "=============================================================="
echo "  🏛️ Academic Admission Studio - Laboratory Capacity & Roster"
echo "=============================================================="
echo ""

if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 was not found on your system."
    echo "💡 Note: You can open 'offline_dashboard.html' directly in any web browser without Python."
    exit 1
fi

python3 -c "import flask, openpyxl" &> /dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing required packages..."
    if [ -f requirements.txt ]; then
        python3 -m pip install -r requirements.txt --quiet
    else
        python3 -m pip install flask openpyxl --quiet
    fi
fi

# Free port 5050 if in use
PID=$(lsof -ti :$PORT 2>/dev/null)
if [ ! -z "$PID" ]; then
    echo "⚠️ Port $PORT was previously in use. Releasing port..."
    kill -9 $PID 2>/dev/null || true
    sleep 1
fi

echo "🚀 Starting server at: $URL"
echo "📌 Press Ctrl + C to stop the server."
echo "=============================================================="
echo ""

if command -v xdg-open &> /dev/null; then
    (sleep 1.2 && xdg-open "$URL" &> /dev/null) &
elif command -v open &> /dev/null; then
    (sleep 1.2 && open "$URL" &> /dev/null) &
fi

python3 core/app.py
