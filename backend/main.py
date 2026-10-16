from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import time

app = FastAPI()

SLOT_COUNT = 8               # 칸 수 (1~4 가루, 5~8 알약). 기계 모양이 정함
DEVICE_TIMEOUT_SEC = 10      # 기계는 2초마다 /device/next 를 부름. 이만큼 조용하면 끊긴 걸로 봄

# 기계가 마지막으로 /device/next 를 부른 시각 (서버 메모리에만 있음. 서버를 다시 켜면 None)
last_seen = None

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

# 저장용 공통 함수: 여러 SQL 을 한 연결에서 실행하고 한 번에 commit
# statements: [(sql, params), ...]. 중간에 에러가 나면 commit 하지 않아서 반쯤 저장되는 일이 없음
# 돌려주는 값: 마지막 문장의 lastrowid (INSERT 로 새로 생긴 번호)
def execute_all(statements):
    conn = sqlite3.connect('stackdose.db')
    try:
        cur = conn.cursor()
        for sql, params in statements:
            cur.execute(sql, params)
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

@app.get("/")
def root():
    return {"message" : "Hello World"}

# 칸 8개 전체 (남은 양 화면)
@app.get("/slots")
def get_slots():
    return fetch_all("SELECT * FROM slots")

# 칸 고치기 (화면의 "남은 양" 줄을 눌러서 이름 · 남은 양을 바꿈)
# supplement 가 비어 있으면 빈 칸으로 만듦 (남은 양 0)
class SlotIn(BaseModel):
    supplement: str | None = None
    remaining: int = 0

@app.put("/slots/{no}")
def update_slot(no:int, body:SlotIn):
    if not 1 <= no <= SLOT_COUNT:
        raise HTTPException(404, detail=f"Slot {no} not found")
    name = (body.supplement or "").strip() or None
    remaining = max(0, body.remaining) if name else 0
    execute_all([("UPDATE slots SET supplement = ?, remaining = ? WHERE no = ?", (name, remaining, no))])
    return {"ok": True, "no": no}


