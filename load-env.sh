#!/bin/bash 

# Change to the settings directory
cd src/.settings

# Check if .env file exists  
if [ ! -f ".env" ]; then  
  echo "Error: .env file not found in current directory." >&2  
  exit 1  
fi  
 
# Load and export variables from .env  
while IFS= read -r line; do  
  # Skip comments (lines starting with #) and empty lines  
  if [[ "$line" =~ ^# || -z "$line" ]]; then  
    continue  
  fi 
  echo "Loading variable: $line"
  # Export the variable (KEY=VALUE)  
  export "$line"  
done < ".env"

# Change back to the old directory
cd  $OLDPWD
 
echo "✅ Successfully loaded environment variables from .env"