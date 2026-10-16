# circuit.py 의 회로로 KiCad PCB 를 만듦 (부품 배치 + 넷 + GND 면). 배선(트랙)은 아직 없음 → KiCad 에서 하거나 자동 배선
# 실행: KiCad 에 들어 있는 파이썬으로
#   "C:\Program Files\KiCad\10.0\bin\python.exe" hardware/pcb/gen_pcb.py
# 결과: hardware/pcb/stackdose_ctrl.kicad_pcb (+ .kicad_pro)
import os
import sys
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import circuit as C  # noqa: E402

FP_DIR = r"C:\Program Files\KiCad\10.0\share\kicad\footprints"
OUT = os.path.join(HERE, "stackdose_ctrl.kicad_pcb")

# ---- 기판 크기와 배치 (mm, 기판 왼쪽 위 = (0, 0), 아래로 +y) ----
BOARD_W, BOARD_H = 92.0, 80.0
O = (50.0, 50.0)                 # KiCad 화면에서 기판을 둘 위치 (보기 편하게)

ESP_X0 = 3.0                     # ESP32 1번 핀 x (안테나가 기판 왼쪽 밖으로 나가게)
ESP_TOP_Y, ESP_ROW_GAP = 6.0, 25.4   # ★ 줄 간격
DRV_X, DRV_ROW_GAP = 68.0, 17.78     # ★ 줄 간격
DRV_Y = {"U1": 5.0, "U2": 42.0}
HEADER_Y = 45.0

board = pcbnew.BOARD()
nets = {}


def mm(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(O[0] + x), pcbnew.FromMM(O[1] + y))


def net(name):
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        nets[name] = n
    return nets[name]


def place(lib, name, ref, value, x, y, deg=0, pad_nets=None):
    fp = pcbnew.FootprintLoad(os.path.join(FP_DIR, lib + ".pretty"), name)
    fp.SetReference(C.REF.get(ref, ref))
    fp.SetValue(value)
    fp.SetOrientationDegrees(deg)
    fp.SetPosition(mm(x, y))
    fp.Reference().SetVisible(False)   # 부품 이름 대신 silk_text 로 쓴 기능 이름을 보여 줌 (겹침 · 잘림 방지)
    fp.Value().SetVisible(False)
    board.Add(fp)
    for pad in fp.Pads():
        i = int(pad.GetNumber()) - 1 if pad.GetNumber().isdigit() else None
        if pad_nets and i is not None and i < len(pad_nets) and pad_nets[i]:
            pad.SetNet(net(pad_nets[i]))
    return fp


def silk_text(text, x, y, size=1.2, deg=0):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(mm(x, y))
    t.SetLayer(pcbnew.F_SilkS)
    t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(size), pcbnew.FromMM(size)))
    t.SetTextThickness(pcbnew.FromMM(size * 0.15))
    t.SetTextAngleDegrees(deg)
    board.Add(t)


def rect(layer, x0, y0, x1, y1, width=0.15):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_RECT)
    s.SetStart(mm(x0, y0))
    s.SetEnd(mm(x1, y1))
    s.SetLayer(layer)
    s.SetWidth(pcbnew.FromMM(width))
    board.Add(s)


def zone(layer, x0, y0, x1, y1, net_name=None, keepout=False):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    poly = z.Outline()
    poly.NewOutline()
    for px, py in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        poly.Append(pcbnew.FromMM(O[0] + px), pcbnew.FromMM(O[1] + py))
    if keepout:   # 구리 면(GND 채우기)만 막음. ESP32 1·2번 핀과 거기로 가는 선은 지나가야 함
        z.SetIsRuleArea(True)
        z.SetDoNotAllowZoneFills(True)
        z.SetDoNotAllowTracks(False)
        z.SetDoNotAllowVias(False)
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
    else:
        z.SetNet(net(net_name))
        z.SetMinThickness(pcbnew.FromMM(0.25))
        z.SetLocalClearance(pcbnew.FromMM(0.4))
    board.Add(z)
    return z


# ---- 기판 테두리 ----
rect(pcbnew.Edge_Cuts, 0, 0, BOARD_W, BOARD_H, 0.1)

# ---- ESP32: 소켓 두 줄 (위에서 봤을 때 그대로 꽂음) ----
place("Connector_PinSocket_2.54mm", "PinSocket_1x19_P2.54mm_Vertical", "J_ESP1", "ESP32 top",
      ESP_X0, ESP_TOP_Y, 90, [C.ESP_NET.get(p) for p in C.ESP_TOP])
place("Connector_PinSocket_2.54mm", "PinSocket_1x19_P2.54mm_Vertical", "J_ESP2", "ESP32 bottom",
      ESP_X0, ESP_TOP_Y + ESP_ROW_GAP, 90, [C.ESP_NET.get(p) for p in C.ESP_BOTTOM])
esp_x0, esp_x1 = ESP_X0 - 1.19, ESP_X0 + 45.72 + 1.19                      # ESP32 기판 (48.1 실측)
esp_y0 = ESP_TOP_Y + ESP_ROW_GAP / 2 - 27.9 / 2
rect(pcbnew.F_SilkS, esp_x0, esp_y0, esp_x1, esp_y0 + 27.9)
silk_text("ESP32-DevKitC   USB >",(esp_x0 + esp_x1) / 2, ESP_TOP_Y + ESP_ROW_GAP / 2, 1.5)
silk_text("ANT", 1.2, ESP_TOP_Y + ESP_ROW_GAP / 2, 1.0, 90)

