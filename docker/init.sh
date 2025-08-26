#! /bin/zsh
# This script is used to run the container for the first time

# Mount the investor workspace to the container
MOUNT_DIR=/var/investorlab
WORKSPACE_DIR=/Users/nomadmot/Library/CloudStorage/Dropbox/Apps/Investing

echo "Mounting $WORKSPACE_DIR to $MOUNT_DIR"

# Start the new container
echo "Starting container"
podman run -it --detach --replace \
    --name portfolio-dashboard \
    -v $WORKSPACE_DIR:$MOUNT_DIR \
    -p 8080:8080 \
    portfolio-dashboard:latest
# run the configuration script
