#!/bin/bash

# Script: folders_with_less_than_5_files.sh
# Usage: ./folders_with_less_than_5_files.sh /path/to/target_directory

# Check for input
if [ $# -ne 1 ]; then
    echo "Usage: $0 /path/to/directory"
    exit 1
fi

TARGET_DIR="$1"

# Check if input is a valid directory
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: '$TARGET_DIR' is not a valid directory."
    exit 1
fi

echo "Analyzing folders in: $TARGET_DIR"
echo "Folders with fewer than 5 files/subfolders:"

# Loop over top-level folders inside TARGET_DIR
for dir in "$TARGET_DIR"/*/; do
    # Skip if it's not a directory
    [ -d "$dir" ] || continue

    # Count immediate children (non-recursive)
    count=$(find "$dir" -mindepth 1 -maxdepth 1 | wc -l)

    if [ "$count" -lt 5 ]; then
        echo "$dir ($count items)"
    fi
done
