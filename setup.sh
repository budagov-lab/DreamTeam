#!/bin/bash
# DreamTeam — one-command setup after clone
# Run from DreamTeam folder: ./setup.sh

set -e
echo "DreamTeam setup..."
pip install -e .
echo ""
echo "Verifying..."
python -m dreamteam
echo ""
if [ ! -d .dreamteam ]; then
    echo "Creating project..."
    python -m dreamteam new-project .
fi
echo ""
echo "Ready. Open in Cursor, run /start + your goal, then dreamteam run-next"
