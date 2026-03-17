#!/bin/bash
set -e # Stops the script immediately if any command fails

# 1. Check if the key is provided
if [ -z "$INORBIT_LIFTOFF_KEY" ]; then
    echo "Error: INORBIT_LIFTOFF_KEY environment variable is not set."
    exit 1
fi

# 2. Copy agent.sh to agent.env.sh
cd $HOME/.inorbit/local
cp agent.sh agent.env.sh

# 3. Download the installer (putting the URL in quotes is safer)
curl -fsSL "https://control.inorbit.ai/liftoff/$INORBIT_LIFTOFF_KEY" -o /tmp/installer.sh

# 4. Strip out the interactive prompts
sed -i '/Press ENTER to resume installation or CTRL\+C to cancel\./d;/read -r input <\/dev\/tty/d' /tmp/installer.sh

# 5. Execute the installer (using bash is usually safer)
bash /tmp/installer.sh