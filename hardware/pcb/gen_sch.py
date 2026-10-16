# circuit.py 의 회로로 KiCad 회로도(2D)를 만듦. PCB(gen_pcb.py)와 같은 데이터라 둘이 어긋나지 않음
# 방식: 부품 기호를 놓고, 핀마다 짧은 선 + 넷 이름표(label). 이름이 같은 이름표끼리 연결됨
# 실행: "C:\Program Files\KiCad\10.0\bin\python.exe" hardware/pcb/gen_sch.py
# 결과: hardware/pcb/stackdose_ctrl.kicad_sch
import os
import re
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import circuit as C  # noqa: E402

SYM_DIR = r"C:\Program Files\KiCad\10.0\share\kicad\symbols"
OUT = os.path.join(HERE, "stackdose_ctrl.kicad_sch")
PROJECT = "stackdose_ctrl"
ROOT = str(uuid.uuid4())
G = 2.54   # 회로도 격자. 모든 좌표를 이 배수로 둬야 선이 이어짐


def uid():
    return str(uuid.uuid4())


# ---- 라이브러리에서 기호 정의를 그대로 가져옴 (회로도 파일 안에 같이 넣어야 함) ----
_lib_cache = {}


def lib_symbol(lib, name):
    if lib not in _lib_cache:
        _lib_cache[lib] = open(os.path.join(SYM_DIR, lib + ".kicad_sym"), encoding="utf-8").read()
    text = _lib_cache[lib]
    start = text.index(f'\t(symbol "{name}"\n')
    depth, i = 0, start + 1
    while True:   # 괄호 짝을 세어서 이 기호 블록의 끝을 찾음
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    block = text[start:i + 1].strip()
    pins = {}
    for m in re.finditer(r'\(pin \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)[\s\S]*?\(number "([^"]+)"', block):
        pins[m.group(4)] = (float(m.group(1)), float(m.group(2)), int(float(m.group(3))))
    full = block.replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"', 1)
    return full, pins


used_symbols = {}
items = []


def text(s, x, y, size=2.0):
    items.append(f'(text "{s}" (exclude_from_sim no) (at {x:.2f} {y:.2f} 0) '
                 f'(effects (font (size {size} {size})) (justify left bottom)) (uuid "{uid()}"))')


def wire(x1, y1, x2, y2):
    items.append(f'(wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f})) (stroke (width 0) (type default)) (uuid "{uid()}"))')


def label(name, x, y, angle):
    just = "right bottom" if angle == 180 else "left bottom"
    items.append(f'(label "{name}" (at {x:.2f} {y:.2f} {angle}) (fields_autoplaced yes) '
                 f'(effects (font (size 1.27 1.27)) (justify {just})) (uuid "{uid()}"))')


def no_connect(x, y):
    items.append(f'(no_connect (at {x:.2f} {y:.2f}) (uuid "{uid()}"))')


def symbol(lib, name, ref, value, x, y, pin_nets, footprint="", pin_names=None):
    """기호 하나를 놓고, 핀마다 선 + 넷 이름표 (넷이 없으면 X 표시). pin_names: 기호 옆에 적을 핀 이름"""
    ref = C.REF.get(ref, ref)
    key = f"{lib}:{name}"
    if key not in used_symbols:
        used_symbols[key] = lib_symbol(lib, name)
    _, pins = used_symbols[key]
    pin_uuids = " ".join(f'(pin "{n}" (uuid "{uid()}"))' for n in pins)
    top = y - max(py for _, py, _ in pins.values()) - 2.54   # 부품 이름은 기호 맨 위 핀보다 위에 (핀 이름과 안 겹치게)
    rx, ry, vx, vy = (x, top - 2, x, top) if lib != "Device" else (x + 2.54, y - 1, x + 2.54, y + 1.5)   # C · R 은 옆에
    items.append(
        f'(symbol (lib_id "{key}") (at {x:.2f} {y:.2f} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) '
        f'(uuid "{uid()}") '
        f'(property "Reference" "{ref}" (at {rx:.2f} {ry:.2f} 0) (effects (font (size 1.27 1.27)) (justify left))) '
        f'(property "Value" "{value}" (at {vx:.2f} {vy:.2f} 0) (effects (font (size 1.27 1.27)) (justify left))) '
        f'(property "Footprint" "{footprint}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes))) '
        f'(property "Datasheet" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes))) '
        f'{pin_uuids} '
        f'(instances (project "{PROJECT}" (path "/{ROOT}" (reference "{ref}") (unit 1)))))')
    for num, (px, py, ang) in pins.items():
        cx, cy = x + px, y - py                     # 기호 좌표는 y 가 위로 +, 회로도는 아래로 +
        # 핀이 바깥으로 향하는 방향 (ang 은 연결점에서 몸통 쪽 방향)
        dx, dy = {0: (-1, 0), 180: (1, 0), 90: (0, 1), 270: (0, -1)}[ang]
        i = int(num) - 1
        net_name = pin_nets[i] if i < len(pin_nets) else None
        if pin_names and i < len(pin_names) and pin_names[i]:
            text(pin_names[i], x + 2.2, cy + 0.6, 1.0)
        if not net_name:
            no_connect(cx, cy)
            continue
        ex, ey = cx + dx * 2 * G, cy + dy * 2 * G
        wire(cx, cy, ex, ey)
        label(net_name, ex, ey, {(-1, 0): 180, (1, 0): 0, (0, 1): 270, (0, -1): 90}[(dx, dy)])