# 프리셋 목록 + 각 프리셋의 항목
# JOIN 결과는 평평한 줄(프리셋 이름이 줄마다 반복)이라, 프리셋 번호별로 묶어서 돌려줌
# LEFT JOIN: 항목이 하나도 없는 프리셋도 목록에 나오게 (그때 slot · amount 는 None)
# 결과 모양: [{"no":1, "name":"아침", "items":[{"slot":1,"amount":5}, ...]}]
@app.get("/presets")
def get_presets():
    res = fetch_all("""
        SELECT A.no, A.name, B.slot, B.amount
        FROM presets AS A
        LEFT JOIN preset_items AS B ON A.no = B.preset
        ORDER BY A.no, B.slot
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
        if row["slot"] is not None:   # 항목이 없는 프리셋의 줄은 건너뜀
            presets[no]["items"].append({
                "slot": row["slot"],
                "amount": row["amount"],
            })
    return list(presets.values())

# 프리셋 추가 · 수정에 쓰는 요청 모양 (FastAPI 가 JSON 을 이 모양으로 검사해 줌)
class PresetItemIn(BaseModel):
    slot: int
    amount: int   # 정수만 (기계가 atoi 로 읽음). 가루 g, 알약 개수

class PresetIn(BaseModel):
    name: str
    items: list[PresetItemIn]

# 저장 전에 내용 검사. 문제가 있으면 400 + 이유
def check_preset(body:PresetIn):
    if not body.name.strip():
        raise HTTPException(400, detail="이름을 적어 주세요")
    if not body.items:
        raise HTTPException(400, detail="담을 것을 하나 이상 넣어 주세요")
    slots_seen = set()
    for item in body.items:
        if not 1 <= item.slot <= SLOT_COUNT:
            raise HTTPException(400, detail=f"{item.slot}번 칸은 없어요")
        if item.slot in slots_seen:   # 같은 칸이 두 번이면 기계용 amounts[8] 에서 하나가 덮어써짐
            raise HTTPException(400, detail=f"{item.slot}번 칸이 두 번 들어갔어요")
        if item.amount <= 0:
            raise HTTPException(400, detail="양은 1 이상이어야 해요")
        slots_seen.add(item.slot)

def item_statements(no, items):
    return [("INSERT INTO preset_items (preset, slot, amount) VALUES (?, ?, ?)", (no, i.slot, i.amount)) for i in items]

@app.post("/presets")
def create_preset(body:PresetIn):
    check_preset(body)
    no = execute_all([("INSERT INTO presets (name) VALUES (?)", (body.name.strip(),))])
    execute_all(item_statements(no, body.items))
    return {"ok": True, "no": no}

# 수정: 이름을 바꾸고, 항목은 지웠다가 새로 넣음 (항목이 몇 개 바뀌었는지 따질 필요가 없음)
@app.put("/presets/{no}")
def update_preset(no:int, body:PresetIn):
    check_preset(body)
    if fetch_all("SELECT no FROM presets WHERE no = (?)", (no,)) == []:
        raise HTTPException(404, detail=f"Preset {no} not found")
    execute_all([
        ("UPDATE presets SET name = ? WHERE no = ?", (body.name.strip(), no)),
        ("DELETE FROM preset_items WHERE preset = ?", (no,)),
        *item_statements(no, body.items),
    ])
    return {"ok": True, "no": no}

# 삭제: 항목 먼저 지우고 프리셋을 지움 (SQLite 는 기본으로 ON DELETE CASCADE 가 꺼져 있음)
# 지난 담기 기록(dispenses)은 남겨 둠
@app.delete("/presets/{no}")
def delete_preset(no:int):
    if fetch_all("SELECT no FROM presets WHERE no = (?)", (no,)) == []:
        raise HTTPException(404, detail=f"Preset {no} not found")
    execute_all([
        ("DELETE FROM preset_items WHERE preset = ?", (no,)),
        ("DELETE FROM presets WHERE no = ?", (no,)),
    ])
    return {"ok": True, "no": no}

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

# 화면의 "지금 담는 중" 패널용: 가장 최근 담기 요청 하나 + 칸별 진행
# 요청이 하나도 없으면 null
# 주의: 이 경로는 /dispenses/{id} 보다 위에 있어야 함. 아래에 두면 "current" 를 id 로 읽으려다 422
# steps 의 actual 은 아직 기계가 칸별로 보고하지 않아서, 끝났으면 목표량 · 아니면 0 으로 채움
#   (나중에 기계가 저울 값을 보고하면 여기를 실제 값으로 바꿈)
STEP_STATUS = {"requested": "waiting", "running": "running", "done": "done", "canceled": "canceled"}

@app.get("/dispenses/current")
def current_dispense():
    res = fetch_all("""
        SELECT D.id, D.preset, D.status, D.created_at, P.name
        FROM dispenses AS D
        LEFT JOIN presets AS P ON D.preset = P.no
        ORDER BY D.id DESC LIMIT 1
    """)
    if res == []:
        return None
    job = dict(res[0])
    items = fetch_all("SELECT slot, amount FROM preset_items WHERE preset = (?) ORDER BY slot", (job["preset"],))
    step_status = STEP_STATUS.get(job["status"], job["status"])
    job["steps"] = [{
        "slot": item["slot"],
        "target": item["amount"],
        "actual": item["amount"] if job["status"] == "done" else 0,
        "status": step_status,
    } for item in items]
    return job

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
    global last_seen
    last_seen = time.time()   # 기계가 살아 있다는 신호 (화면의 "신호 n초 전")
    preset = fetch_all("SELECT * FROM dispenses WHERE status = 'requested' ORDER BY id LIMIT 1")
    if preset == []:
        return None
    res = fetch_all("SELECT * FROM preset_items WHERE preset = (?)", (preset[0]["preset"],))

    amounts = [0] * 8
    for item in res:
        amounts[item["slot"]-1] = item["amount"]
    job = dict(preset[0])
    job["amounts"] = amounts
    return job

# 화면 위쪽 기계 상태: 켜져 있나, 담는 중인가, 마지막 신호가 몇 초 전인가
# 기계는 일하는 중(start ~ finish)에는 /device/next 를 안 부르지만, 그 사이는 몇 초라 끊김으로 보지 않음
@app.get("/device")
def get_device():
    if last_seen is None:   # 서버를 켠 뒤로 기계가 한 번도 안 부름
        return {"online": False, "state": "offline", "seen_sec": None}
    ago = int(time.time() - last_seen)
    online = ago < DEVICE_TIMEOUT_SEC
    # 가장 최근 요청이 running 일 때만 "담는 중" (예전에 finish 를 못 받고 멈춘 running 은 무시)
    latest = fetch_all("SELECT status FROM dispenses ORDER BY id DESC LIMIT 1")
    if not online:
        state = "offline"
    elif latest and latest[0]["status"] == "running":
        state = "dispensing"
    else:
        state = "idle"
    return {"online": online, "state": state, "seen_sec": ago}

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
        raise HTTPException(409, detail="Status is not running")
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
        # 남은 양 줄이기: 프리셋의 목표량만큼 (0 밑으로는 안 내려감)
        # 나중에 기계가 저울로 잰 실제 양을 보고하면 그 값으로 바꿈
        cur.execute("""
            UPDATE slots SET remaining = MAX(0, remaining - (
                SELECT I.amount FROM preset_items AS I
                JOIN dispenses AS D ON D.preset = I.preset
                WHERE D.id = ? AND I.slot = slots.no
            ))
            WHERE no IN (
                SELECT I.slot FROM preset_items AS I
                JOIN dispenses AS D ON D.preset = I.preset
                WHERE D.id = ?
            )
        """, (id, id))
        conn.commit()
        return {"ok" : True, "id" : id, "status" : "done"}
    finally:
        cur.close()
        conn.close()

# 화면의 "멈추기": 아직 기계가 가져가지 않은 요청만 취소할 수 있음 (requested → canceled)
# 기계가 이미 담는 중(running)이면 409. 펌웨어가 중간에 멈추라는 신호를 아직 안 봄
@app.post("/dispenses/{id}/cancel")
def dispense_cancel(id:int):
    res = fetch_all("SELECT status FROM dispenses WHERE id = (?)", (id,))
    if res == []:
        raise HTTPException(404, detail=f"Id {id} not found")
    conn = sqlite3.connect('stackdose.db')
    try:
        cur = conn.cursor()
        # start 와 같은 방식: 조건에 status 를 넣어서, 기계가 막 가져간 요청을 취소하지 않게 함
        cur.execute("UPDATE dispenses SET status = 'canceled' WHERE id = (?) AND status = 'requested'", (id,))
        if cur.rowcount == 0:
            raise HTTPException(409, detail="기계가 이미 담기 시작했거나 끝난 요청이에요")
        conn.commit()
        return {"ok": True, "id": id, "status": "canceled"}
    finally:
        conn.close()

