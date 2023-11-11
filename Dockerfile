FROM lifflander1/vt:amd64-ubuntu-22.04-clang-14-cpp

RUN apt-get update -y -q && \
    apt-get install -y -q --no-install-recommends \
    python3-pip heaptrack\
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install matplotlib pandas requests

COPY ClangBuildAnalyzer.ini /

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

COPY generate_build_graph.py /
RUN chmod +x /generate_build_graph.py

COPY generate_perf_graph.py /
RUN chmod +x /generate_perf_graph.py

COPY generate_wiki_pages.py /
RUN chmod +x /generate_wiki_pages.py

COPY build_vt.sh /
RUN chmod +x /build_vt.sh

RUN ln -s /usr/bin/python3 /usr/bin/python

ENTRYPOINT ["/entrypoint.sh"]
