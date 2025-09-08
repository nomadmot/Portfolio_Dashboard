#! /bin/zsh
# This script is used to run the container for the first time
IMAGE_NAME=portfolio-dashboard-test:latest
CONTAINER_NAME=portfolio-dashboard-test
echo "Initializing image $IMAGE_NAME in container $CONTAINER_NAME"

# Mount the investor workspace to the container
MOUNT_DIR=/var/investorlab
WORKSPACE_DIR=/Users/nomadmot/Library/CloudStorage/Dropbox/Apps/Investing

echo "Mounting $WORKSPACE_DIR to $MOUNT_DIR"

# Start the new container
echo "Starting container"
podman run -it --detach --replace \
    --name $CONTAINER_NAME \
    -v $WORKSPACE_DIR:$MOUNT_DIR \
    -p 8080 \
    $IMAGE_NAME
