import psycopg2 as psql


def main():
    try:
        connect_str = "dbname='routing_db' user='user' password='user' host='localhost'"
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
