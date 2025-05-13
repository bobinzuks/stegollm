#!/bin/bash

# Script to activate the virtual environment and run StegoLLM

# Define the virtual environment directory
VENV_DIR=".venv"
PROJECT_ROOT=$(pwd) # Assumes script is run from project root

echo "StegoLLM Start Script"
echo "---------------------"
echo "Project Root: $PROJECT_ROOT"
echo "Virtual Env Dir: $VENV_DIR"

# Check if the virtual environment directory exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment directory '$VENV_DIR' not found."
    echo "Please ensure the virtual environment is created (e.g., python3 -m venv .venv) and dependencies are installed."
    exit 1
fi

# Check if the activation script exists
ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"
if [ ! -f "$ACTIVATE_SCRIPT" ]; then
    echo "Error: Activation script '$ACTIVATE_SCRIPT' not found in the virtual environment."
    echo "The virtual environment might be corrupted or not set up correctly."
    exit 1
fi

echo "Activating virtual environment..."
# shellcheck disable=SC1090
source "$ACTIVATE_SCRIPT"

# Check if activation was successful (optional, $VIRTUAL_ENV is usually set)
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Error: Virtual environment activation failed."
    exit 1
fi
echo "Virtual environment activated: $VIRTUAL_ENV"

echo "Running StegoLLM..."
stegollm start
# Run with custom config
stegollm start --config ./stegollm/config/custom_config.yaml

# Deactivation is usually handled by the user closing the shell or explicitly.
# If you want to auto-deactivate, you could add 'deactivate' here,
# but then the user wouldn't see any errors if stegollm exits immediately.
# For a server, it's better to leave it active until Ctrl+C.

echo "---------------------"
echo "StegoLLM script finished or was interrupted."