import sqlite3
conn = sqlite3.connect('stackdose.db')
cursor = conn.cursor()
schema = open("schema.sql", "r", encoding="utf-8").read()

cursor.executescript(schema)

conn.close()