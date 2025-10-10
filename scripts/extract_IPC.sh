#!/bin/bash

# ==============================
# IPC Extraction Script (non-interactive)
# Usage: ./extract_ipc.sh <SUBDIR> <ExpNo> <IPC_SUBDIR>
# ==============================

if [ $# -ne 3 ]; then
    echo "Usage: $0 <Prefetcher's_level> <RESULTS_SUBDIR> <ExpNo> "
    exit 1
fi

SUBDIR=$2
ExpNo=$3


RESULT_DIR="../results/$1/$SUBDIR/$ExpNo"
OUT_DIR="../Statistics/IPC_all/$1/$SUBDIR"
OUT_FILE="$OUT_DIR/IPC_value_${ExpNo}.txt"

# Check if the result directory exists
if [ ! -d "$RESULT_DIR" ]; then
    echo "❌ Error: Directory '$RESULT_DIR' does not exist. Please check the name and try again."
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUT_DIR"

# Ensure output file exists
touch "$OUT_FILE"

# Temporary file for updated results
TEMP_FILE=$(mktemp)

# Copy old results into temp
cp "$OUT_FILE" "$TEMP_FILE"

# Process each result file
for file in "$RESULT_DIR"/*; do
    fname=$(basename "$file")

    # Extract IPC
    ipc=$(grep "CPU 0 cumulative IPC" "$file" | awk '{print $5}')

    # If file entry already exists in OUT_FILE
    if grep -q "^$fname" "$OUT_FILE"; then
        existing_ipc=$(grep "^$fname" "$OUT_FILE" | awk '{print $2}')
        
        if [ -z "$existing_ipc" ] || [ "$existing_ipc" = " " ]; then
            echo "Updating $fname with new IPC $ipc"
            sed -i "s/^$fname:.*/$fname: $ipc/" "$TEMP_FILE"
        else
            echo "Skipping $fname (already exists with IPC)"
        fi
    else
        echo "Adding $fname $ipc"
        echo "$fname: $ipc" >> "$TEMP_FILE"
    fi
done

# Sort results by trace name
sort -k1,1 "$TEMP_FILE" -o "$TEMP_FILE"

# Replace old file with updated temp
mv "$TEMP_FILE" "$OUT_FILE"

echo "✅ IPC extraction for '$SUBDIR' updated and sorted. Stored in $OUT_FILE"
