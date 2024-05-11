#!/bin/bash

set -euo pipefail

export WIKI_DIR=~/Work/vt.wiki
export ROOT_DIR=~/Work/vt.wiki/build_stats
export GITHUB_REPOSITORY="DARMA-tasking/vt"
export INPUT_BUILD_STATS_OUTPUT=$ROOT_DIR
export INPUT_BUILD_RESULT_FILENAME="build_result.txt"
export INPUT_BUILD_TIMES_FILENAME="build_times.csv"
export INPUT_GRAPH_FILENAME="graph.png"
export INPUT_BADGE_FILENAME="build_status_badge.svg"
export INPUT_BADGE_TITLE="vt build times"
export INPUT_NUM_LAST_BUILD=25
export INPUT_X_LABEL="Run number"
export INPUT_Y_LABEL="Build time (min)"
export INPUT_GRAPH_WIDTH=20
export INPUT_GRAPH_HEIGHT=20
export INPUT_BADGE_LOGO="logo"
export INPUT_BADGE_FILENAME="badge_file"
export CXX=clang++-13
export CC=clang-13

WORKSPACE=$1
RUN_NUMBER=$2
BUILD_STATS_DIR=$3

cd "$WORKSPACE"

VT_BUILD_FOLDER="$WORKSPACE/build/vt"

########################
## CLONE DEPENDENCIES ##
########################

[ ! -d 'FlameGraph' ] && git clone https://github.com/brendangregg/FlameGraph.git
[ ! -d 'ClangBuildAnalyzer' ] && git clone https://github.com/aras-p/ClangBuildAnalyzer

cd ClangBuildAnalyzer
[ ! -d 'build' ] && mkdir build
cd build

cmake .. && make
chmod +x ClangBuildAnalyzer
ClangBuildTool="$WORKSPACE/ClangBuildAnalyzer/build/ClangBuildAnalyzer"

##################
## BUILD VT LIB ##
##################

cd "$WORKSPACE"
export VT_TESTS_ARGUMENTS="--vt_perf_gen_file"

# Build VT lib
[ ! -d 'vt' ] && git clone https://github.com/$GITHUB_REPOSITORY.git
eval "$BUILD_STATS_DIR/build_vt.sh" "$WORKSPACE/vt" "$WORKSPACE/build" "-ftime-trace" vt
vt_build_time=$(grep -oP 'real\s+\K\d+m\d+\.\d+s' "$VT_BUILD_FOLDER/build_time.txt")

# Build tests and examples
eval "$BUILD_STATS_DIR/build_vt.sh" "$WORKSPACE/vt" "$WORKSPACE/build" "-ftime-trace" all
tests_and_examples_build=$(grep -oP 'real\s+\K\d+m\d+\.\d+s' "$VT_BUILD_FOLDER/build_time.txt")

cp "$BUILD_STATS_DIR/ClangBuildAnalyzer.ini" .
$ClangBuildTool --all "$VT_BUILD_FOLDER" vt-build
$ClangBuildTool --analyze vt-build > build_result.txt

#######################
## PERFORMANCE TESTS ##
#######################

cd "$VT_BUILD_FOLDER"
ctest --output-on-failure --verbose -L perf_test
cd -

##########################
## GENERATE FLAMEGRAPHS ##
##########################

# Running 'mpirun -n x heaptrack' will generate x number of separate files, one for each node/rank
mpirun -n 2 heaptrack "$WORKSPACE/build/vt/examples/collection/jacobi2d_vt" 10 10 200
jacobi_output_list=$(ls -- *heaptrack.jacobi2d_vt.*.gz)

node_num=0
for file in ${jacobi_output_list}
do
    file_name="flame$node_num"

    # number of allocations
    heaptrack_print -f "$file" -F "alloc_count_$file_name"
    "$WORKSPACE/FlameGraph/flamegraph.pl" --title="jacobi2d_vt node:$node_num number of allocations"\
    --width=1920 --colors mem --countname allocations < "alloc_count_$file_name" > "flame_heaptrack_jacobi_alloc_count_$node_num.svg"

    # leaked
    heaptrack_print -f "$file" -F "leaked_$file_name" --flamegraph-cost-type leaked
    "$WORKSPACE/FlameGraph/flamegraph.pl" --title="jacobi2d_vt node:$node_num number of bytes leaked"\
    --width=1920 --colors mem --countname bytes < "leaked_$file_name" > "flame_heaptrack_jacobi_leaked_$node_num.svg"

    ((node_num=node_num+1))
done

#####################
## GENERATE GRAPHS ##
#####################

cd "$WIKI_DIR" || exit 1

# Generate graph
# python3 "$BUILD_STATS_DIR/generate_build_graph.py" -vt "$vt_build_time" -te "$tests_and_examples_build" -r "$RUN_NUMBER"
perf_test_files=$(find "$VT_BUILD_FOLDER/tests/" -name "*_mem.csv" | sed 's!.*/!!' | sed -e 's/_mem.csv$//')

cd perf_tests

# for file in $perf_test_files
# do
#     # Each test generates both time/mem files
#     time_file="${file}_time.csv"
#     memory_file="${file}_mem.csv"
#     echo "Test files $VT_BUILD_FOLDER/tests/$time_file $VT_BUILD_FOLDER/tests/$memory_file for test: $file"
#     python3 "$BUILD_STATS_DIR/generate_perf_graph.py" -time "$VT_BUILD_FOLDER/tests/$time_file"\
#     -mem "$VT_BUILD_FOLDER/tests/$memory_file" -r "$RUN_NUMBER" -wiki "$WIKI_DIR"
# done
python3 "$BUILD_STATS_DIR/generate_perf_graph.py"
cd -

cp "$WORKSPACE/build_result.txt" "$INPUT_BUILD_STATS_OUTPUT"
eval cp "$WORKSPACE/flame_heaptrack*" "./perf_tests/"

# python3 "$BUILD_STATS_DIR/generate_wiki_pages.py" -t "$perf_test_files"

exit 0
