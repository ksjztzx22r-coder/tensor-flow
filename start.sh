#!/bin/bash
# ==============================================================================
# Wildlife Intrusion Detection System - Live Console Launcher
# Safely stops background service to prevent 'GPIO busy' and runs interactive output
# ==============================================================================

cd "$(dirname "$0")"

echo "=============================================================="
echo " Starting Wildlife Intrusion Detection (Live Console Mode)"
echo "=============================================================="

# Check and stop background service if running to release GPIO 17
if systemctl is-active --quiet wildlife.service; then
    echo "[INFO] Stopping background service to free GPIO pins..."
    sudo systemctl stop wildlife.service
fi

# Ensure no orphaned python instances are holding GPIO 17
sudo pkill -9 -f "src.Rasp_Pi.main" 2>/dev/null || true
sleep 0.5

# Run main script with unbuffered live terminal output
exec /usr/bin/python3 -u -m src.Rasp_Pi.main
