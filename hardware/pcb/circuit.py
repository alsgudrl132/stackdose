# 제어 기판 회로: 부품마다 "핀 번호 → 넷(전선 이름)"
# hardware/wiring.md 를 PCB 로 옮긴 것. 회로를 바꾸면 여기만 고치고 gen_pcb.py 를 다시 돌림
#
# 모듈(ESP32, DRV8833)은 납땜하지 않고 핀소켓에 꽂음 → 이미 산 부품을 그대로 씀
# MCP23017 · HX711 · 홀 센서 · ULN2003 은 기계의 다른 판에 있어서, 여기서는 선을 꽂는 핀헤더만 둠

# ---- ESP32-DevKitC (38핀 클론). 위에서 봤을 때, 안테나 쪽이 1번 핀 ----
# 핀 이름은 보드 실물 사진(2026-10-13)의 인쇄와 같음. 두 줄 간격 25.4 ★ (보드 폭 27.9 실측, 줄 간격은 미실측)
ESP_TOP = ["GND", "IO23", "IO22", "TX", "RX", "IO21", "GND", "IO19", "IO18", "IO5",
           "IO17", "IO16", "IO4", "IO0", "IO2", "IO15", "D1", "D0", "CLK"]
ESP_BOTTOM = ["3V3", "EN", "IO36", "IO39", "IO34", "IO35", "IO32", "IO33", "IO25", "IO26",
              "IO27", "IO14", "IO12", "GND", "IO13", "D2", "D3", "CMD", "5V"]

# ESP32 핀 → 넷 (wiring.md 의 핀 배정. 안 쓰는 핀은 연결 없음)
ESP_NET = {
    "GND": "GND", "3V3": "+3V3", "5V": "ESP_5V",
    "IO21": "SDA", "IO22": "SCL",
    "IO18": "HX_DT", "IO33": "HX_SCK",
    "IO25": "M1_IN1", "IO26": "M1_IN2", "IO27": "M2_IN1", "IO13": "M2_IN2",
    "IO32": "M3_IN1", "IO23": "M3_IN2", "IO4": "M4_IN1", "IO19": "M4_IN2",
    "IO36": "HALL1", "IO39": "HALL2", "IO34": "HALL3", "IO35": "HALL4",
}

# ---- DRV8833 모듈 (디바이스마트 VLT-MD012). 상품 사진의 인쇄 그대로, 위 → 아래 ----
# ⚠ 이 모듈은 nFAULT 가 밖으로 안 나옴 (wiring.md 의 ULT/GPIO5 는 쓸 수 없음). 잠자기 해제 핀 이름은 STBY
# 두 줄 간격 17.78 ★ (사진으로 어림. 실물이 오면 캘리퍼로 재기)
DRV_LEFT = ["NC", "AIN2", "AIN1", "STBY", "BIN1", "BIN2", "NC", "GND"]
DRV_RIGHT = ["VM", "NC", "GND", "AO1", "AO2", "BO2", "BO1", "GND"]


def drv_nets(a, b):
    """a, b = 이 드라이버가 맡는 가루 모터 번호 (A 채널, B 채널)"""
    left = {"AIN1": f"M{a}_IN1", "AIN2": f"M{a}_IN2", "BIN1": f"M{b}_IN1", "BIN2": f"M{b}_IN2",
            "STBY": "+3V3", "GND": "GND"}
    right = {"VM": "+5V", "GND": "GND", "AO1": f"M{a}_OUT1", "AO2": f"M{a}_OUT2",
             "BO1": f"M{b}_OUT1", "BO2": f"M{b}_OUT2"}
    return ([left.get(p) for p in DRV_LEFT], [right.get(p) for p in DRV_RIGHT])


# 바깥으로 나가는 핀헤더: (기판 글자, 핀마다 넷)
HEADERS = {
    "J_I2C": ("MCP23017", ["+3V3", "GND", "SDA", "SCL", "+5V"]),   # 5V 는 ULN2003 ×4 전원도 같이
    "J_HX": ("HX711", ["+3V3", "GND", "HX_DT", "HX_SCK"]),
    "J_H1": ("HALL5", ["+3V3", "GND", "HALL1"]),                    # 기판 글자는 칸 번호 (5~8번 칸)
    "J_H2": ("HALL6", ["+3V3", "GND", "HALL2"]),
    "J_H3": ("HALL7", ["+3V3", "GND", "HALL3"]),
    "J_H4": ("HALL8", ["+3V3", "GND", "HALL4"]),
    # USB 로 굽는 동안에는 뽑아 둠 (어댑터 5V 와 USB 5V 가 부딪히지 않게). wiring.md 의 ⚠ 를 점퍼로 바꾼 것
    "JP1": ("5V-ESP", ["+5V", "ESP_5V"]),
}

# 나사 터미널 5.08mm 2핀 (2EDGK): (기판 글자, [1번, 2번])
TERMINALS = {
    "J_PWR": ("5V IN", ["+5V", "GND"]),
    "J_M1": ("M1", ["M1_OUT1", "M1_OUT2"]),
    "J_M2": ("M2", ["M2_OUT1", "M2_OUT2"]),
    "J_M3": ("M3", ["M3_OUT1", "M3_OUT2"]),
    "J_M4": ("M4", ["M4_OUT1", "M4_OUT2"]),
}

# 코드 안의 이름 → KiCad 부품 번호 (KiCad 규칙: 글자 + 숫자로 끝나야 함). 기능 이름은 값(Value)과 기판 글자로 보임
REF = {
    "J_ESP1": "J1", "J_ESP2": "J2",
    "U1L": "J3", "U1R": "J4", "U2L": "J5", "U2R": "J6",   # DRV8833 모듈을 꽂는 소켓
    "J_I2C": "J7", "J_HX": "J8", "J_H1": "J9", "J_H2": "J10", "J_H3": "J11", "J_H4": "J12",
    "J_PWR": "J13", "J_M1": "J14", "J_M2": "J15", "J_M3": "J16", "J_M4": "J17",
}

# 커패시터 1000uF 10V (1번 = +), 저항
CAPS = {"C1": ["+5V", "GND"], "C2": ["+5V", "GND"], "C3": ["+5V", "GND"]}   # DRV1, DRV2 옆, 전원 입력 옆
RESISTORS = {"R1": ("4.7k", ["SDA", "+3V3"]), "R2": ("4.7k", ["SCL", "+3V3"])}   # I2C 풀업
