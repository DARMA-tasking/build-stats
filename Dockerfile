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
    clang-10 \
    python3-pip \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# The above probably should be prebuilt image
RUN pip3 install matplotlib pandas requests

RUN ln -s \
    "$(which $(echo clang-10 | cut -d- -f1)++-$(echo clang-10  | cut -d- -f2))" \
    /usr/bin/clang++

ENTRYPOINT ["/entrypoint.sh"]
