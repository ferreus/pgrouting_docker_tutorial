# Introduction

This is a simple tutorial on how to start a pgrouting docker container, populate it with data, and run a few querries on it

# Quick Start

## 1. Prepare local directory
```bash
mkdir -p ~/dev/pgrouting
mkdir ~/dev/pgrouting/data
mkdir ~/dev/pgrouting/maps
```

put your osm file in ~/pgrouting/maps, we use haifa.osm for example

## 2. Start docker
path must be absolute, so don't use `~/`

    docker run --name pgrouting -d -p 5432:5432 -v /home/$USER/dev/pgrouting/data/:/data -v /home/$USER/dev/pgrouting/maps:/maps pgrouting/pgrouting:v2.6.2-postgresql_11

We mapped local directories data and maps to container's data directory. That's what -v is for.
Basically it shares directories from local computer with docker container. Usefull.

## 3. Now, log into docker container:

    docker exec -it pgrouting /bin/bash

Your are now inside docker, running bash.
This docker container installed `osm2pgrouting` into `/usr/local/` instead of `/usr`, which creates a problem, but we can easilly fix that:

    cd /usr/share
    ln -s /usr/local/share/osm2pgrouting

We just created a link from /usr/share/osm2pgrouting to /usr/local/share/osm2pgrouting.

## 4. Now let's prepare our database.

```bash
# cd without arguments to go to home folder
cd
# starts postgresql command line client
psql -U postgres
```
```sql
-- This is a psql comment, We now create user "user" with password "user"
CREATE ROLE "user" SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN PASSWORD 'user';
-- exit psql
\q
```

### Add the user to .pgpass
Now a good idea to store password for a database this way, but good for tutorial.

    cd
    echo :5432:*:user:user >> .pgpass
    chmod 0600 ~/.pgpass


## 5. Now we going to create the database:

```bash
createdb -U user city_routing
psql -U user -d city_routing
```

```sql
-- add PostGIS functions
CREATE EXTENSION postgis;

-- add pgRouting functions
CREATE EXTENSION pgrouting;

-- Inspect the pgRouting installation
\dx+ pgrouting

-- View pgRouting version
SELECT pgr_version();

-- exit psql
\q
```

We created a new database, called city_routing and activated postgis and pgrouting extensions. Now let's load osm into the database.

## 6. Loading our osm data into our database:
```bash
cd /maps
osm2pgrouting -f haifa.osm -d city_routing -U user -W user
```


## 7. Finally, It's tme to run some queries
```bash
# First, let's verify we have our database tables:
psql -U user -d city_routing -c "\d"
# if everything went well the result should look like:

               List of relations
Schema |           Name           |   Type   | Owner
--------+--------------------------+----------+-------
public | configuration            | table    | user
public | configuration_id_seq     | sequence | user
public | geography_columns        | view     | user
public | geometry_columns         | view     | user
public | pointsofinterest         | table    | user
public | pointsofinterest_pid_seq | sequence | user
public | raster_columns           | view     | user
public | raster_overviews         | view     | user
public | spatial_ref_sys          | table    | user
public | ways                     | table    | user
public | ways_gid_seq             | sequence | user
public | ways_vertices_pgr        | table    | user
public | ways_vertices_pgr_id_seq | sequence | user
(13 rows)
```

Now, let's try and find a node nearest the lat,lon point:

Some notable locations in haifa:
|     Address       |    Lat    |    Lon    |
| ----------------  | --------- | --------  |
| Haifa, Matam      | 32.789795 | 34.959672 |
| Haifa, Ziv        | 32.783076 | 35.014519 |


Ok, time to find nearest node:
```bash
# Start postgresql command line client
psql -U user -d city_routing
```

```sql
-- Find nearest node for Haifa, Matam
select * from ways_vertices_pgr order by the_geom <-> ST_SetSRID(ST_Point(34.959672,32.789795),4326) LIMIT 1;
-- Find nearest node for Haifa, Ziv Center:
select * from ways_vertices_pgr order by the_geom <-> ST_SetSRID(ST_Point(35.014519,32.783076),4326) LIMIT 1;

-- Now that we have the IDs of two nodes we can find a route between them:
select * from pgr_dijkstra('SELECT gid as id, source, target, cost_s as cost, reverse_cost_s as reverse_cost from ways', 3229,372,directed:=true);

-- And if we want to find the list of lat,lon along the route, we can query individual node for it's location, or we can use SQL:

select id,osm_id,lat,lon from ways_vertices_pgr where id in (select node as id from pgr_dijkstra('SELECT gid as id, source, target, cost_s as cost, reverse_cost_s as reverse_cost from ways', 3229,372,directed:=true));

-- some more SQL magic, to get the cost with lat, lon:
select t.id,t.osm_id,t.lat,t.lon,tr.cost,tr.agg_cost from ways_vertices_pgr as t INNER JOIN pgr_dijkstra('SELECT gid as id, source, target, cost_s as cost, reverse_cost_s as reverse_cost from ways', 3229,372,directed:=true) as tr ON t.id = tr.node;

-- Exit from psql
\q
```


## 8. Now, let's do it with Python3

The same is also possible with any other language: C, C++, but for now we will stick with Python3

If you still inside the docker container, type `exit` to go back to our shell on the host computer.
```bash
exit
```

Ok, Let's assume we have Python3 installed.
Let's install virtualenv to manage python environments.
```bash
sudo apt install python3-venv
```

Now, let's prepare our python environment:
```bash
cd /home/$USER/dev/pgrouting
mkdir -p python/env
python3 -mvenv ./python/env
cd python

# This created python environment, every installed dependency will go into our env dir, and won't into system dir
# Now we need to activate the environment
source ./env/bin/activate

#Now, we in our local python environment, and can install python modules, we need to use psycopg2 module to talk with postgresql
pip install psycopg2-binary
```

