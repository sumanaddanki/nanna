#!/bin/bash
# Auto-recorder launcher for WhatsApp calls
# Run this on Mac Air before making calls

cd "$(dirname "$0")"

echo "=============================================="
echo "  WHATSAPP CALL AUTO-RECORDER"
echo "=============================================="
echo ""
echo "Before starting, make sure:"
echo "  1. System Settings → Sound → Output = Multi-Output Device"
echo "  2. System Settings → Sound → Input = Aggregate Device"
echo ""
echo "Starting auto-recorder..."
echo ""

python3 auto_record_calls.py
