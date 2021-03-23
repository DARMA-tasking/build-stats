#!/bin/bash

set -euo pipefail

if [ -z "$GITHUB_ACTOR" ]; then
    echo "GITHUB_ACTOR environment variable is not set"
    exit 1
fi

if [ -z "$GITHUB_REPOSITORY" ]; then
    echo "GITHUB_REPOSITORY environment variable is not set"
    exit 1
fi

if [ -z "${INPUT_GITHUB_PERSONAL_TOKEN}" ]; then
    echo "github-personal-token environment variable is not set"
    exit 1
fi

# docker build -t ${INPUT_DOCKER_REPOSITORY}:${INPUT_TAG} .

# containerId=$(docker create ${INPUT_DOCKER_REPOSITORY}:${INPUT_TAG})
# docker cp "$containerId":"${INPUT_LAST_BUILD_TIME_FILE}" ./last_build.txt
# docker rm "$containerId"

# echo "${INPUT_DOCKER_PASSWORD}" | docker login -u ${INPUT_DOCKER_USERNAME} --password-stdin docker.io
# docker push ${INPUT_DOCKER_REPOSITORY}:latest

GIT_REPOSITORY_URL="https://${INPUT_GITHUB_PERSONAL_TOKEN}@github.com/$GITHUB_REPOSITORY.wiki.git"

tmp_dir=$(mktemp -d -t ci-XXXXXXXXXX)
(
    cd "$tmp_dir" || exit 1
    git init
    git config user.name "$GITHUB_ACTOR"
    git config user.email "$GITHUB_ACTOR@users.noreply.github.com"
    git pull "$GIT_REPOSITORY_URL"

    # build_time=$(ls -l | grep -oP 'real\s+\K\d+m\d+\.\d+s' "$GITHUB_WORKSPACE"/last_build.txt)
    # echo $build_time

    # Generate graph
    python3 /generate_graph.py -t $INPUT_LAST_BUILD_TIME -r $INPUT_RUN_NUMBER

    # git add .
    # git commit -m "$INPUT_COMMIT_MESSAGE"
    # git push --set-upstream "$GIT_REPOSITORY_URL" master
) || exit 1

rm -rf "$tmp_dir"

exit 0
