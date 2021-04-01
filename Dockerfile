FROM lifflander1/vt:amd64-ubuntu-20.04-gcc-9-cpp

ENV CC=clang-10 \
    CXX=clang++

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

COPY generate_graph.py /
RUN chmod +x /generate_graph.py

COPY build_vt.sh /
RUN chmod +x /build_vt.sh

RUN apt-get update -y -q && \
    apt-get install -y -q --no-install-recommends \
    libc++-10-dev llvm-dev \
    clang-10 libclang-10-dev \
    python3-pip \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# The above probably should be prebuilt image
RUN pip3 install matplotlib pandas requests

RUN ln -s /usr/bin/clang++-10 /usr/bin/clang++
RUN ln -s /usr/bin/python3 /usr/bin/python

ENTRYPOINT ["/entrypoint.sh"]
