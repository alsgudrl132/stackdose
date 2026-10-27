# 만능기판(브레드보드형 Half, 89x52) 납땜 배치: 구멍마다 무엇을 꽂는지 + 검사 + 그림
# 회로는 circuit.py 와 같아야 함 (검사가 비교함). 배치를 바꾸면 여기만 고치고 다시 돌림
#
# 실행: python hardware/pcb/perfboard.py
# 결과: perfboard_top.png (위에서 본 배치도), perfboard_3d.png (3D), perfboard_connect.png (연결도)
#
# 기판 구조 (상품 사진 2026-10-16 확인, ElectroCookie 계열):
#   - 세로 30칸(1~30). 칸마다 위 묶음 J~F 5구멍, 아래 묶음 E~A 5구멍이 각각 이어져 있음 (위·아래 묶음끼리는 안 이어짐)
#   - 전원줄 4개: 위 바깥(-), 위 안쪽(+), 아래 안쪽(-), 아래 바깥(+). 줄마다 30구멍이 가로로 이어짐
#   - 바깥 전원줄 2개는 제어판 받침 홈의 턱(가장자리 2.3mm) 밑이라 안 씀
#   - 위 안쪽(+) 줄 = 3V3, 아래 안쪽(-) 줄 = GND 로 씀. 5V 는 전류가 커서 칸과 선으로 따로 돌림
# 구멍 위치는 사진에서 잰 값이라 ±0.5mm ★
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import circuit as C  # noqa: E402

PB_W, PB_D = 89.0, 52.0
P = 2.54
LIP = 2.3                       # 받침 홈 턱이 덮는 가장자리 폭 (electronics.scad groove_d 2 + clear 0.3)
COL_X0 = 6.8                    # 1번 칸 x ★
ROW_Y = {"T-": 2.5, "T+": 5.1,
         "J": 11.8, "I": 11.8 + P, "H": 11.8 + 2 * P, "G": 11.8 + 3 * P, "F": 11.8 + 4 * P,
         "E": 11.8 + 7 * P, "D": 11.8 + 8 * P, "C": 11.8 + 9 * P, "B": 11.8 + 10 * P, "A": 11.8 + 11 * P,
         "B-": 11.8 + 11 * P + 6.7, "B+": 11.8 + 11 * P + 9.3}
TOP_ROWS, BOT_ROWS = "JIHGF", "EDCBA"
RAIL_USE = {"T+": "+3V3", "B-": "GND"}     # 쓰는 전원줄과 그 넷
DRV_COLS = {"U1": 1, "U2": 10}            # 모듈 소켓 첫 칸 (8칸씩)
DRV_TOP, DRV_BOT = "H", "D"               # 소켓 두 줄 (줄 간격 6칸 = 15.24, 2026-10-21 만능기판에 올려 확인)
DRV_W, DRV_L = 18.4, 21.3                 # 모듈 기판: 핀 줄 사이 방향 폭 · 핀 줄 길이 (둘 다 실측 2026-10-21)


def xy(h):
    row, col = h
    return COL_X0 + (col - 1) * P, ROW_Y[row]


def hole(s):
    """'I6' → ('I', 6), 'T+5' → ('T+', 5)"""
    for r in ("T+", "T-", "B+", "B-"):
        if s.startswith(r):
            return (r, int(s[len(r):]))
    return (s[0], int(s[1:]))


# ---------------- 배치 ----------------
# 핀 하나 = (구멍, 넷, 그림 글자, 종류)
pins = []        # 소켓·핀헤더·부품 다리 (구멍 하나에 하나)
wires = []       # 기판 위 납땜 선: (구멍1, 구멍2, 넷)
external = []    # 밖에서 들어오는 선 (모터·센서·전원): (구멍, 넷, 글자)
bodies = []      # 키가 있는 부품 (겹침 검사): (이름, 종류, 모양)


def pin(h, net, label, kind):
    pins.append((hole(h), net, label, kind))


# DRV8833 모듈: 시계 방향 90° 돌려 꽂음 → 모듈 왼쪽 줄(신호)이 위(H), 오른쪽 줄(전원·모터)이 아래(C),
# 모듈 1번 핀(맨 위)이 오른쪽 끝 칸. 그래서 칸 순서가 모듈 인쇄의 거꾸로
drv_motor = {"U1": (1, 2), "U2": (3, 4)}
for ref, c0 in DRV_COLS.items():
    a, b = drv_motor[ref]
    left, right = C.drv_nets(a, b)
    for i in range(8):
        col = c0 + 7 - i
        pin(f"{DRV_TOP}{col}", left[i], C.DRV_LEFT[i], "socket")
        pin(f"{DRV_BOT}{col}", right[i], C.DRV_RIGHT[i], "socket")
    x0, x1 = xy(("A", c0))[0] - 1.27, xy(("A", c0 + 7))[0] + 1.27
    mx, my = (DRV_L - 7 * P) / 2, (DRV_W - (ROW_Y[DRV_BOT] - ROW_Y[DRV_TOP])) / 2   # 모듈이 핀보다 튀어나온 길이
    mx0, mx1 = xy(("A", c0))[0] - mx, xy(("A", c0 + 7))[0] + mx
    bodies.append((f"DRV8833 {ref}", "module", ("rect", mx0, ROW_Y[DRV_TOP] - my, mx1, ROW_Y[DRV_BOT] + my, 8.5, 10.1)))
    for r in (DRV_TOP, DRV_BOT):
        bodies.append((f"소켓 {ref}{r}", "socket", ("rect", x0, ROW_Y[r] - 1.27, x1, ROW_Y[r] + 1.27, 0, 8.5)))

