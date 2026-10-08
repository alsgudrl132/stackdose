from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

# CORS: 프론트(5173 포트)에서 이 서버(8000 포트)를 부를 수 있게 허락
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

# 조회용 공통 함수: SQL을 실행하고 결과 줄 목록(리스트)을 돌려줌. 없으면 빈 리스트 []
# params: SQL의 ? 자리에 들어갈 값 (튜플. 값 하나면 (값,) 처럼 쉼표 필수)
def fetch_all(sql, params=()):
    try:
        conn = sqlite3.connect('stackdose.db')
        conn.row_factory = sqlite3.Row   # 결과를 컬럼 이름으로 꺼낼 수 있게 (row["no"])
        cur = conn.cursor()
        res = cur.execute(sql, params).fetchall()
        return res
    finally:
        # 성공하든 에러가 나든 마지막에 연결을 닫음
        cur.close()
        conn.close()

@app.get("/")
def root():
    return {"message" : "Hello World"}

# 칸 8개 전체 (남은 양 화면)
@app.get("/slots")
def get_slots():
    return fetch_all("SELECT * FROM slots")


# 프리셋 목록 + 각 프리셋의 항목
# JOIN 결과는 평평한 줄(프리셋 이름이 줄마다 반복)이라, 프리셋 번호별로 묶어서 돌려줌
# 결과 모양: [{"no":1, "name":"아침", "items":[{"slot":1,"amount":5}, ...]}]
@app.get("/presets")
def get_presets():
    res = fetch_all("""
        SELECT A.no, A.name, B.slot, B.amount
        FROM presets AS A
        JOIN preset_items AS B ON A.no = B.preset
    """)
    presets = {}   # 프리셋 번호 → 프리셋 상자
    for row in res:
        no = row["no"]
        if no not in presets:   # 처음 보는 프리셋이면 빈 items 로 상자를 만듦
            presets[no] = {
                "no": no,
                "name": row["name"],
                "items": [],
            }
        presets[no]["items"].append({   # 모든 줄에서 실행: 그 프리셋 상자에 항목 추가
            "slot": row["slot"],
            "amount": row["amount"],
        })
    return list(presets.values())

# 담기 요청: 화면의 "담기" 버튼이 부름
# 없는 프리셋이면 404, 있으면 dispenses 에 requested 상태로 한 줄 저장하고 요청 번호(id)를 돌려줌
@app.post("/presets/{no}/dispense")
def dispense_preset(no:int):   # no:int → 주소의 글자 "1"을 숫자 1로 바꿈. 숫자가 아니면 FastAPI가 422
    try:
        conn = sqlite3.connect('stackdose.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        res = cur.execute('''SELECT no FROM presets WHERE no = (?)''',(no,)).fetchall()
        if not res:   # 빈 리스트 = 그런 프리셋 없음
            raise HTTPException(status_code=404, detail=f"Preset {no} not found")
        cur.execute('''INSERT INTO dispenses (preset, status) VALUES(?, ?)''', (no, "requested"))
        conn.commit()   # 저장(INSERT/UPDATE)은 commit 해야 파일에 실제로 기록됨
        return {"ok" : True, "id": cur.lastrowid, "preset" : no}   # lastrowid = 방금 넣은 줄의 id
    finally:
        cur.close()
        conn.close()

# 담기 요청 한 건 조회 (상태 확인용). 없는 번호면 404
@app.get("/dispenses/{id}")
def dispense_status(id:int):
    res = fetch_all("SELECT * FROM dispenses WHERE id = (?)", (id,))
    if res == []:
        raise HTTPException(404, detail=f"Id {id} not found")
    return res[0]   # 리스트가 아니라 객체 하나로

# 기계(가상 디스펜서 / 나중에 ESP32)가 "다음에 할 일"을 가져감
# requested 상태 중 가장 오래된 것(id 가장 작은 것) 하나. 일감이 없으면 null (에러 아님, 평범한 상황)
@app.get("/device/next")
def get_next_job():
    res = fetch_all("SELECT * FROM dispenses WHERE status = 'requested' ORDER BY id LIMIT 1")
    if res == []:
        return None
    return res[0]

# 기계가 일감을 "내가 할게"라고 가져감: requested → running
# 404 = 없는 요청, 409(Conflict) = 지금 상태에서는 시작할 수 없음 (이미 running 이거나 done)
@app.post("/dispenses/{id}/start")
def dispense_start(id:int):
    res = fetch_all("SELECT status FROM dispenses WHERE id = (?)", (id,))
    if res == []:
        raise HTTPException(404, detail=f"Id {id} not found")
    if res[0]["status"] != "requested":   # 이미 다른 기계가 가져갔거나 끝난 요청
        raise HTTPException(409, detail="Status is not requested")
    try:
        conn = sqlite3.connect('stackdose.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        # 조건에 status = 'requested' 를 같이 넣어서, 검사와 변경을 한 문장에서 함
        cur.execute("UPDATE dispenses SET status = 'running' WHERE id = (?) AND status = 'requested'", (id,))
        # rowcount = 실제로 바뀐 줄 수. 0이면 위 SELECT 와 이 UPDATE 사이에 다른 기계가 먼저 가져간 것
        # → 같은 일을 두 번 하지 않게 409 (두 번 눌림 방지)
        if cur.rowcount == 0:
            raise HTTPException(409, detail="Now running")
        conn.commit()
        return {"ok" : True, "id" : id, "status" : "running"}
    finally:
        cur.close()
        conn.close()

# 기계가 일감을 다 했다고 보고: running → done
# 상태 흐름: requested(요청됨) → running(진행 중, start) → done(완료, finish)
# 404 = 없는 요청, 409 = running 이 아님 (아직 시작 안 했거나 이미 끝남)
@app.post("/dispenses/{id}/finish")
def dispense_finish(id:int):
    res = fetch_all("SELECT status FROM dispenses WHERE id = (?)", (id,))
    if res == []:
        raise HTTPException(404, detail=f"Id {id} not found")
    if res[0]["status"] != "running":   # 진행 중인 요청만 끝낼 수 있음
        raise HTTPException(409, detail="Status is not requested")
    try:
        conn = sqlite3.connect('stackdose.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        # 조건에 status = 'running' 을 같이 넣어서, 검사와 변경을 한 문장에서 함
        cur.execute("UPDATE dispenses SET status = 'done' WHERE id = (?) AND status = 'running'", (id,))
        # rowcount = 실제로 바뀐 줄 수. 0이면 위 SELECT 와 이 UPDATE 사이에 이미 누가 끝낸 것
        # → 완료 보고가 두 번 처리되지 않게 409
        if cur.rowcount == 0:
            raise HTTPException(409, detail="Now finish")
        conn.commit()
        return {"ok" : True, "id" : id, "status" : "done"}
    finally:
        cur.close()
        conn.close()

