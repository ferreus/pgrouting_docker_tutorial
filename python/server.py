from flask import Flask
from flask_restful import Resource, Api,reqparse
import psycopg2 as psql
import json
from gevent.pywsgi import WSGIServer

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
            connect_str = "dbname='routing_db' user='user' password='user' host='localhost'"
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
    #app.run(debug=True,host='0.0.0.0')
    http_server = WSGIServer(('',5000),app)
    http_server.serve_forever()
