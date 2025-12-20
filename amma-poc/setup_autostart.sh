#!/bin/bash
# Setup Auto-Start for WhatsApp Recorder
# Run this ONCE to enable automatic recording on Mac startup
#
# Usage: ./setup_autostart.sh

echo "=============================================="
echo "  SETUP AUTO-START RECORDER"
echo "=============================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_FILE="$SCRIPT_DIR/com.nanna.whatsapp-recorder.plist"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"

# Create LaunchAgents directory if needed
mkdir -p "$LAUNCH_AGENTS"
mkdir -p "$SCRIPT_DIR/logs"

# Stop if already running
launchctl unload "$LAUNCH_AGENTS/com.nanna.whatsapp-recorder.plist" 2>/dev/null

# Copy plist to LaunchAgents
cp "$PLIST_FILE" "$LAUNCH_AGENTS/"

# Load the agent
launchctl load "$LAUNCH_AGENTS/com.nanna.whatsapp-recorder.plist"

if [ $? -eq 0 ]; then
    echo "✓ Auto-start ENABLED!"
    echo ""
    echo "The recorder will now:"
    echo "  • Start automatically when you log in"
    echo "  • Run in background (no terminal needed)"
    echo "  • Restart if it crashes"
    echo ""
    echo "Check status:"
    echo "  launchctl list | grep nanna"
    echo ""
    echo "View logs:"
    echo "  tail -f $SCRIPT_DIR/logs/recorder.log"
    echo ""
    echo "To DISABLE auto-start:"
    echo "  launchctl unload ~/Library/LaunchAgents/com.nanna.whatsapp-recorder.plist"
else
    echo "✗ Failed to enable auto-start"
    echo "Check the plist file for errors"
fi

echo ""
echo "=============================================="
