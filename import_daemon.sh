#!/bin/bash
# Author: Djetic Alexandre
# Date: 31/05/2024
# Modified: 31/05/2024
# Description: This script imports the daemons required by front-end and back-end

if [ $EUID -ne 0 ]; then
  echo "This script requires sudo/root access"
  exit 1
fi

# Copy both daemons
cp sysmanage.service /etc/systemd/system/
cp sysmanage_backend.service /etc/systemd/system/

# Reload systemd daemons
systemctl daemon-reload

# Start the daemons
systemctl start sysmanage
systemctl start sysmanage_backend

# Enable auto-start at boot
systemctl enable sysmanage
systemctl enable sysmanage_backend