# ESP32 로 가는 수 핀헤더 (F-F 점퍼 30cm). 글자 = ESP32 핀 이름
ESP_PIN_AT = {
    "IO27": "J4", "IO13": "J3", "IO25": "J6", "IO26": "J7",      # DRV U1 신호 칸 (가루 2, 가루 1)
    "IO4": "J13", "IO19": "J12", "IO32": "J15", "IO23": "J16",   # DRV U2 신호 칸 (가루 4, 가루 3)
    "IO21": "F20", "IO22": "F21", "IO18": "F23", "IO33": "F24",
    "IO36": "F25", "IO39": "F26", "IO34": "F27", "IO35": "F28",
    "3V3": "T+18", "GND": "B-24", "5V": "C21",
}
for name, h in ESP_PIN_AT.items():
    net = C.ESP_NET[name]
    pin(h, "+5V" if net == "ESP_5V" else net, "ESP " + name, "esp")   # 5V 점퍼 = JP1 (USB 로 구울 때 뽑음)

# MCP23017 로 가는 수 핀헤더 (F-F 점퍼 30cm 2개 이음)
for net, h in zip(C.HEADERS["J_I2C"][1], ["T+19", "B-25", "G20", "G21", "D21"]):
    pin(h, net, "MCP " + {"+3V3": "3V3", "+5V": "5V"}.get(net, net), "mcp")

# 커패시터 1000uF: + 다리는 5V 칸 A줄, - 다리는 바로 밑 GND 줄. 몸통은 두 다리 사이에 세움
for name, plus, minus in [("C1", "A8", "B-8"), ("C2", "A17", "B-17"), ("C3", "A21", "B-21")]:
    pin(plus, "+5V", name + " +", "cap")
    pin(minus, "GND", name + " -", "cap")
    (px, py), (_, my) = xy(hole(plus)), xy(hole(minus))
    bodies.append((name, "cap", ("circle", px, (py + my) / 2, 5.0, 0, 13)))

# 풀업 저항 4.7k: 칸 I줄 ↔ 3V3 줄, 눕혀서 (몸통이 J줄 위를 지나감)
for name, a, b, net in [("R1", "I20", "T+20", "SDA"), ("R2", "I21", "T+21", "SCL")]:
    pin(a, net, name, "res")
    pin(b, "+3V3", name, "res")
    (ax, ay), (_, by) = xy(hole(a)), xy(hole(b))
    bodies.append((name, "res", ("rect", ax - 1.2, (ay + by) / 2 - 3.2, ax + 1.2, (ay + by) / 2 + 3.2, 0, 2.5)))

# 기판 위 납땜 선 (단선 0.6, 짧게 잘라 씀)
wires += [
    ("J5", "T+5", "+3V3"), ("J14", "T+14", "+3V3"),                 # STBY → 3V3 (안 이으면 모터 안 돎)
    ("A1", "B-1", "GND"), ("A6", "B-6", "GND"), ("A10", "B-10", "GND"), ("A15", "B-15", "GND"),
    ("B17", "B21", "+5V"),                                          # U2 VM → 5V 칸(21)
    ("E17", "E8", "+5V"),                                           # U2 VM → U1 VM (모듈 밑으로 지나감)
    ("G1", "E1", "GND"), ("G10", "E10", "GND"),                     # 모듈 위쪽 GND 핀도 GND 로 (모듈 밑)
    ("G29", "G30", "GND"), ("F30", "B-30", "GND"),                  # 위쪽 GND 칸 (센서 - 선 받는 곳)
]

# 밖에서 들어오는 선 (기판에 바로 납땜)
external += [("E21", "+5V", "DC 잭 +"), ("B-26", "GND", "DC 잭 -")]
for m, (o1, o2) in {1: ("A5", "A4"), 2: ("A2", "A3"), 3: ("A14", "A13"), 4: ("A11", "A12")}.items():
    external += [(o1, f"M{m}_OUT1", f"가루 모터 {m} (1)"), (o2, f"M{m}_OUT2", f"가루 모터 {m} (2)")]
external += [("J23", "HX_DT", "HX711 DT"), ("J24", "HX_SCK", "HX711 SCK"),
             ("T+23", "+3V3", "HX711 VCC"), ("J30", "GND", "HX711 GND")]
for k, (s, plus, minus) in enumerate([("J25", "T+25", "J29"), ("J26", "T+26", "I29"),
                                      ("J27", "T+27", "H29"), ("J28", "T+28", "F29")], 1):
    external += [(s, f"HALL{k}", f"홀 {k + 4}칸 S"), (plus, "+3V3", f"홀 {k + 4}칸 +"), (minus, "GND", f"홀 {k + 4}칸 -")]

