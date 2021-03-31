#!/bin/bash

set -euo pipefail

cd "$GITHUB_WORKSPACE"

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

wget https://include-what-you-use.org/downloads/include-what-you-use-0.14.src.tar.gz
tar xzf include-what-you-use-0.14.src.tar.gz --one-top-level=include-what-you-use --strip-components 1



git clone https://github.com/aras-p/ClangBuildAnalyzer
cd ClangBuildAnalyzer
mkdir build && cd build

cmake .. && make

ClangBuildTool="$GITHUB_WORKSPACE/ClangBuildAnalyzer/build/ClangBuildAnalyzer"
cd "$GITHUB_WORKSPACE"


# BUILD VT
mkdir build
$ClangBuildTool --start vt-build
./build_vt.sh /vt /build
$ClangBuildTool --stop vt-build > build_result.txt
cat build_result.txt

build_time=$(grep -oP 'real\s+\K\d+m\d+\.\d+s' build_time.txt)


# GENERATE BUILD TIME GRAPH

tmp_dir=$(mktemp -d -t ci-XXXXXXXXXX)
(
    WIKI_URL="https://${INPUT_GITHUB_PERSONAL_TOKEN}@github.com/$GITHUB_REPOSITORY.wiki.git"

    cd "$tmp_dir" || exit 1
    git init
    git config user.name "$GITHUB_ACTOR"
    git config user.email "$GITHUB_ACTOR@users.noreply.github.com"
    git pull "$WIKI_URL"

    # Generate graph
    python3 /generate_graph.py -t $build_time -r $INPUT_RUN_NUMBER

    # git add .
    # git commit -m "$INPUT_COMMIT_MESSAGE"
    # git push --set-upstream "$WIKI_URL" master
) || exit 1

rm -rf "$tmp_dir"

exit 0
