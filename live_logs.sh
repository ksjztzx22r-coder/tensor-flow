#!/bin/bash
# ==============================================================================
# Wildlife Intrusion Detection System - Live Background Stream
# Streams exact output, status, and procedure text from the background service
# ==============================================================================

echo "Connecting to live service stream (Ctrl+C to exit)..."
sudo journalctl -u wildlife.service -f -n 50 -o cat
