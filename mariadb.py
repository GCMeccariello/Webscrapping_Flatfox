import mariadb
import sys

try:
    conn = mariadb.connect(
        user = "admin",
        password= 'password',
        host = 'localhost',
        port = 3306,
        database = 'testdatabase'
    )


except mariadb.Error as e:
    print(f"there was an error: {e}")

cur = conn.cursor()

cur.execute("CREATE or REPLACE TABLE testtable12345(\
            Strasse VARCHAR(255),\
            Postleitzahl Int(4),\
            Ort VARCHAR(25),\
            Anzahl_Zimmer FLOAT,\
            Flaeche Int(10),\
            Preis Int(10)\
            );")

cur.execute("LOAD DATA LOCAL INFILE 'flatfox_stage.csv' INTO TABLE testtable12345 \
            FIELDS TERMINATED BY ',' (\
            Strasse, Postleitzahl, Ort, Anzahl_Zimmer, Flaeche, Preis \
            )")

conn.commit()