for _, (h, _, label, kind) in enumerate(pins):
    if kind in ("esp", "mcp"):
        x, y = xy(h)
        bodies.append((label, "header", ("rect", x - 1.27, y - 1.27, x + 1.27, y + 1.27, 0, 22)))


# ---------------- 검사 ----------------
def all_holes():
    hs = [(r, c) for r in TOP_ROWS + BOT_ROWS for c in range(1, 31)]
    return hs + [(r, c) for r in ROW_Y if len(r) == 2 for c in range(1, 31)]


def check():
    errors = []
    parent = {h: h for h in all_holes()}

    def find(h):
        while parent[h] != h:
            parent[h] = parent[parent[h]]
            h = parent[h]
        return h

    def union(a, b):
        parent[find(a)] = find(b)

    for c in range(1, 31):                          # 기판에 원래 있는 구리: 칸 묶음, 전원줄
        for group in (TOP_ROWS, BOT_ROWS):
            for r in group[1:]:
                union((group[0], c), (r, c))
        for rail in ("T-", "T+", "B-", "B+"):
            union((rail, 1), (rail, c))
    for a, b, _ in wires:
        union(hole(a), hole(b))

    # 1. 구멍 하나에 다리 하나
    used = {}
    for h, net, label, _ in pins:
        used.setdefault(h, []).append(label)
    for a, b, _ in wires:
        used.setdefault(hole(a), []).append("선")
        used.setdefault(hole(b), []).append("선")
    for h, _, label in external:
        used.setdefault(hole(h), []).append(label)
    for h, who in used.items():
        if h not in parent:
            errors.append(f"없는 구멍 {h}")
        elif len(who) > 1:
            errors.append(f"구멍 {h[0]}{h[1]} 에 둘 이상: {who}")
        if h[0] in ("T-", "B+"):
            errors.append(f"바깥 전원줄(턱 밑) 사용: {h} {who}")

    # 2. 넷: 같은 넷은 한 섬, 다른 넷은 다른 섬
    net_of_island, island_of_net = {}, {}
    items = [(h, net, label) for h, net, label, _ in pins if net]
    items += [(hole(a), net, "선") for a, _, net in wires] + [(hole(h), net, label) for h, net, label in external]
    items += [((r, 1), net) + ("전원줄",) for r, net in RAIL_USE.items()]
    for h, net, label in items:
        isl = find(h)
        if net_of_island.setdefault(isl, net) != net:
            errors.append(f"합선: {net} 와 {net_of_island[isl]} 이 이어짐 ({label} @ {h[0]}{h[1]})")
        island_of_net.setdefault(net, set()).add(isl)
    for net, isl in island_of_net.items():
        if len(isl) > 1:
            errors.append(f"끊김: {net} 이 {len(isl)} 덩어리로 나뉨")

    # 3. circuit.py 와 비교: 모든 부품 핀이 같은 넷에 있는지
    want = []
    for name, net in C.ESP_NET.items():
        want.append(("ESP " + name, "+5V" if net == "ESP_5V" else net))
    for ref, c0 in DRV_COLS.items():
        a, b = drv_motor[ref]
        left, right = C.drv_nets(a, b)
        want += [(f"{ref} L{i + 1}", n) for i, n in enumerate(left) if n]
        want += [(f"{ref} R{i + 1}", n) for i, n in enumerate(right) if n]
    want += [("MCP " + n, n) for n in C.HEADERS["J_I2C"][1]]
    want += [("HX " + n, n) for n in C.HEADERS["J_HX"][1]]
    for k in range(1, 5):
        want += [(f"HALL{k} " + n, n) for n in C.HEADERS[f"J_H{k}"][1]]
    for ref, nets in C.CAPS.items():
        want += [(ref, n) for n in nets]
    for ref, (_, nets) in C.RESISTORS.items():
        want += [(ref, n) for n in nets]
    for ref in ("J_PWR", "J_M1", "J_M2", "J_M3", "J_M4"):
        want += [(ref, n) for n in C.TERMINALS[ref][1]]
    have = {}
    for h, net, label in items:
        have.setdefault(net, 0)
        have[net] += 1
    for who, net in want:
        if net not in island_of_net:
            errors.append(f"circuit.py 의 {who} → {net} 가 기판에 없음")
    extra = set(island_of_net) - {n for _, n in want}
    for n in extra:
        errors.append(f"circuit.py 에 없는 넷: {n}")
    # 핀 수 비교 (ESP 19 · MCP 5 · 센서 16 · 모터 8 · 소켓 32)
    counts = {k: sum(1 for p in pins if p[3] == k) for k in ("esp", "mcp", "socket", "cap", "res")}
    expect = {"esp": sum(1 for n in C.ESP_NET.values() if n), "mcp": 5, "socket": 32, "cap": 6, "res": 4}
    for k in expect:
        if counts[k] != expect[k]:
            errors.append(f"{k} 핀 수 {counts[k]} ≠ {expect[k]}")

    # 4. 겹침: 키 있는 부품끼리, 부품 밑 구멍 사용, 받침 턱
    def overlap(s1, s2):
        if s1[0] == "rect" and s2[0] == "rect":
            return s1[1] < s2[3] - 0.05 and s2[1] < s1[3] - 0.05 and s1[2] < s2[4] - 0.05 and s2[2] < s1[4] - 0.05
        if s1[0] == "circle" and s2[0] == "rect":
            s1, s2 = s2, s1
        if s1[0] == "rect" and s2[0] == "circle":
            cx = min(max(s2[1], s1[1]), s1[3])
            cy = min(max(s2[2], s1[2]), s1[4])
            return math.hypot(cx - s2[1], cy - s2[2]) < s2[3] - 0.05
        return math.hypot(s1[1] - s2[1], s1[2] - s2[2]) < s1[3] + s2[3] - 0.05

    def zrange(s):
        return s[-2], s[-1]

    for i, (n1, k1, s1) in enumerate(bodies):
        for n2, k2, s2 in bodies[i + 1:]:
            if {k1, k2} <= {"module", "socket"}:
                continue
            z1, z2 = zrange(s1), zrange(s2)
            if z1[0] < z2[1] and z2[0] < z1[1] and overlap(s1, s2):
                errors.append(f"부딪힘: {n1} ↔ {n2}")
    for h, who in used.items():
        x, y = xy(h)
        dot = ("circle", x, y, 0.6, 0, 1)
        for n, k, s in bodies:
            if k in ("module",):
                continue                 # 모듈 밑(높이 8.5) 은 납작한 선이 지나갈 수 있음
            if k == "socket" and h[0] in (DRV_TOP, DRV_BOT) and all(w in C.DRV_LEFT + C.DRV_RIGHT for w in who):
                continue                 # 소켓 자기 구멍
            if overlap(s, dot) and not any(n.split()[0] in w for w in who) and not (k == "header" and n in who):
                errors.append(f"구멍 {h[0]}{h[1]} ({who}) 이 {n} 밑에 깔림")
        if y < LIP + 0.6 or y > PB_D - LIP - 0.6:
            errors.append(f"구멍 {h[0]}{h[1]} 이 받침 턱 밑")
    for n, k, s in bodies:
        y0, y1 = (s[2] - s[3], s[2] + s[3]) if s[0] == "circle" else (s[2], s[4])
        if y0 < LIP or y1 > PB_D - LIP:
            errors.append(f"{n} 이 받침 턱({LIP}mm)에 걸림")
    return errors, counts


