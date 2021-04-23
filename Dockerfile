FROM lifflander1/vt:amd64-ubuntu-20.04-clang-10-cpp

RUN apt-get update -y -q && \
    apt-get install -y -q --no-install-recommends \
    python3-pip \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install matplotlib pandas requests

# The above probably should be prebuilt image

COPY ClangBuildAnalyzer.ini /

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

COPY generate_graph.py /
RUN chmod +x /generate_graph.py

COPY generate_wiki_page.py /
RUN chmod +x /generate_wiki_page.py

COPY build_vt.sh /
RUN chmod +x /build_vt.sh

RUN ln -s /usr/bin/python3 /usr/bin/python

ENTRYPOINT ["/entrypoint.sh"]
