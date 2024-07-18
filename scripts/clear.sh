#!/bin/bash

# Variables for directories
root="./"
sub_directory="./missing_tradition"

# Loop through the files in the sub-directory
for file in "$sub_directory"/*; do
  # Extract the file name without the path
  file_name=$(basename "$file")
  
  # Check if the file exists in the root directory
  if [ -e "$root/$file_name" ]; then
    # Delete the file in the root directory
    rm "$root/$file_name"
  fi
done

echo "Operation completed."
