#!/bin/bash

cd $HOME/.inorbit/local
AGENT_SH="agent.sh"
AGENT_ENV_SH="agent.env.sh"

# 1. Ensure both files exist
if [ ! -f "$AGENT_SH" ] || [ ! -f "$AGENT_ENV_SH" ]; then
    echo "Error: Required files not found in the current directory."
    exit 1
fi

# 2. Source agent.sh to evaluate the variables into the script's environment
source "$AGENT_SH"

# 3. Safely extract just the variable names from agent.sh using awk
# This looks for lines starting with 'export ' and drops everything after '='
var_names=$(awk '/^export / {gsub(/=.*/, "", $2); print $2}' "$AGENT_SH")

# 4. Loop through each extracted variable and update agent.env.sh
for var_name in $var_names; do
    
    # Grab the evaluated value using bash indirect expansion
    var_value="${!var_name}"
    
    # Use '|' as the sed delimiter so slashes in paths or URLs don't break the command
    if grep -q "^export $var_name=" "$AGENT_ENV_SH"; then
        sed -i "s|^export $var_name=.*|export $var_name=\"$var_value\"|" "$AGENT_ENV_SH"
    else
        echo "export $var_name=\"$var_value\"" >> "$AGENT_ENV_SH"
    fi
    
    echo "Updated $var_name"
done

# 5. Execute the target script in the background
echo "Starting InOrbit agent..."
~/.inorbit/dist/scripts/start.sh &

# 6. Capture and save the PID of the background process
INORBIT_PID=$!
echo "InOrbit agent started with PID: $INORBIT_PID"
echo "InOrbit agent started with PID: $INORBIT_PID" > "$HOME/inorbit_agentpid.txt"