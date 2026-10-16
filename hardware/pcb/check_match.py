# 회로도와 PCB 가 같은 연결인지 비교 (kicad-cli 의 ERC 가 이 PC 에서 죽어서 대신 쓰는 검사)
# 실행: "C:\Program Files\KiCad\10.0\bin\python.exe" hardware/pcb/check_match.py
import os
import re
import subprocess
import tempfile
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
SCH = os.path.join(HERE, "stackdose_ctrl.kicad_sch")
PCB = os.path.join(HERE, "stackdose_ctrl.kicad_pcb")

net_file = os.path.join(tempfile.gettempdir(), "stackdose_sch.net")
r = subprocess.run([CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", net_file, SCH],
                   capture_output=True, text=True, encoding="utf-8", errors="ignore")
warn = (r.stdout + r.stderr).strip()

# 회로도: 넷 이름 → {(부품, 핀)}
sch = {}
text = open(net_file, encoding="utf-8").read()
nets_part = text[text.index("(nets"):]
for chunk in re.split(r"\(net\s*\(code", nets_part)[1:]:   # 넷 하나씩
    name = re.search(r'\(name\s+"([^"]+)"\)', chunk).group(1).lstrip("/")
    nodes = set(re.findall(r'\(node\s*\(ref\s+"([^"]+)"\)\s*\(pin\s+"([^"]+)"\)', chunk))
    if not name.startswith("unconnected-") and not name.startswith("Net-("):
        sch[name] = nodes

# PCB: 넷 이름 → {(부품, 패드)}
board = pcbnew.LoadBoard(PCB)
pcb = {}
for fp in board.GetFootprints():
    for pad in fp.Pads():
        if pad.GetNetname():
            pcb.setdefault(pad.GetNetname(), set()).add((fp.GetReference(), pad.GetNumber()))

problems = []
for n in sorted(set(sch) | set(pcb)):
    a, b = sch.get(n, set()), pcb.get(n, set())
    if a != b:
        problems.append(f"{n}: 회로도에만 {sorted(a - b)} / PCB 에만 {sorted(b - a)}")
print("kicad-cli 경고:", warn or "없음")
print(f"넷 수: 회로도 {len(sch)}, PCB {len(pcb)}")
print("다른 곳:", "\n  ".join(problems) if problems else "없음 (회로도와 PCB 연결이 같음)")
