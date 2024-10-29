#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$(dirname "$0")"

# Define the source and destination paths
SOURCE_FILE="$SCRIPT_DIR/.env.example"
DESTINATION_FILE="$SCRIPT_DIR/../.env"

# Check if the source file exists
if [[ -f "$SOURCE_FILE" ]]; then
    # Move the file (copy and remove the original)
cp "$SOURCE_FILE" "$DESTINATION_FILE"
    echo "Moved $SOURCE_FILE to $DESTINATION_FILE"
else
    echo "Error: $SOURCE_FILE does not exist."
fi
