#!/usr/bin/env bash

set -ex

source_dir=${1}
build_dir=${2}
extra_flags=${3}

# Dependency versions, when fetched via git.
checkpoint_rev=develop

mkdir -p "${build_dir}"
pushd "${build_dir}"

export CHECKPOINT_BUILD=${build_dir}/checkpoint

if test -d "${build_dir}/checkpoint"
then
    { echo "Checkpoint already in lib... not downloading, building, and installing"; } 2>/dev/null
else
    git clone -b "${checkpoint_rev}" --depth 1 https://github.com/DARMA-tasking/checkpoint.git
    export CHECKPOINT=$PWD/checkpoint

    mkdir -p "$CHECKPOINT_BUILD"
    cd "$CHECKPOINT_BUILD"
    mkdir build
    cd build
    cmake -G "${CMAKE_GENERATOR:-Ninja}" \
          -DCMAKE_INSTALL_PREFIX="$CHECKPOINT_BUILD/install" \
          -Ddetector_DIR="$DETECTOR_BUILD/install" \
          "$CHECKPOINT"
    cmake --build . --target install
fi

export VT=${source_dir}
export VT_BUILD=${build_dir}/vt

mkdir -p "$VT_BUILD"
cd "$VT_BUILD"

cmake -G "${CMAKE_GENERATOR:-Ninja}" \
      -DCMAKE_EXPORT_COMPILE_COMMANDS=1 \
      -Dvt_test_trace_runtime_enabled="${VT_TRACE_RUNTIME_ENABLED:-0}" \
      -Dvt_lb_enabled="${VT_LB_ENABLED:-1}" \
      -Dvt_trace_enabled="${VT_TRACE_ENABLED:-0}" \
      -Dvt_doxygen_enabled="${VT_DOXYGEN_ENABLED:-0}" \
      -Dvt_mimalloc_enabled="${VT_MIMALLOC_ENABLED:-0}" \
      -Dvt_asan_enabled="${VT_ASAN_ENABLED:-0}" \
      -Dvt_pool_enabled="${VT_POOL_ENABLED:-1}" \
      -Dvt_build_extended_tests="${VT_EXTENDED_TESTS_ENABLED:-1}" \
      -Dvt_zoltan_enabled="${VT_ZOLTAN_ENABLED:-0}" \
      -Dvt_production_build_enabled="${VT_PRODUCTION_BUILD_ENABLED:-0}" \
      -Dvt_unity_build_enabled="${VT_UNITY_BUILD_ENABLED:-0}" \
      -Dvt_diagnostics_enabled="${VT_DIAGNOSTICS_ENABLED:-1}" \
      -Dvt_diagnostics_runtime_enabled="${VT_DIAGNOSTICS_RUNTIME_ENABLED:-0}" \
      -Dvt_fcontext_enabled="${VT_FCONTEXT_ENABLED:-0}" \
      -Dvt_fcontext_build_tests_examples="${VT_FCONTEXT_BUILD_TESTS_EXAMPLES:-0}" \
      -DUSE_OPENMP="${VT_USE_OPENMP:-0}" \
      -DUSE_STD_THREAD="${VT_USE_STD_THREAD:-0}" \
      -DCODE_COVERAGE="${CODE_COVERAGE:-0}" \
      -DMI_INTERPOSE:BOOL=ON \
      -DMI_OVERRIDE:BOOL=ON \
      -Dvt_mpi_guards="${VT_MPI_GUARD_ENABLED:-0}" \
      -DMPI_EXTRA_FLAGS="${MPI_EXTRA_FLAGS:-}" \
      -DCMAKE_BUILD_TYPE="${CMAKE_BUILD_TYPE:-Release}" \
      -DMPI_C_COMPILER="${MPICC:-mpicc}" \
      -DMPI_CXX_COMPILER="${MPICXX:-mpicxx}" \
      -DCMAKE_CXX_COMPILER="${CXX:-c++}" \
      -DCMAKE_C_COMPILER="${CC:-cc}" \
      -DCMAKE_EXE_LINKER_FLAGS="${CMAKE_EXE_LINKER_FLAGS:-}" \
      -Dcheckpoint_ROOT="$CHECKPOINT_BUILD/install" \
      -DCMAKE_PREFIX_PATH="${CMAKE_PREFIX_PATH:-}" \
      -DCMAKE_INSTALL_PREFIX="$VT_BUILD/install" \
      -Dvt_ci_build="${VT_CI_BUILD:-0}" \
      -DCMAKE_CXX_FLAGS="${extra_flags:-}" \
      -Dvt_tests_num_nodes=2 \
      "$VT"

{ time cmake --build . --target "${4}" ; } 2> >(tee build_time.txt)