# ---------------- 그림 ----------------
NET_COLOR = {"+5V": (220, 40, 40), "+3V3": (245, 140, 0), "GND": (30, 30, 30)}


def net_color(net):
    if net in NET_COLOR:
        return NET_COLOR[net]
    if net.startswith("M") and "_OUT" in net:
        return (150, 60, 200)
    if net.startswith("M"):
        return (0, 130, 200)
    return (0, 150, 90)


def draw_top(path):
    from PIL import Image, ImageDraw, ImageFont
    S, M = 13, 60                                  # 1mm = 13px, 여백
    LEG = 430
    n_rows = sum(1 for p in pins if p[3] in ("esp", "mcp")) + len(external)
    W, H = int(PB_W * S) + 2 * M + LEG, max(int(PB_D * S) + 2 * M + 40, M + 30 + int(n_rows * 15.2) + 20)
    im = Image.new("RGB", (W, H), (250, 250, 247))
    d = ImageDraw.Draw(im)
    f = lambda s: ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", s)
    fb = lambda s: ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", s)
    X = lambda x: M + x * S
    Y = lambda y: M + 30 + y * S
    d.text((M, 12), "만능기판 납땜 배치도 (위에서 본 모습)", font=fb(22), fill=(20, 20, 20))
    # 기판, 턱
    d.rounded_rectangle([X(0), Y(0), X(PB_W), Y(PB_D)], radius=3 * S, fill=(28, 70, 140))
    for y0, y1 in ((0, LIP), (PB_D - LIP, PB_D)):
        d.rectangle([X(0), Y(y0), X(PB_W), Y(y1)], fill=(90, 110, 150))
    d.text((X(PB_W) - 210, Y(0) - 4), "받침 턱 (여기엔 아무것도 X)", font=f(12), fill=(220, 230, 255))
    # 기판 구리 (칸 묶음 · 전원줄)
    for c in range(1, 31):
        for g in (TOP_ROWS, BOT_ROWS):
            x = X(xy((g[0], c))[0])
            d.line([x, Y(ROW_Y[g[0]]), x, Y(ROW_Y[g[-1]])], fill=(200, 175, 90), width=7)
    for r in ("T-", "T+", "B-", "B+"):
        y = Y(ROW_Y[r])
        col = {"T+": (245, 140, 0), "B-": (60, 60, 60)}.get(r, (110, 120, 150))
        d.line([X(COL_X0), y, X(COL_X0 + 29 * P), y], fill=col, width=7)
    # 글자: 칸 번호, 줄 이름
    for c in range(1, 31):
        x = X(xy(("A", c))[0])
        d.text((x - 6, Y(ROW_Y["F"] + 2.0)), str(c), font=f(11), fill=(230, 230, 230))
    for r, y in ROW_Y.items():
        name = {"T+": "3V3", "B-": "GND", "T-": "안씀", "B+": "안씀"}.get(r, r)
        d.text((X(0) - 44, Y(y) - 9), name, font=fb(13), fill=(40, 40, 40))
    # 구멍
    for h in all_holes():
        x, y = xy(h)
        d.ellipse([X(x) - 5, Y(y) - 5, X(x) + 5, Y(y) + 5], fill=(235, 215, 140), outline=(120, 100, 40))
    # DRV 모듈 외곽, 소켓
    for n, k, s in bodies:
        if k == "module":
            d.rectangle([X(s[1]), Y(s[2]), X(s[3]), Y(s[4])], outline=(170, 120, 255), width=3)
            d.text((X(s[1]) + 28, Y((s[2] + s[4]) / 2) - 16), n + "\n(모듈 밑으로 선 지나감)", font=fb(14), fill=(220, 200, 255))
        elif k == "socket":
            d.rectangle([X(s[1]), Y(s[2]), X(s[3]), Y(s[4])], outline=(10, 10, 10), width=3)
    # 기판 위 선
    for a, b, net in wires:
        (ax, ay), (bx, by) = xy(hole(a)), xy(hole(b))
        c = net_color(net)
        d.line([X(ax), Y(ay), X(bx), Y(by)], fill=(255, 255, 255), width=8)
        d.line([X(ax), Y(ay), X(bx), Y(by)], fill=c, width=5)
    # 부품
    for n, k, s in bodies:
        if k == "cap":
            d.ellipse([X(s[1] - s[3]), Y(s[2] - s[3]), X(s[1] + s[3]), Y(s[2] + s[3])], outline=(20, 40, 120), width=3)
            d.text((X(s[1]) - 30, Y(s[2]) - 10), n + " 1000µF", font=fb(12), fill=(255, 255, 255))
        if k == "res":
            d.rectangle([X(s[1]), Y(s[2]), X(s[3]), Y(s[4])], fill=(225, 195, 140), outline=(90, 60, 20))
    for h, net, label, kind in pins:
        x, y = xy(h)
        if kind == "socket":
            d.ellipse([X(x) - 6, Y(y) - 6, X(x) + 6, Y(y) + 6], fill=(15, 15, 15))
            t = label if label != "NC" else "-"
            ty = Y(y) - 26 if h[0] == DRV_TOP else Y(y) + 8
            d.text((X(x) - 3, ty), t, font=f(10), fill=(255, 255, 255), anchor=None)
        elif kind in ("esp", "mcp"):
            col = (255, 220, 0) if kind == "esp" else (0, 220, 220)
            d.rectangle([X(x) - 7, Y(y) - 7, X(x) + 7, Y(y) + 7], fill=(20, 20, 20), outline=col, width=3)
        elif kind == "cap":
            d.ellipse([X(x) - 5, Y(y) - 5, X(x) + 5, Y(y) + 5], fill=(255, 255, 255) if "+" in label else (120, 120, 120))
            d.text((X(x) + 6, Y(y) - 9), "+" if "+" in label else "-", font=fb(14), fill=(255, 255, 255))
        elif kind == "res":
            d.ellipse([X(x) - 4, Y(y) - 4, X(x) + 4, Y(y) + 4], fill=(150, 150, 150))
    for h, net, label in external:
        x, y = xy(hole(h))
        c = net_color(net)
        d.ellipse([X(x) - 7, Y(y) - 7, X(x) + 7, Y(y) + 7], outline=c, width=4)
        d.ellipse([X(x) - 3, Y(y) - 3, X(x) + 3, Y(y) + 3], fill=c)
    # 번호표: ESP·MCP 핀, 밖에서 오는 선 → 오른쪽 목록
    lx = X(PB_W) + 30
    d.text((lx, Y(0) - 26), "구멍 → 무엇", font=fb(16), fill=(20, 20, 20))
    rows = []
    for h, net, label, kind in pins:
        if kind in ("esp", "mcp"):
            rows.append((h, label, "수 핀헤더 (점퍼)", (230, 190, 0) if kind == "esp" else (0, 170, 170)))
    for h, net, label in external:
        rows.append((hole(h), label, "선 납땜", net_color(net)))
    rows.sort(key=lambda r: (["T+", "J", "I", "H", "G", "F", "E", "D", "C", "B", "A", "B-"].index(r[0][0]), r[0][1]))
    yy = Y(0)
    for h, label, how, col in rows:
        d.rectangle([lx, yy + 3, lx + 10, yy + 13], fill=col)
        d.text((lx + 16, yy - 2), f"{h[0]}{h[1]:<3}", font=fb(12), fill=(20, 20, 20))
        d.text((lx + 62, yy - 2), label, font=f(12), fill=(20, 20, 20))
        d.text((lx + 210, yy - 2), how, font=f(11), fill=(110, 110, 110))
        yy += 15.2
    # 범례
    ly = Y(PB_D) + 18
    items = [((220, 40, 40), "5V 선"), ((245, 140, 0), "3V3 선"), ((30, 30, 30), "GND 선"),
             ((0, 130, 200), "모터 신호"), ((150, 60, 200), "모터 출력"), ((0, 150, 90), "센서·I2C")]
    xx = M
    for col, t in items:
        d.line([xx, ly + 8, xx + 26, ly + 8], fill=col, width=5)
        d.text((xx + 32, ly - 2), t, font=f(13), fill=(30, 30, 30))
        xx += 120
    d.text((M, ly + 22), "■ 노랑 테두리 = ESP32 로 가는 수 핀   ■ 하늘 테두리 = MCP23017 로 가는 수 핀   ● 동그라미 = 밖에서 오는 선을 바로 납땜   "
           "금색 세로줄 = 기판 안에서 이미 이어진 5구멍", font=f(12), fill=(60, 60, 60))
    im.save(path)


