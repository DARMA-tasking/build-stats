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

VT_BUILD_FOLDER="$GITHUB_WORKSPACE/build/vt"

git clone https://github.com/brendangregg/FlameGraph.git

# ClangBuildAnalyzer
git clone https://github.com/aras-p/ClangBuildAnalyzer
cd ClangBuildAnalyzer
mkdir build && cd build

cmake .. && make
chmod +x ClangBuildAnalyzer
ClangBuildTool="$GITHUB_WORKSPACE/ClangBuildAnalyzer/build/ClangBuildAnalyzer"
cd "$GITHUB_WORKSPACE"

# Build VT lib
/build_vt.sh "$GITHUB_WORKSPACE" "$GITHUB_WORKSPACE/build" "-ftime-trace" vt
vt_build_time=$(grep -oP 'real\s+\K\d+m\d+\.\d+s' "$VT_BUILD_FOLDER/build_time.txt")

# Build tests and examples
/build_vt.sh "$GITHUB_WORKSPACE" "$GITHUB_WORKSPACE/build" "-ftime-trace" all
tests_and_examples_build=$(grep -oP 'real\s+\K\d+m\d+\.\d+s' "$VT_BUILD_FOLDER/build_time.txt")

# cp /ClangBuildAnalyzer.ini .
# $ClangBuildTool --all "$VT_BUILD_FOLDER" vt-build
# $ClangBuildTool --analyze vt-build > build_result.txt

mpirun -n 2 $GITHUB_WORKSPACE/build/vt/tests/ping_pong --vt_quiet --vt_perf_gen_file
cat ./test_ping_pong.csv

# Generate flamegraphs
# Running 'mpirun -n x heaptrack' will generate x number of separate files, one for each node/rank

mpirun -n 2 heaptrack $GITHUB_WORKSPACE/build/vt/examples/collection/jacobi2d_vt 10 10 200
jacobi_output_list=$(ls | grep "heaptrack.jacobi2d_vt.*.gz")

node_num=0
for file in ${jacobi_output_list}
do
    file_name="flame$node_num"

    heaptrack_print -f "$file" -F "alloc_count_$file_name"
    heaptrack_print -f "$file" -F "alloc_size_$file_name" --flamegraph-cost-type allocated

    "$GITHUB_WORKSPACE/FlameGraph/flamegraph.pl" --title="jacobi2d_vt node:$node_num" --width=1920 --colors mem\
     --countname allocations < "alloc_count_$file_name" > "flame_heaptrack_jacobi_alloc_count_$node_num.svg"

    "$GITHUB_WORKSPACE/FlameGraph/flamegraph.pl" --title="jacobi2d_vt node:$node_num" --width=1920 --colors mem\
     --countname allocations < "alloc_size_$file_name" > "flame_heaptrack_jacobi_alloc_size_$node_num.svg"

    ((node_num=node_num+1))
done

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
    # python3 /generate_graph.py -vt "$vt_build_time" -te "$tests_and_examples_build" -r "$GITHUB_RUN_NUMBER"

    # cp "$GITHUB_WORKSPACE/build_result.txt" "$INPUT_BUILD_STATS_OUTPUT"

    eval cp "$GITHUB_WORKSPACE/flame_heaptrack*" "./perf_tests/"
    # python3 /generate_wiki_page.py

    git add .
    git commit -m "$INPUT_COMMIT_MESSAGE"
    git push --set-upstream "$WIKI_URL" master
) || exit 1

rm -rf "$tmp_dir"

exit 0
