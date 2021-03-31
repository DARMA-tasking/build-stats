# FROM lifflander1/vt:amd64-ubuntu-20.04-clang-10-cpp
FROM ubuntu:latest

ENV CC=gcc \
    CXX=clang++

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

COPY generate_graph.py /
RUN chmod +x /generate_graph.py

COPY build_vt.sh /
RUN chmod +x /build_vt.sh

RUN apt-get update -y -q && \
    apt-get install -y -q --no-install-recommends \
    ca-certificates \
    less \
    curl \
    git \
    wget \
    clang-10 \
    zlib1g \
    zlib1g-dev \
    ninja-build \
    valgrind \
    make-guile \
    libomp5 \
    python3 \
    python3-pip \
    ssh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# The above probably should be prebuilt image
RUN pip3 install matplotlib pandas requests

ENTRYPOINT ["/entrypoint.sh"]
