#!/bin/bash

# Usage: ./push_line.sh <file_path> "<new_line_content>"

FILE="/home/neeraj/BackUp/path_to_backup.txt"
NEW_LINE="$1"

# Ensure both arguments are provided
if [ -z "$NEW_LINE" ]; then
    echo "Usage: $0 \"<new_line_content>\""
    exit 1
fi

# Create the file if it doesn't exist
touch "$FILE"

# Read existing lines (if any)
LINES=()
while IFS= read -r line; do
    LINES+=("$line")
done < "$FILE"

# Keep only the last line (if exists)
if [ ${#LINES[@]} -ge 1 ]; then
    LAST_LINE="${LINES[-1]}"
else
    LAST_LINE=""
fi

# Overwrite file: previous last line becomes first, new line becomes second
{
    if [ -n "$LAST_LINE" ]; then
        echo "$LAST_LINE"
    fi
    echo "$NEW_LINE"
} > "$FILE"

# Confirm result
echo "✅ File updated:"
cat "$FILE"


# Check if file path is provided
if [ -z "$FILE" ]; then
    echo "Usage: $0 <file_path>"
    exit 1
fi

# Check if file exists and not empty
if [ ! -f "$FILE" ]; then
    echo "❌ Error: File '$FILE' not found."
    exit 1
elif [ ! -s "$FILE" ]; then
    echo "⚠️ File '$FILE' is empty."
    exit 1
fi

echo
echo "===================================================================="
# Read and print only the first line
FIRST_LINE=$(head -n 1 "$FILE")
echo "===================================================================="


