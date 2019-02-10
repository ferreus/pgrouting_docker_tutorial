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
        connect_str = "dbname='routing_db' user='user' password='user' host='localhost'"
        conn = psql.connect(connect_str)
        cursor = conn.cursor()
        cursor.execute('select pgr_version();');
        rows = cursor.fetchall()
        for r in rows:
            print(r[0])

        pntSource = nearest_node(cursor,34.959672,32.789795)
        pntDest = nearest_node(cursor,35.014,32.783076)
        print("Source:",pntSource)
        print("Dest:",pntDest)
        route(cursor,pntSource[0],pntDest[0])

    except Exception as e:
        print("Unable to connect to database...")
        print(e)


if __name__ == "__main__":
    main()