def scad_model(path):
    out = ["// perfboard.py 가 만든 파일. 직접 고치지 말 것", "$fn=24;"]
    T = 1.6
    sx = lambda x: x
    sy = lambda y: PB_D - y           # OpenSCAD 는 y 가 위로
    out.append(f"color([0.11,0.27,0.55]) difference() {{ translate([0,0,-{T}]) cube([{PB_W},{PB_D},{T}]);")
    for h in all_holes():
        x, y = xy(h)
        out.append(f"  translate([{sx(x):.2f},{sy(y):.2f},-2]) cylinder(d=1.0,h=3);")
    out.append("}")
    for h in all_holes():   # 구멍 둘레 금색
        x, y = xy(h)
        out.append(f"color([0.85,0.72,0.35]) translate([{sx(x):.2f},{sy(y):.2f},0]) difference(){{cylinder(d=1.9,h=0.05);cylinder(d=1.0,h=1);}}")
    for n, k, s in bodies:
        if k == "socket":
            out.append(f"color([0.08,0.08,0.08]) translate([{s[1]:.2f},{sy(s[4]):.2f},0]) cube([{s[3]-s[1]:.2f},{s[4]-s[2]:.2f},8.5]);")
        elif k == "module":
            out.append(f"color([0.45,0.2,0.65]) translate([{s[1]:.2f},{sy(s[4]):.2f},8.5]) cube([{s[3]-s[1]:.2f},{s[4]-s[2]:.2f},1.6]);")
            cx, cy = (s[1] + s[3]) / 2, sy((s[2] + s[4]) / 2)
            out.append(f"color([0.1,0.1,0.1]) translate([{cx-3:.2f},{cy-2.5:.2f},10.1]) cube([6,5,1]);")
        elif k == "cap":
            out.append(f"color([0.1,0.15,0.35]) translate([{s[1]:.2f},{sy(s[2]):.2f},0.5]) cylinder(r={s[3]},h=13);")
            out.append(f"color([0.75,0.75,0.8]) translate([{s[1]:.2f},{sy(s[2]):.2f},13.4]) cylinder(r={s[3]-0.6},h=0.2);")
        elif k == "res":
            cx, cy = (s[1] + s[3]) / 2, sy((s[2] + s[4]) / 2)
            out.append(f"color([0.85,0.75,0.55]) translate([{cx:.2f},{cy:.2f},1.4]) rotate([90,0,0]) cylinder(d=2.3,h=6.3,center=true);")
    for h, net, label, kind in pins:
        x, y = xy(h)
        if kind in ("esp", "mcp"):
            out.append(f"color([0.1,0.1,0.1]) translate([{x-1.27:.2f},{sy(y)-1.27:.2f},0]) cube([2.54,2.54,2.5]);")
            out.append(f"color([0.9,0.75,0.3]) translate([{x-0.32:.2f},{sy(y)-0.32:.2f},0]) cube([0.64,0.64,8.5]);")
        if kind == "res":
            pass
    def bent(x1, y1, x2, y2, c, z=1.2, r=0.55):
        return (f"color([{c[0]/255:.2f},{c[1]/255:.2f},{c[2]/255:.2f}]) {{"
                f"hull(){{translate([{x1:.2f},{y1:.2f},0])sphere(r={r});translate([{x1:.2f},{y1:.2f},{z}])sphere(r={r});}}"
                f"hull(){{translate([{x1:.2f},{y1:.2f},{z}])sphere(r={r});translate([{x2:.2f},{y2:.2f},{z}])sphere(r={r});}}"
                f"hull(){{translate([{x2:.2f},{y2:.2f},{z}])sphere(r={r});translate([{x2:.2f},{y2:.2f},0])sphere(r={r});}}}}")
    for a, b, net in wires:
        (ax, ay), (bx, by) = xy(hole(a)), xy(hole(b))
        out.append(bent(ax, sy(ay), bx, sy(by), net_color(net)))
    for h, net, label in external:   # 밖으로 나가는 선: 가까운 가장자리로
        x, y = xy(hole(h))
        if label.startswith("DC"):
            ex, ey = PB_W + 8, sy(y)
        elif y < PB_D / 2:
            ex, ey = x, PB_D + 8
        else:
            ex, ey = x, -8
        z = 4.5 if h.startswith("T+") else 2.5   # 3V3 줄에서 나가는 선은 한 층 위로 (그림에서 겹치지 않게)
        out.append(bent(x, sy(y), ex, ey, net_color(net), z=z))
    open(path, "w", encoding="utf-8").write("\n".join(out))


