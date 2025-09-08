#! /bin/zsh
# This script builds the container image for the project.
IMAGE_NAME=portfolio-dashboard
echo "Building the container image: $IMAGE_NAME"

# Remove any existing image with the same name
podman rmi -f $IMAGE_NAME

# Change directory so build context is at project root
cd ../

# Build the image using the Dockerfile in the current directory
podman build -f docker/Dockerfile -t $IMAGE_NAME  --iidfile image_id .
IMAGE_ID=`cat image_id`
echo "Successfully built image with ID: $IMAGE_ID"

# initialize the container
docker/init.sh

# push to DockerHub
echo "Pushing image $IMAGE_ID to DockerHub as $IMAGE_NAME"
podman login docker.io
podman push $IMAGE_ID tdamon/nomadmot:$IMAGE_NAME
