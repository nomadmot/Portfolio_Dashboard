#! /bin/zsh
# This script builds the container image for the project.

# Remove any existing image with the same name
podman rm -f portfolio-dashboard:latest
podman rmi -f portfolio-dashboard:latest

# Change directory so build context is at project root
cd ../

# Build the image using the Dockerfile in the current directory
podman build -f docker/Dockerfile -t portfolio-dashboard:latest .

