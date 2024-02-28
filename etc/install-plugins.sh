#!/bin/bash

# Check if the PLUGINS environment variable is defined
if [ -z "$PLUGINS" ]; then
  exit 1
fi

packages=$(echo "$PLUGINS" | tr ',' ' ')
pip install $packages

echo "Plugins installation completed."
