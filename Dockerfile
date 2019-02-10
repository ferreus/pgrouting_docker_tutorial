FROM pgrouting/pgrouting:v2.6.2-postgresql_11
RUN apt install -y osmctools
ADD maps /maps
ADD run.sh /maps/run.sh
WORKDIR /maps
ENTRYPOINT ["/maps/run.sh"]
CMD ["run_default"]