def draw_connect(path):
    """연결도: 만능기판 안의 회로 + 밖의 모듈까지, 선 종류와 가닥 수"""
    from PIL import Image, ImageDraw, ImageFont
    W, H = 2000, 1030
    im = Image.new("RGB", (W, H), (250, 250, 247))
    d = ImageDraw.Draw(im)
    f = lambda s: ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", s)
    fb = lambda s: ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", s)

    def box(x, y, w, h, title, fill=(255, 255, 255), outline=(60, 60, 60), lines=(), size=14):
        d.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=fill, outline=outline, width=3)
        d.text((x + 12, y + 8), title, font=fb(17), fill=(20, 20, 20))
        for i, t in enumerate(lines):
            d.text((x + 12, y + 36 + i * (size + 5)), t, font=f(size), fill=(50, 50, 50))

    def link(pts, color, label="", lpos=0.5, width=4, off=(6, -24)):
        d.line(pts, fill=color, width=width, joint="curve")
        if label:
            i = min(int(lpos * (len(pts) - 1)), len(pts) - 2)
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]
            d.text(((x1 + x2) / 2 + off[0], (y1 + y2) / 2 + off[1]), label, font=f(14), fill=color)

    d.text((30, 18), "연결도 (회로)  —  만능기판 안과 밖", font=fb(24), fill=(20, 20, 20))
    d.text((30, 54), "선 색: 빨강 5V · 주황 3V3 · 검정 GND · 파랑 모터 신호 · 보라 모터 전원 · 초록 센서/I2C.  "
           "글자 = 선 종류, 가닥 수, 길이", font=f(15), fill=(80, 80, 80))
    R, O, K, B, V, G = (220, 40, 40), (235, 130, 0), (30, 30, 30), (0, 120, 200), (150, 60, 200), (0, 150, 90)

    # ESP32
    esp_rows = [("IO25", "가루1 IN1"), ("IO26", "가루1 IN2"), ("IO27", "가루2 IN1"), ("IO13", "가루2 IN2"),
                ("IO32", "가루3 IN1"), ("IO23", "가루3 IN2"), ("IO4", "가루4 IN1"), ("IO19", "가루4 IN2"),
                ("IO21", "SDA"), ("IO22", "SCL"), ("IO18", "HX711 DT"), ("IO33", "HX711 SCK"),
                ("IO36", "홀 5칸"), ("IO39", "홀 6칸"), ("IO34", "홀 7칸"), ("IO35", "홀 8칸"),
                ("3V3", "3V3 줄"), ("GND", "GND 줄"), ("5V", "5V (USB 굽기 전 뽑기!)")]
    box(30, 110, 330, 520, "ESP32-DevKitC", lines=[f"{a:<5} → {b}" for a, b in esp_rows], size=15)

    # 만능기판
    bx, by, bw, bh = 520, 110, 760, 640
    box(bx, by, bw, bh, "만능기판 (89×52, 납땜)", fill=(232, 240, 252), outline=(28, 70, 140))
    d.line([bx + 30, by + 60, bx + bw - 30, by + 60], fill=O, width=8)
    d.text((bx + 34, by + 64), "3V3 줄 (위 안쪽 +)", font=fb(14), fill=O)
    d.line([bx + 30, by + bh - 40, bx + bw - 30, by + bh - 40], fill=K, width=8)
    d.text((bx + 34, by + bh - 68), "GND 줄 (아래 안쪽 -)", font=fb(14), fill=K)
    for i, (ref, ms) in enumerate([("DRV8833 U1", "가루 1 · 2"), ("DRV8833 U2", "가루 3 · 4")]):
        x = bx + 40 + i * 250
        box(x, by + 120, 210, 230, ref, fill=(240, 230, 255), outline=(150, 60, 200),
            lines=[f"맡는 모터: {ms}", "AIN1 AIN2 BIN1 BIN2", "  ← ESP32 (파랑)", "STBY → 3V3", "VM → 5V,  GND → GND",
                   "AO1 AO2 BO1 BO2", "  → 모터 (보라)"], size=13)
        link([(x + 105, by + 120), (x + 105, by + 66)], O, "STBY", off=(6, -10))
        link([(x + 105, by + 350), (x + 105, by + bh - 46)], K, "GND", off=(6, -40))
    # 5V 칸
    box(bx + 540, by + 120, 190, 150, "5V 칸 (21번 칸)", fill=(255, 235, 235), outline=R,
        lines=["DC 잭 + 가 여기로", "U1 · U2 VM", "MCP 5V, ESP 5V", "C1~C3 1000µF +"], size=13)
    box(bx + 540, by + 300, 190, 120, "풀업 R1 · R2 4.7k", fill=(255, 248, 230), outline=O,
        lines=["SDA → 3V3", "SCL → 3V3"], size=13)
    box(bx + 540, by + 440, 190, 130, "커패시터 1000µF ×3", fill=(235, 240, 255), outline=(20, 40, 120),
        lines=["+ = 5V,  - = GND", "모터가 돌 때", "전압 꺼짐을 메움"], size=13)

    # 왼쪽 연결
    link([(360, 200), (520, 270)], B, "F-F 30cm ×8 (모터 신호)", off=(-60, -52))
    link([(360, 420), (520, 420)], G, "F-F 30cm ×8 (I2C·HX·홀)", off=(-150, -26))
    link([(360, 590), (520, 590)], K, "F-F 30cm ×3 (3V3·GND·5V)", off=(-150, -26))
    # DC 잭
    box(1380, 110, 220, 90, "DC 잭 (5V 4A)", lines=["터미널블럭 to DC"], size=13)
    link([(1380, 150), (1280, 230)], R, "단선 2가닥 (+, -)", off=(10, 20))

    # 가루 모터
    for i in range(4):
        x = 560 + i * 180
        box(x, 860, 160, 90, f"가루 모터 {i + 1}", lines=["JGA25-370", "단자에 0.1µF 납땜"], size=12)
        link([(x + 80, 860), (x + 80, 750)], V, "단선 2" if i == 0 else "", off=(8, -10))
    d.text((560, 960), "모터 → 기판: 단선 0.6, 뒤쪽 2개 45cm · 앞쪽 2개 65cm, 기판 A줄에 바로 납땜", font=f(14), fill=V)

    # MCP · ULN · 28BYJ
    box(1420, 260, 220, 130, "MCP23017", lines=["주소 0x20", "GPA0~7, GPB0~7", "→ ULN2003 ×4"], size=13)
    link([(1280, 330), (1420, 330)], G, "F-F 30cm 2개 이음 ×5", off=(-60, -48))
    d.text((1290, 345), "(SDA SCL 3V3 GND 5V,\n 이음은 수 핀헤더)", font=f(12), fill=G)
    box(1420, 420, 220, 110, "5V · GND 갈래", fill=(255, 240, 240), outline=R,
        lines=["수 핀헤더 5핀 · 6핀을", "맨 선으로 묶음"], size=13)
    link([(1530, 390), (1530, 420)], R)
    for i in range(4):
        y = 250 + i * 150
        box(1720, y, 250, 120, f"ULN2003 #{i + 1} → 28BYJ", lines=[f"알약 {i + 5}칸", "IN1~4 ← MCP (F-F 30cm)", "+ - ← 갈래 (F-F 30cm)"], size=12)
        link([(1640, 320), (1720, y + 60)], G)
    d.text((1660, 860), "MCP → ULN 신호 16가닥,\n갈래 → ULN 전원 8가닥\n(모두 F-F 30cm)", font=f(14), fill=G)

    # HX711 · 로드셀, 홀
    box(1380, 640, 230, 120, "HX711 → 로드셀", lines=["로드셀 4선은 HX711에 납땜", "E+ E- A- A+"], size=12)
    link([(1280, 690), (1380, 690)], G, "단선 4 (55cm)", off=(-100, -28))
    box(1380, 790, 230, 120, "홀 센서 ×4", lines=["알약 5~8칸 원점", "다리에 납땜 + 수축튜브"], size=12)
    link([(1280, 720), (1380, 840)], G, "단선 3×4 (45/60cm)", off=(-160, 10))

    d.text((30, 995), "회로 정보는 circuit.py 하나에서 나옴. 만능기판 배치(perfboard_top.png)는 perfboard.py 검사로 이 회로와 같은지 확인함",
           font=f(14), fill=(110, 110, 110))
    im.save(path)


