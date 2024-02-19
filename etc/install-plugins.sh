#!/bin/bash

# Check if the PLUGINS environment variable is defined
if [ -z "$PLUGINS" ]; then
  exit 1
fi

# Split the list of plugins using a comma as the delimiter
IFS=',' read -ra plugins <<< "$PLUGINS"

# Iterate over the libraries and install each one
for plugin in "${plugins[@]}"; do
  echo "Installing plugin: $plugin"
  pip install "$plugin"
done

echo "Plugins installation completed."
