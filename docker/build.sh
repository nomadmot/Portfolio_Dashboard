#! /bin/sh
# This script builds the container image for the project.
#
# Usage:
#   ./build.sh [--tag TAG] [--name NAME] [--dockerhub] [-h|--help]
#
# Options:
#   --tag TAG       Tag for the built image (default: latest)
#   --name NAME     Image name (default: portfolio-dashboard)
#   --dockerhub     Push the image to DockerHub after building (default: do not push)
#   -h, --help      Show this help message and exit

REPOSITORY="docker.io/nomadmot"
IMAGE_NAME="portfolio-dashboard"
TAG_NAME="latest"
PUSH_TO_DOCKERHUB=false

usage() {
    cat <<EOF
Build the Portfolio Dashboard container image.

Usage: build.sh [OPTIONS]

Options:
  --tag TAG        Tag for the built image (default: latest)
  --name NAME      Image name (default: portfolio-dashboard)
  --dockerhub      Push the image to DockerHub after building (default: no push)
  -h, --help       Show this help message and exit

Examples:
  build.sh                              # build portfolio-dashboard:latest (no push)
  build.sh --tag v0.2.4                 # build portfolio-dashboard:v0.2.4 (no push)
  build.sh --tag v0.2.4 --dockerhub     # build and push to DockerHub
  build.sh --name my-dashboard --tag dev  # build my-dashboard:dev (no push)
EOF
}

# Parse command-line arguments. Both short (-t/-n/-d) and long (--tag/--name/
# --dockerhub) forms are accepted. Long flags may use the space or '=' form.
while [ $# -gt 0 ]; do
    case "$1" in
        -t)            [ $# -ge 2 ] || { echo "Error: $1 requires a value." >&2; usage; exit 1; }; TAG_NAME=$2; shift 2 ;;
        --tag)         [ $# -ge 2 ] || { echo "Error: $1 requires a value." >&2; usage; exit 1; }; TAG_NAME=$2; shift 2 ;;
        --tag=*)       TAG_NAME=${1#--tag=}; shift ;;
        -n)            [ $# -ge 2 ] || { echo "Error: $1 requires a value." >&2; usage; exit 1; }; IMAGE_NAME=$2; shift 2 ;;
        --name)        [ $# -ge 2 ] || { echo "Error: $1 requires a value." >&2; usage; exit 1; }; IMAGE_NAME=$2; shift 2 ;;
        --name=*)      IMAGE_NAME=${1#--name=}; shift ;;
        -d|--dockerhub) PUSH_TO_DOCKERHUB=true; shift ;;
        -h|--help)     usage; exit 0 ;;
        *)             echo "Error: unknown argument: $1" >&2; usage; exit 1 ;;
    esac
done

# Guard against a value-taking flag given in the '=' form with an empty value
# (e.g. "--tag="), which would leave the variable empty.
if [ -z "$TAG_NAME" ] || [ -z "$IMAGE_NAME" ]; then
    echo "Error: --tag and --name must both be non-empty." >&2
    usage
    exit 1
fi

echo "Building the container image: $IMAGE_NAME:$TAG_NAME"

# Remove any existing image with the same name
docker rmi --force --ignore "$IMAGE_NAME:$TAG_NAME"

# Change directory so build context is at project root
cd ../

# Build the image using the Dockerfile in the current directory
docker build -f docker/Dockerfile -t "$IMAGE_NAME:$TAG_NAME" --iidfile image_id .
IMAGE_ID=$(cat image_id)
echo "Successfully built image with ID: $IMAGE_ID"

# Push to DockerHub only when explicitly requested
if [ "$PUSH_TO_DOCKERHUB" = true ]; then
    FULL_IMAGE="$REPOSITORY/$IMAGE_NAME:$TAG_NAME"
    echo "Pushing image $IMAGE_ID to $FULL_IMAGE"
    docker login "$REPOSITORY"
    docker tag "$IMAGE_NAME:$TAG_NAME" "$FULL_IMAGE"
    docker push "$FULL_IMAGE"
else
    echo "Skipping DockerHub push (use --dockerhub to enable)."
fi