OPENSCAD = r"C:\Program Files\OpenSCAD\openscad.exe"


def render_3d(scad, png):
    tmp = png + ".tmp.png"      # 편집기에서 열려 있으면 바로 덮어쓰기가 실패해서, 다른 이름으로 만든 뒤 바꿈
    cmd = [OPENSCAD, "-o", tmp, "--imgsize=1800,1150", "--colorscheme=Tomorrow",
           "--camera=44.5,24,0,50,0,15,215", scad]
    subprocess.run(cmd, check=True, capture_output=True)
    os.replace(tmp, png)


if __name__ == "__main__":
    errors, counts = check()
    print("핀:", counts, "| 선:", len(wires), "| 밖에서 오는 선:", len(external))
    if errors:
        print("검사 실패:")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print("검사 통과: 구멍 겹침 없음, 합선·끊김 없음, circuit.py 넷과 일치, 부품끼리 안 부딪힘, 받침 턱 피함")
    draw_top(os.path.join(HERE, "perfboard_top.png"))
    draw_connect(os.path.join(HERE, "perfboard_connect.png"))
    scad = os.path.join(HERE, "perfboard_3d.scad")
    scad_model(scad)
    render_3d(scad, os.path.join(HERE, "perfboard_3d.png"))
    print("그림: perfboard_top.png, perfboard_3d.png")
