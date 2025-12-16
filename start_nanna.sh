#!/bin/bash
# Nanna - Start All Services
# Usage: ./start_nanna.sh

echo "=========================================="
echo "  Starting Nanna Voice Services"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Start Coqui TTS Server (background)
echo -e "${YELLOW}Starting Coqui TTS Server...${NC}"
cd /Users/sumanaddanke/git/nanna/tools
/opt/homebrew/bin/python3.11 nanna_tts_server.py &
TTS_PID=$!
echo -e "${GREEN}TTS Server started (PID: $TTS_PID)${NC}"

# Wait for server to be ready
echo "Waiting for TTS model to load..."
sleep 5
while ! curl -s http://localhost:5002/health > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
echo -e "\n${GREEN}TTS Server ready!${NC}"

# 2. Start webapp server
echo -e "\n${YELLOW}Starting Webapp Server...${NC}"
cd /Users/sumanaddanke/git/nanna/webapp
python3 -m http.server 8080 &
WEB_PID=$!
echo -e "${GREEN}Webapp started at http://localhost:8080${NC}"

# Show status
echo ""
echo "=========================================="
echo -e "${GREEN}All services running!${NC}"
echo "=========================================="
echo ""
echo "Services:"
echo "  - TTS Server:  http://localhost:5002 (PID: $TTS_PID)"
echo "  - Webapp:      http://localhost:8080 (PID: $WEB_PID)"
echo ""
echo "Open in browser: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Open browser
open http://localhost:8080

# Wait and cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Stopping services...${NC}"
    kill $TTS_PID 2>/dev/null
    kill $WEB_PID 2>/dev/null
    echo -e "${GREEN}All services stopped.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Keep running
wait
