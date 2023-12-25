import psycopg2 as psql

def main():
    conn = psql.connect(
        host="localhost",
        database="store",
        user="ilyas",
        password="password"
    )
    cursor = conn.cursor()
    cursor.execute(open("schema.sql", "r").read())
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
