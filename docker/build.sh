#! /bin/zsh
# This script builds the container image for the project.
REPOSITORY=docker.io/nomadmot
IMAGE_NAME=portfolio-dashboard
TAG_NAME=latest
echo "Building the container image: $IMAGE_NAME:$TAG_NAME"

# Remove any existing image with the same name
docker rmi --force --ignore $IMAGE_NAME

# Change directory so build context is at project root
cd ../

# Build the image using the Dockerfile in the current directory
docker build -f docker/Dockerfile -t $IMAGE_NAME  --iidfile image_id .
IMAGE_ID=`cat image_id`
echo "Successfully built image with ID: $IMAGE_ID"

# push to DockerHub
echo "Pushing image $IMAGE_ID to $REPOSITORY/$IMAGE_NAME:$TAG_NAME"
docker login docker.io/nomadmot
docker push $IMAGE_ID $REPOSITORY/$IMAGE_NAME:$TAG_NAME
