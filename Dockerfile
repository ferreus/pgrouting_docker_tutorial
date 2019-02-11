# We start from a good base, the pgrouting docker image we used in quick start
FROM pgrouting/pgrouting:v2.6.2-postgresql_11

#Add osmconvert to this docker
RUN apt install -y osmctools

# Fix the location of osm2pgrouting
RUN ln -s /usr/local/share/osm2pgrouting /usr/share/osm2pgrouting

# Add maps
ADD maps /maps

# Add our custom run.sh script
ADD run.sh /maps/run.sh

# Setup Entry point
WORKDIR /maps
ENTRYPOINT ["/maps/run.sh"]
CMD ["run_default"]