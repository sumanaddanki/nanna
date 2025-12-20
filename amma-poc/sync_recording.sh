#!/bin/bash
# Sync recordings from Mac Air to Mac Studio for processing
# Then archive to US NAS
#
# Run on Mac Air after recording:
#   ./sync_recording.sh
#
# Or specify a file:
#   ./sync_recording.sh voice/raw/whatsapp_call_20241217_143000.wav

cd "$(dirname "$0")"

# Configuration
STUDIO_HOST="studio"  # Uses ~/.ssh/config
STUDIO_PATH="/Users/semostudio/git/sumanaddanki/nanna/amma-poc"
NAS_HOST="aauser@192.168.1.183"
NAS_PORT="17183"
NAS_ARCHIVE_PATH="/volume1/homes/aauser/amma-archive"

echo "=============================================="
echo "  SYNC RECORDINGS"
echo "=============================================="

# Find files to sync
if [ -n "$1" ]; then
    FILES=("$1")
else
    FILES=(voice/raw/*.wav)
fi

if [ ${#FILES[@]} -eq 0 ] || [ ! -f "${FILES[0]}" ]; then
    echo "No recordings found in voice/raw/"
    exit 1
fi

echo ""
echo "Files to sync:"
for f in "${FILES[@]}"; do
    if [ -f "$f" ]; then
        size=$(du -h "$f" | cut -f1)
        echo "  - $(basename "$f") ($size)"
    fi
done

echo ""
echo "Step 1: Push to Mac Studio for processing..."
echo "----------------------------------------------"

for f in "${FILES[@]}"; do
    if [ -f "$f" ]; then
        echo "  Copying $(basename "$f")..."
        scp "$f" "${STUDIO_HOST}:${STUDIO_PATH}/voice/raw/"
        if [ $? -eq 0 ]; then
            echo "  ✓ Copied to Mac Studio"
        else
            echo "  ✗ Failed to copy to Mac Studio"
            exit 1
        fi
    fi
done

echo ""
echo "Step 2: Process on Mac Studio..."
echo "----------------------------------------------"
echo "  SSH to Mac Studio and run:"
echo ""
echo "  cd ${STUDIO_PATH}"
echo "  python process_recording.py voice/raw/<filename>.wav"
echo "  python ../tools/separate_speakers.py voice/processed/<filename>_processed.wav"
echo ""

# Ask if user wants to archive now
read -p "Archive raw recordings to NAS now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Step 3: Archive to US NAS (4TB)..."
    echo "----------------------------------------------"

    # Create archive directory on NAS if needed
    ssh -p ${NAS_PORT} ${NAS_HOST} "mkdir -p ${NAS_ARCHIVE_PATH}/raw"

    for f in "${FILES[@]}"; do
        if [ -f "$f" ]; then
            echo "  Archiving $(basename "$f")..."
            scp -P ${NAS_PORT} "$f" "${NAS_HOST}:${NAS_ARCHIVE_PATH}/raw/"
            if [ $? -eq 0 ]; then
                echo "  ✓ Archived to NAS"

                # Move to local archive (don't delete, just move)
                mkdir -p voice/archived
                mv "$f" voice/archived/
                echo "  ✓ Moved to local archive"
            else
                echo "  ✗ Failed to archive to NAS (file kept locally)"
            fi
        fi
    done
fi

echo ""
echo "=============================================="
echo "  SYNC COMPLETE"
echo "=============================================="
echo ""
echo "Workflow:"
echo "  1. ✓ Raw recordings pushed to Mac Studio"
echo "  2. → Process on Mac Studio (speaker separation)"
echo "  3. ✓ Archive to US NAS (4TB)"
echo ""
echo "On Mac Studio, run:"
echo "  cd ${STUDIO_PATH}"
echo "  python process_recording.py voice/raw/<file>.wav"
