#!/bin/bash

if [ $# -ne 1 ]; then
  echo "usage: deploy.sh [branch]" >&2
  exit 1
fi

branch=$1
#tag_built="test"
tag_built="0.3.0"

# pull codes from remote branch, and get changed dir
ref_before=$(git rev-parse --short=10 HEAD)
git checkout $branch && \
git pull origin $branch
ref_after=$(git rev-parse --short=10 HEAD)
if [ "$ref_before" == "$ref_after" ]; then
  echo "no update, skip deployment..."
  exit 0
fi
changed_files=$(git diff $ref_before..$ref_after --stat | \
awk -F '|' '{ gsub(/(^ *)|( *$)/, "", $1); print $1 }' | \
head -n -1 | awk -F '/' '{ print $1 }' | sort -u)

# build docker image
echo "$changed_files" | grep -q "^api$" && \
cd ../api && \
docker build . -t langgenius/dify-api:$tag_built
# build docker image
echo "$changed_files" | grep -q "^web$" && \
cd ../web && \
docker build . -t langgenius/dify-web:$tag_built

# recreate docker containers using image built above
cd ../docker && \
docker-compose up -d && \
docker logs -f docker-api-1