# ---- DRV8833 ×2: 소켓 두 줄씩 ----
for ref, (a, b) in (("U1", (1, 2)), ("U2", (3, 4))):
    left, right = C.drv_nets(a, b)
    y = DRV_Y[ref]
    place("Connector_PinSocket_2.54mm", "PinSocket_1x08_P2.54mm_Vertical", ref + "L", "DRV8833 L",
          DRV_X, y, 0, left)
    place("Connector_PinSocket_2.54mm", "PinSocket_1x08_P2.54mm_Vertical", ref + "R", "DRV8833 R",
          DRV_X + DRV_ROW_GAP, y, 0, right)
    rect(pcbnew.F_SilkS, DRV_X - 1.6, y - 1.6, DRV_X + DRV_ROW_GAP + 1.6, y + 17.78 + 1.6)
    silk_text(f"DRV8833 {ref} (M{a} M{b})", DRV_X + DRV_ROW_GAP / 2, y + 9, 1.0, 90)
    silk_text("AIN2", DRV_X + 3.2, y + 2.54, 0.8)   # 꽂는 방향 표시 (모듈 인쇄와 맞추기)

# ---- 커패시터: 드라이버 사이 빈칸, 전원 입력 옆 ----
place("Capacitor_THT", "CP_Radial_D10.0mm_P5.00mm", "C1", "1000uF 10V", 72.5, 31.4, 0, C.CAPS["C1"])
place("Capacitor_THT", "CP_Radial_D10.0mm_P5.00mm", "C2", "1000uF 10V", 54.0, 56.0, 0, C.CAPS["C2"])
place("Capacitor_THT", "CP_Radial_D10.0mm_P5.00mm", "C3", "1000uF 10V", 20.0, 66.0, 0, C.CAPS["C3"])

# ---- 바깥으로 나가는 핀헤더: ESP32 아래 한 줄 ----
x = 3.0
for ref in ("J_I2C", "J_HX", "J_H1", "J_H2", "J_H3", "J_H4"):
    label, pins = C.HEADERS[ref]
    n = len(pins)
    place("Connector_PinHeader_2.54mm", f"PinHeader_1x{n:02d}_P2.54mm_Vertical", ref, label, x, HEADER_Y, 90, pins)
    silk_text(label, x + (n - 1) * 2.54 / 2, HEADER_Y - 2.6, 1.0)
    first = {"+3V3": "3V3"}.get(pins[0], pins[0])
    silk_text(first, x, HEADER_Y + 2.6, 0.8)
    x += n * 2.54 + 1.8
# USB 로 굽는 동안 뽑는 점퍼: ESP32 5V 핀 바로 아래
jp_label, jp_pins = C.HEADERS["JP1"]
place("Connector_PinHeader_2.54mm", "PinHeader_1x02_P2.54mm_Vertical", "JP1", jp_label,
      ESP_X0 + 45.72 - 2.54, ESP_TOP_Y + ESP_ROW_GAP + 5.5, 90, jp_pins)
silk_text("OPEN FOR USB",ESP_X0 + 45.72 - 1.27, ESP_TOP_Y + ESP_ROW_GAP + 8.0, 0.8)

# ---- I2C 풀업 저항 ----
place("Resistor_THT", "R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal", "R1", "4.7k", 3.0, 53.0, 0, C.RESISTORS["R1"][1])
place("Resistor_THT", "R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal", "R2", "4.7k", 3.0, 57.0, 0, C.RESISTORS["R2"][1])

# ---- 나사 터미널: 아래 가장자리 (전선이 기판 밖에서 들어오게) ----
# 180° 로 돌려 놓아서 1번 패드가 오른쪽, 2번이 왼쪽 (x - 5.08)
x = 40.0
for ref in ("J_PWR", "J_M1", "J_M2", "J_M3", "J_M4"):
    label, pins = C.TERMINALS[ref]
    place("TerminalBlock_Phoenix", "TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
          ref, label, x, BOARD_H - 6.0, 180, pins)
    silk_text(label, x - 2.54, BOARD_H - 13.0, 1.0)
    x += 11.5   # 터미널 몸통 폭 11.2 + 틈

# ---- 안테나 밑은 구리를 비움 (Wi-Fi 가 약해지지 않게) ----
for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    zone(layer, 0, esp_y0 - 1, ESP_X0 + 3, esp_y0 + 27.9 + 1, keepout=True)

# ---- GND 면: 양면 전체 (GND 는 선 없이 이 면으로 이어짐) ----
for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    zone(layer, 0.3, 0.3, BOARD_W - 0.3, BOARD_H - 0.3, "GND")

board.BuildConnectivity()
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(OUT, board)

pro = OUT.replace(".kicad_pcb", ".kicad_pro")
if not os.path.exists(pro):
    open(pro, "w").write("{}\n")

# 확인용: 넷마다 연결된 패드 수 (1개짜리 넷은 연결이 빠진 것)
counts = {}
for fp in board.GetFootprints():
    for pad in fp.Pads():
        nm = pad.GetNetname()
        if nm:
            counts[nm] = counts.get(nm, 0) + 1
lonely = sorted(n for n, c in counts.items() if c < 2)
print("saved", OUT)
print("nets", len(counts), "| 패드가 1개뿐인 넷:", lonely or "없음")
