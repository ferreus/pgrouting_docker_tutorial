# Creating docker image for our pgRouting database

We will base our pgRouting Dockerfile on the Dockerfile for pgrouting itself.
Which is based on postgres11 + postgis docker which in turn is based on ubuntu:bionic.

See this diagram to better understand this process.
![Dockerfile inheritance](/docs/pgRoutingDockerfile.png)

This is our Dockerfile:

```Dockerfile
FROM pgrouting/pgrouting:v2.6.2-postgresql_11

#Add osmconvert to this docker
RUN apt install -y osmctools

# Fix the location of osm2pgrouting
RUN ln -s /usr/local/share/osm2pgrouting /usr/share/osm2pgroutingInheritance

# Add maps
ADD maps /maps

# Add our custom run.sh script
ADD run.sh /maps/run.sh

# Setup Entry point
WORKDIR /maps
ENTRYPOINT ["/maps/run.sh"]
CMD ["run_default"]
```

Now, the most of the magic is happen inside the `run.sh` script.

I took the `run.sh` from the postgres/pg11 docker github:
[github.com/pgRouting/docker-pgrouting/blob/master/postgres/pg11/resources/run.sh](https://github.com/pgRouting/docker-pgrouting/blob/master/postgres/pg11/resources/run.sh)

And modified it.

## Why we need `run.sh` at all?
This is a script, that checks if we have a valid database configuration in our /data directory, if not, it completes the postgres installation, by creating the data directory. This is done on container start, and not during image creation to allow users to substitute (map) the data directory.

In our modification, on first start, we will initialize the data directory, and run osmconvert and osm2pgrouting.

There entire `run.sh` script is too long to list here,
So here is our additions to the script:

```bash
### OUR MODIFICATION (Do our database setup)
log "Configurating and adding postgres user to the database..."
su postgres -c "psql -U postgres -p 5432 -c \"CREATE ROLE \\\"user\\\" SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN PASSWORD 'user';\""
#wget https://download.geofabrik.de/asia/israel-and-palestine-latest.osm.pbf -O /maps/israel.osm.pbf
log "Preparing osm file..."
osmconvert /maps/israel.osm.pbf --drop-author --drop-version --out-osm -o=/maps/israel.osm
log "Creating routing database..."
su postgres -c "echo \"Creating db...\" && PGPASSWORD=user createdb -U user -w routing_db"
log "Preparing routing database..."
su postgres -c "PGPASSWORD=user psql -d routing_db -U user -w -c \"CREATE EXTENSION postgis;CREATE EXTENSION pgrouting;\""
log "Loading osm into database..."
osm2pgrouting -f /maps/israel.osm -d routing_db -U user -W user
### END OF OUR MODIFICATION
```

You can see the whole file [here](/run.sh)

You may notice that this are almost exact steps from our [quickStart guide](/docs/quickStart.md)

Now we ready to create the pgRouting docker image:

Our directory structure should look like that:

    .
    ├── Dockerfile
    ├── maps
    │   └── israel.osm.pbf
    └── run.sh


Let's build:

    docker build -t israel_pgrouting .

If successful you should have an `israel_pgrouting` image, in `docker images` output.

## Congratulations

You'be build another docker image, now you ready to start query_server and israel_pgrouting containers and make sure they see each other and the outside world.

Proceed to [next section](/docs/networking.md)
