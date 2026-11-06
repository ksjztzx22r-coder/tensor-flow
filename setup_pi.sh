#!/bin/bash
# ==============================================================================
# Wildlife Detection & Deterrence System - Automated Setup Script for Raspberry Pi
# Platform: Raspberry Pi 3B+ (Debian / Python 3.11)
# ==============================================================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================================================${NC}"
echo -e "${BLUE}  Wildlife Intrusion Detection System - Raspberry Pi Setup Script  ${NC}"
echo -e "${BLUE}==================================================================${NC}"

# Check that we are running inside the repository directory
if [ ! -f "requirements_pi.txt" ]; then
    echo -e "${RED}[ERROR] Please run this script from the project root directory (tensor-flow).${NC}"
    exit 1
fi

CURRENT_USER=$(whoami)
PROJECT_DIR=$(pwd)

echo -e "${GREEN}[1/6] Updating system packages & installing OS dependencies...${NC}"
sudo apt update -y
sudo apt install -y \
    python3-pip \
    python3-dev \
    libatlas-base-dev \
    libopenjp2-7 \
    libgl1-mesa-glx \
    pulseaudio \
    alsa-utils

# Handle libtiff across Debian versions (libtiff6 on Bookworm, libtiff5 on Bullseye)
sudo apt install -y libtiff6 || sudo apt install -y libtiff5 || sudo apt install -y libtiff-dev || true

# Install picamera2 if supported on this Debian release
echo -e "${GREEN}[2/6] Checking Picamera2 package availability...${NC}"
sudo apt install -y python3-picamera2 || echo -e "${YELLOW}[NOTE] python3-picamera2 package not found in this repo; falling back to OpenCV/V4L2.${NC}"

echo -e "${GREEN}[3/6] Installing Python runtime dependencies...${NC}"
# Use --break-system-packages for Debian Python 3.11 if needed
pip3 install -r requirements_pi.txt --break-system-packages || pip3 install -r requirements_pi.txt

echo -e "${GREEN}[4/6] Creating log and models directories...${NC}"
mkdir -p logs/detections
mkdir -p models
mkdir -p sounds

echo -e "${GREEN}[5/6] Creating systemd service for standalone auto-start...${NC}"
SERVICE_FILE="/etc/systemd/system/wildlife.service"

sudo bash -c "cat <<EOF > $SERVICE_FILE
[Unit]
Description=Wildlife Intrusion Detection & Acoustic Deterrence
After=network.target sound.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/python3 -m src.Rasp_Pi.main
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable wildlife.service
echo -e "${GREEN}[INFO] wildlife.service successfully enabled for auto-start on boot.${NC}"

echo -e "${GREEN}[6/6] Hardware smoke tests ready.${NC}"
echo -e "${BLUE}==================================================================${NC}"
echo -e "${GREEN}Setup completed successfully!${NC}"
echo -e "${BLUE}==================================================================${NC}"
echo ""
echo -e "${YELLOW}Next steps to test in PuTTY:${NC}"
echo -e "1. Test Audio Speaker:     ${GREEN}python3 -m src.Rasp_Pi.audio${NC}"
echo -e "2. Test Camera Capture:    ${GREEN}python3 -m src.Rasp_Pi.camera${NC}"
echo -e "3. Test PIR Motion Sensor: ${GREEN}python3 -m src.Rasp_Pi.pir_sensor${NC}"
echo -e "4. Test TFLite Detector:   ${GREEN}python3 -m src.Rasp_Pi.detector${NC}"
echo -e "5. Run Full System Live:   ${GREEN}python3 -m src.Rasp_Pi.main${NC}"
echo ""
echo -e "${YELLOW}To start/stop background service:${NC}"
echo -e "  Start service:  ${GREEN}sudo systemctl start wildlife.service${NC}"
echo -e "  Check status:   ${GREEN}sudo systemctl status wildlife.service${NC}"
echo -e "  Stop service:   ${GREEN}sudo systemctl stop wildlife.service${NC}"
echo -e "  View live logs: ${GREEN}sudo journalctl -u wildlife.service -f${NC}"
echo ""
