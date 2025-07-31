#!/bin/bash

# Script to create a new sudo docker volume and copy data from an existing container
# sudo docker ps
# sh ./create_volume.sh <container_id>

# Check if required arguments are provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <source_container> [source_path] [new_volume_name]"
    echo "Example: $0 n8n /home/node/.n8n n8n-genie_n8n_data"
    echo "Defaults: source_path=/home/node/.n8n, new_volume_name=n8n-genie_n8n_data"
    exit 1
fi

SOURCE_CONTAINER="$1"
SOURCE_PATH="${2:-/home/node/.n8n}"
NEW_VOLUME="${3:-n8n-genie_n8n_data}"

echo "Creating new volume: $NEW_VOLUME"
sudo docker volume create "$NEW_VOLUME"

if [ $? -ne 0 ]; then
    echo "Error: Failed to create volume $NEW_VOLUME"
    exit 1
fi

echo "Volume $NEW_VOLUME created successfully"

# Check if source container exists
if ! sudo docker container inspect "$SOURCE_CONTAINER" > /dev/null 2>&1; then
    echo "Error: Container $SOURCE_CONTAINER does not exist"
    sudo docker volume rm "$NEW_VOLUME"
    exit 1
fi

echo "Copying data from container $SOURCE_CONTAINER:$SOURCE_PATH to volume $NEW_VOLUME"

# Create temporary directory for data transfer
TEMP_DIR="/tmp/container-data-$(date +%s)"

# Copy data from container to host
echo "Copying data from container to temporary directory..."
sudo docker cp "$SOURCE_CONTAINER:$SOURCE_PATH" "$TEMP_DIR"

if [ $? -ne 0 ]; then
    echo "Error: Failed to copy data from container"
    sudo docker volume rm "$NEW_VOLUME"
    exit 1
fi

# Copy data from host to new volume
echo "Copying data from temporary directory to volume..."
sudo docker run --rm -v "$TEMP_DIR":/from:ro -v "$NEW_VOLUME":/to alpine sh -c "
    cp -av /from/. /to/ && 
    chown -R 1000:1000 /to &&
    chmod -R 755 /to
"

if [ $? -eq 0 ]; then
    echo "Data copied successfully from $SOURCE_CONTAINER:$SOURCE_PATH to volume $NEW_VOLUME"
else
    echo "Error: Failed to copy data to volume"
    sudo docker volume rm "$NEW_VOLUME"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Clean up temporary directory
echo "Cleaning up temporary directory..."
sudo rm -rf "$TEMP_DIR"

echo "Volume $NEW_VOLUME is ready to use"