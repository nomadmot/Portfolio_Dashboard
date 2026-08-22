#! /bin/bash

# stop the current container if running
docker container stop portfolio-dashboard

# remove the current container if it exists
docker container rm portfolio-dashboard

# run the docker container, mounting the open_webui data valume
docker run -d \
    --volume /Users/nomadmot/Library/CloudStorage/Dropbox/Apps/Investing/DUCK_PUDDLE:/var/data\
    --volume /Users/nomadmot/Library/CloudStorage/Dropbox/Apps/Investing/WATCHLISTS:/var/watchlists\
    --name portfolio-dashboard \
    --publish 8080:8501 \
    --restart always \
    localhost/portfolio-dashboard
