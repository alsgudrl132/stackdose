from fastapi import FastAPI, HTTPException
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

def fetch_all(sql, params=()):
    try:
        conn = sqlite3.connect('stackdose.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        res = cur.execute(sql, params).fetchall()
        return res
    finally:
        cur.close()
        conn.close()

@app.get("/")
def root():
    return {"message" : "Hello World"}

@app.get("/slots")
def get_slots():
    return fetch_all("SELECT * FROM slots")
    

@app.get("/presets")
def get_presets():
    res = fetch_all("""
        SELECT A.no, A.name, B.slot, B.amount
        FROM presets AS A
        JOIN preset_items AS B ON A.no = B.preset
    """)
    presets = {}
    for row in res:
        no = row["no"]
        if no not in presets:
            presets[no] = {
                "no": no,
                "name": row["name"],
                "items": [],
            }
        presets[no]["items"].append({
            "slot": row["slot"],
            "amount": row["amount"],
        })
    return list(presets.values())

@app.post("/presets/{no}/dispense")
def dispense_preset(no:int):
    try:
        conn = sqlite3.connect('stackdose.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        res = cur.execute('''SELECT no FROM presets WHERE no = (?)''',(no,)).fetchall()
        if not res:
            raise HTTPException(status_code=404, detail=f"Preset {no} not found")
        cur.execute('''INSERT INTO dispenses (preset, status) VALUES(?, ?)''', (no, "requested"))
        conn.commit()
        return {"ok" : True, "id": cur.lastrowid, "preset" : no}
    finally:
        cur.close()
        conn.close()

@app.get("/dispenses/{id}")
def dispense_status(id:int):
    res = fetch_all("SELECT * FROM dispenses WHERE id = (?)", (id,))
    if res == []:
        raise HTTPException(404, detail=f"Id {id} not found")
    return res[0]

@app.get("/device/next")
def get_next_job():
    res = fetch_all("SELECT * FROM dispenses WHERE status = 'requested' ORDER BY id LIMIT 1")
    if res == []:
        return None
    return res[0]

@app.post("/dispenses/{id}/start")
def dispense_start(id:int):
    res = fetch_all("SELECT status FROM dispenses WHERE id = (?)", (id,))
    if res == []:
        raise HTTPException(404, detail=f"Id {id} not found")
    if res[0]["status"] != "requested":
        raise HTTPException(409, detail="Status is not requested")
    try:
        conn = sqlite3.connect('stackdose.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("UPDATE dispenses SET status = 'running' WHERE id = (?) AND status = 'requested'", (id,))
        if cur.rowcount == 0:
            raise HTTPException(409, detail="Now running")
        conn.commit()
    finally:
        cur.close()
        conn.close()