Ok, now we ready for some python code
Let's create `test.py` file.

```python
import psycopg2 as psql


def main():
    try:
        connect_str = "dbname='city_routing' user='user' password='user' host='localhost'"
        conn = psql.connect(connect_str)
        cursor = conn.cursor()
        cursor.execute('select pgr_version();');
        rows = cursor.fetchall()
        for r in rows:
            print(r[0])

    except Exception as e:
        print("Unable to connect to database...")
        print(e)


if __name__ == "__main__":
    main()
```

This tiny script does very little for now
It tries to connect to postgresql running on localhost
and print pgrouting version to screen.
Now you may be wondering why we connect to localhost when our postgresql is running inside the docker?
If you recall, when we started our pgrouting docker, one of the command line switches we used was: `-p 5432:5432`
it tells docker to forward all connections from local computer's port 5432 to our docker container.
And that is why when we connect to 'localhost:5432' we in fact connect to our postgresql inside docker.


Enough talk, let's move on to something more fun:

Create `route.py` file
```python
import psycopg2 as psql

def nearest_node(cursor,lat,lon):
    try:
        cursor.execute('select id,lat,lon from ways_vertices_pgr order by the_geom <-> ST_SetSRID(ST_Point(%s,%s),4326) LIMIT 1',(lat,lon))
        row = cursor.fetchone()
        if row and len(row) == 3:
            return (int(row[0]),float(row[1]),float(row[2]))
    except Exception as e:
        print("Error:")
        print(e)
    return None


def route(cursor,source,dest):
    try:
        cursor.execute("select t.id,t.osm_id,t.lat,t.lon,tr.cost,tr.agg_cost from ways_vertices_pgr as t INNER JOIN pgr_dijkstra('SELECT gid as id, source, target, cost_s as cost, reverse_cost_s as reverse_cost from ways', %s,%s,directed:=true) as tr ON t.id = tr.node",(source,dest))
        rows = cursor.fetchall()
        for r in rows:
            print(r)
    except Exception as e:
        print("Error:",e)

def main():
    try:
        connect_str = "dbname='city_routing' user='user' password='user' host='localhost'"
        conn = psql.connect(connect_str)
        cursor = conn.cursor()
        cursor.execute('select pgr_version();');
        rows = cursor.fetchall()
        for r in rows:
            print(r[0])
        pntSource = nearest_node(cursor,34.959672, 32.789795) 
        pntDest = nearest_node(cursor,35.014,32.783076)
        print("Source:",pntSource)
        print("Dest:",pntDest)
        route(cursor,pntSource[0],pntDest[0])

    except Exception as e:
        print("Unable to connect to database...")
        print(e)


if __name__ == "__main__":
    main()
```



Now run it:
```bash
python route.py
```

Voila, we have our route, that we obtain from code.
But have we done yet? Not quite.
Let's now create a `Query Server` in `Python3`!!!

## 9. Query Server with Python3

Ok, we not going to create something fancy, but let's create a simple REST service with the following method:

`/api/v1/route?from=lat,lon&to=lat,lon`
So when someone request this URL, it will receive a json list with route coordinates.

Let's install python flask
```bash
pip install flask-restful
```

Now let's see our `server.py`
```python
from flask import Flask
from flask_restful import Resource, Api,reqparse
import psycopg2 as psql
import json

app = Flask(__name__)
api = Api(app)

def nearest_node(cursor,lat,lon):
    try:
        cursor.execute('select id,lat,lon from ways_vertices_pgr order by the_geom <-> ST_SetSRID(ST_Point(%s,%s),4326) LIMIT 1',(lat,lon))
        row = cursor.fetchone()
        if row and len(row) == 3:
            return (int(row[0]),float(row[1]),float(row[2]))
    except Exception as e:
        print("Error:")
        print(e)
    return None


def route(cursor,source,dest):
    result = []
    try:
        cursor.execute("select t.id,t.osm_id,t.lat,t.lon,tr.cost,tr.agg_cost from ways_vertices_pgr as t INNER JOIN pgr_dijkstra('SELECT gid as id, source, target, cost_s as cost, reverse_cost_s as reverse_cost from ways', %s,%s,directed:=true) as tr ON t.id = tr.node",(source,dest))
        rows = cursor.fetchall()
        for r in rows:
            print(r)
            result.append([float(r[2]),float(r[3])])
        print(result)
    except Exception as e:
        print("Error:",e)
    return result

conn = None
def get_db():
    global conn
    if conn is None:
        try:
            connect_str = "dbname='city_routing' user='user' password='user' host='localhost'"
            conn = psql.connect(connect_str)
            return conn

        except Exception as e:
            print("Unable to connect to database...")
            print(e)
            raise e
    return conn



def get_cursor():
    cursor = get_db().cursor()
    return cursor

class Route(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('from', type=str, location='args')
        parser.add_argument('to', type=str, location='args')
        args = parser.parse_args()
        src = [float(x) for x in args['from'].split(',')]
        dst = [float(x) for x in args['to'].split(',')]
        cursor = get_cursor()
        src_node = nearest_node(cursor,src[0],src[1])
        dst_node = nearest_node(cursor,dst[0],dst[1])
        result = route(cursor,src_node[0],dst_node[0])
        return result


api.add_resource(Route, '/api/v1/route')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')

```

Start it with:

    python server.py



Now open new terminal tab and run query using CURL:

    curl "http://localhost:5000/api/v1/route?from=34.959672,32.789795&to=35.014519,32.783076"

It should print the route to screen.


For C++ check out [C++ section](/cpp/README.md):

For C# check out [C# section[(/dotNet/README.md)
