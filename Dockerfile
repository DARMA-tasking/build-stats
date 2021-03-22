FROM jdomagala/docker_with_matplotlib:latest

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

COPY generate_graph.py /
RUN chmod +x /generate_graph.py

ENTRYPOINT ["/entrypoint.sh"]
