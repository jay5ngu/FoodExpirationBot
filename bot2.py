import os
import psycopg2

conn = psycopg2.connect(os.environ["DATABASE_URL"])

with conn.cursor() as cur:
    # cur.execute("SELECT now()")
    cur.execute("SELECT * from foodExpirationDate")
    res = cur.fetchall()

    cur.execute("INSERT INTO foodExpirationDate (username, item, expirationDate) VALUES ('test1', 'testing', '2024-08-27')")

    conn.commit()
    print(res)