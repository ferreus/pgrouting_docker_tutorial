#!/bin/bash

set -e

log(){
    echo "$(date +"%Y-%m-%d %T") > $1" >> /log.txt
}

# Generate locale
LANG=${LOCALE}.${ENCODING}

locale-gen ${LANG} > /dev/null

log "Locale ${LOCALE}.${ENCODING} generated"



# Check if command is just "run_default"

if [ "$1" = 'run_default' ]; then
  log "Running server"

  # Check if data folder is empty. If it is, configure the dataserver
  if [ -z "$(ls -A "/data/")" ]; then
    log "Initializing datastore..."

    chown postgres:postgres /data

    # Create datastore
    su postgres -c "initdb --encoding=${ENCODING} --locale=${LANG} --lc-collate=${LANG} --lc-monetary=${LANG} --lc-numeric=${LANG} --lc-time=${LANG} -D /data/"

    log "Datastore created..."

    # Create log folder
    mkdir -p /data/logs
    chown postgres:postgres /data/logs

    log "Log folder created..."

    # Erase default configuration and initialize it
    su postgres -c "rm /data/pg_hba.conf"
    su postgres -c "pg_hba_conf a \"${PG_HBA}\""

    # Modify basic configuration
    su postgres -c "rm /data/postgresql.conf"
    PG_CONF="${PG_CONF}#lc_messages='${LANG}'#lc_monetary='${LANG}'#lc_numeric='${LANG}'#lc_time='${LANG}'"
    su postgres -c "postgresql_conf a \"${PG_CONF}\""

    # Establish postgres user password and run the database
    su postgres -c "pg_ctl -w -D /data/ start"
    su postgres -c "psql -h localhost -U postgres -p 5432 -c \"alter role postgres password '${POSTGRES_PASSWD}';\""

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


    log "Stopping the server..."

    # Stop the server
    su postgres -c "pg_ctl -w -D /data/ stop"
  else
    log "Datastore already exists..."
  fi

  log "Starting the server..."

  # Start the database
  exec gosu postgres postgres -D /data/
else
  exec env "$@"
fi



