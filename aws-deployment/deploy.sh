#!/bin/bash

if [ $# -ne 1 ]; then
  echo "usage: deploy.sh [branch]" >&2
  exit 1
fi

branch=$1

# build docker image
cd ../api && \
git checkout $branch && \
git pull origin $branch && \
docker build . -t langgenius/dify-api:test

# recreate docker containers using image built above
cd ../docker && \
docker-compose up -d && \
docker logs -f docker-api-1
