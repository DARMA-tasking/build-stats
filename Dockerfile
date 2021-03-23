FROM ubuntu:latest

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

COPY generate_graph.py /
RUN chmod +x /generate_graph.py

# Install all required packages like git/python/matplotlib
RUN apt-get update && apt-get install python3 -y && \
    apt-get install python3-pip -y && apt-get install git -y
RUN pip3 install matplotlib pandas requests

ENTRYPOINT ["/entrypoint.sh"]