def conn(n):
    return "Connector_Generic", f"Conn_01x{n:02d}"


# ---- 배치 (A3, mm) ----
text("stackdose control board (generated from circuit.py)", 20.32, 17.78, 3)
text("Labels with the same name are connected. X = not connected", 20.32, 25.4, 1.6)
text("ESP32-DevKitC (plugs into sockets)", 40.64, 33.02)
symbol(*conn(19), "J_ESP1", "ESP32 top row", 63.5, 63.5,
       [C.ESP_NET.get(p) for p in C.ESP_TOP], "Connector_PinSocket_2.54mm:PinSocket_1x19_P2.54mm_Vertical", C.ESP_TOP)
symbol(*conn(19), "J_ESP2", "ESP32 bottom row", 63.5, 132.08,
       [C.ESP_NET.get(p) for p in C.ESP_BOTTOM], "Connector_PinSocket_2.54mm:PinSocket_1x19_P2.54mm_Vertical", C.ESP_BOTTOM)

text("DRV8833 x2 (VLT-MD012)", 134.62, 33.02)
text("no nFAULT pin on this module", 134.62, 38.1, 1.3)
for ref, (a, b), y in (("U1", (1, 2), 55.88), ("U2", (3, 4), 116.84)):
    left, right = C.drv_nets(a, b)
    symbol(*conn(8), ref + "L", f"DRV8833 {ref} left", 154.94, y, left,
           "Connector_PinSocket_2.54mm:PinSocket_1x08_P2.54mm_Vertical", C.DRV_LEFT)
    symbol(*conn(8), ref + "R", f"DRV8833 {ref} right", 154.94, y + 30.48, right,
           "Connector_PinSocket_2.54mm:PinSocket_1x08_P2.54mm_Vertical", C.DRV_RIGHT)

text("Off-board connectors (pin headers)", 213.36, 33.02)
y = 45.72
for ref in ("J_I2C", "J_HX", "J_H1", "J_H2", "J_H3", "J_H4", "JP1"):
    lbl, pins = C.HEADERS[ref]
    n = len(pins)
    symbol(*conn(n), ref, lbl, 236.22, y + (n - 1) * G / 2 if n % 2 else y + n * G / 2, pins,
           f"Connector_PinHeader_2.54mm:PinHeader_1x{n:02d}_P2.54mm_Vertical")
    y += (n + 3) * G
text("JP1: remove while flashing over USB", 213.36, y + 2.54, 1.3)

text("Screw terminals 5.08mm", 289.56, 33.02)
y = 48.26
for ref in ("J_PWR", "J_M1", "J_M2", "J_M3", "J_M4"):
    lbl, pins = C.TERMINALS[ref]
    symbol(*conn(2), ref, lbl, 312.42, y, pins,
           "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal")
    y += 7 * G

text("Bulk capacitors / I2C pull-ups", 289.56, 182.88)
x = 297.18
for ref, pins in C.CAPS.items():
    symbol("Device", "C_Polarized", ref, "1000uF 10V", x, 205.74, pins, "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm")
    x += 6 * G
for ref, (val, pins) in C.RESISTORS.items():
    symbol("Device", "R", ref, val, x, 205.74, pins, "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
    x += 6 * G

# ---- 파일 쓰기 ----
libs = "\n".join(f"    {full}" for full, _ in used_symbols.values())
body = "\n  ".join(items)
sch = f'''(kicad_sch
  (version 20250114)
  (generator "eeschema")
  (generator_version "9.0")
  (uuid "{ROOT}")
  (paper "A3")
  (title_block (title "stackdose control board") (comment 1 "generated from hardware/pcb/circuit.py"))
  (lib_symbols
{libs}
  )
  {body}
  (sheet_instances (path "/" (page "1")))
)
'''
open(OUT, "w", encoding="utf-8").write(sch)
print("saved", OUT, "| symbols", len(items))
