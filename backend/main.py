from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message" : "Hello World"}

@app.get("/slots")
def get_slots():
    try:
        conn = sqlite3.connect('stackdose.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        res = cur.execute("SELECT * FROM slots").fetchall()
        return res
    finally:
        cur.close()
        conn.close()