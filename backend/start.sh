#!/bin/bash
# Author: Djetic Alexandre
# Date: 24/04/2024
# Modified: 24/04/2024

# Function to install dependencies
function install_dependencies {
  echo "Installing dependencies..."
  pip install -r requirements.txt --break-system-packages
  if [ $? -eq 0 ]; then
    echo "Dependencies installed successfully."
  else
    echo "Failed to install dependencies. Exiting."
    exit 1
  fi
}

# Function to check if dependencies and ports are available
function check_requirements {
  if ! command -v uvicorn &> /dev/null; then
    echo "Uvicorn is not installed. Installing..."
    install_dependencies
  fi

  if lsof -i :$PORT &> /dev/null; then
    echo "Port $PORT is already in use. Exiting."
    exit 1
  fi
}

# Function to display script usage
function show_help {
  echo "Usage: $0 [-p PORT]"
  echo "Options:"
  echo "  -p, --port PORT  Specify the port to listen on (default: 13500)"
  exit 1
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -p|--port)
      if [ -z "$2" ]; then
        echo "Error: Option '--port' requires an argument."
        show_help
      fi
      PORT="$2"
      shift # past argument
      shift # past value
      ;;
    *)
      # Unknown option
      show_help
      ;;
  esac
done

# If port is not provided, use default value
if [ -z "$PORT" ]; then
  PORT=13500
fi

# Check and install dependencies, check port availability
check_requirements

# Launch the API
echo "Launching the API on port $PORT..."
uvicorn app:app --reload --port $PORT

