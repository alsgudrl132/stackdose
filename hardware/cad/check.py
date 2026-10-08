"""OpenSCAD 설계 자동 검사.

1) 출력할 부품을 전부 STL 로 렌더 → 오류/경고, 크기(출력판 안에 들어가는지)
2) 조립 상태에서 부품 쌍의 겹침(intersection) → 부피가 있으면 실패
사용: python check.py [parts|clash|all]
"""
import os, re, subprocess, sys, struct, itertools, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OPENSCAD = r"C:\Program Files\OpenSCAD\openscad.exe"
OUT = os.path.join(HERE, "stl")
BED = (220, 220, 250)

PARTS = [
    ("coupon.scad", None, "coupon"),
    ("powder.scad", "block", "powder_block"),
    ("powder.scad", "top", "powder_top"),
    ("powder.scad", "strap", "powder_strap"),
    ("powder.scad", "hopper", "powder_hopper"),
    ("powder.scad", "auger", "auger"),
    ("pill.scad", "skirt", "pill_skirt"),
    ("pill.scad", "floor", "pill_floor"),
    ("pill.scad", "disk", "pill_disk"),
    ("pill.scad", "spacer", "pill_spacer"),
    ("pill.scad", "cover", "pill_cover"),
    ("scale.scad", "pedestal", "scale_pedestal"),
    ("scale.scad", "tray", "scale_tray"),
    ("scale.scad", "spacer", "scale_spacer"),
    ("electronics.scad", "ctrl", "ctrl_plate"),
    ("frame.scad", "post", "post"),
    ("frame.scad", "pins", "pins"),
    ("frame.scad", "pegtest", "pegtest"),
    ("frame.scad", "baseP", "base_powder"),
    ("frame.scad", "deckP", "deck_powder"),
    ("frame.scad", "baseL", "base_pill"),
    ("frame.scad", "deckL", "deck_pill"),
]

# 서로 닿기만 해야 하는(겹치면 안 되는) 쌍
Q = range(4)
CLASH = (
    # 가루 모듈끼리, 모듈 안
    [(f"powder{i}", f"powder{(i+1)%4}") for i in Q] + [(f"powder{i}", f"powder{(i+2)%4}") for i in (0, 1)]
    + [(f"motor{i}", f"motor{(i+1)%4}") for i in Q] + [(f"bin{i}", f"bin{(i+1)%4}") for i in Q]
    + [(f"auger{i}", f"powder{i}") for i in Q] + [(f"motor{i}", f"powder{i}") for i in Q]
    + [(f"auger{i}", f"motor{i}") for i in Q] + [(f"motor{i}", f"powder{(i+1)%4}") for i in Q]
    + [(f"motor{i}", f"powder{(i+3)%4}") for i in Q]
    + [(f"powder{i}", "deckP") for i in Q] + [(f"motor{i}", "deckP") for i in Q]
    # 가루 ↔ 알약 스테이션
    + [(f"motor{i}", "deckL") for i in Q] + [(f"powder{i}", "deckL") for i in Q]
    + [(f"motor{i}", f"pill{j}") for i in (0, 3) for j in (1, 2)]
    + [(f"bin{i}", f"pilltop{j}") for i in (0, 3) for j in (1, 2)]
    # 알약 모듈끼리, 모듈 안
    + [(f"pill{i}", f"pill{j}") for i in Q for j in Q if i < j]
    + [(f"pilltop{i}", f"pilltop{j}") for i in Q for j in Q if i < j]
    + [(f"disk{i}", f"pill{i}") for i in Q] + [(f"disk{i}", f"pilltop{i}") for i in Q]
    + [(f"pspacer{i}", f"pill{i}") for i in Q] + [(f"pspacer{i}", f"disk{i}") for i in Q] + [(f"pspacer{i}", f"byj{i}") for i in Q]
    + [(f"byj{i}", f"pill{i}") for i in Q] + [(f"byj{i}", f"disk{i}") for i in Q]
    + [(f"byj{i}", "deckL") for i in Q] + [(f"pilltop{i}", f"pill{i}") for i in Q]
    + [(f"pill{i}", "deckL") for i in Q]
    # 뼈대
    + [("deckP", "postsP"), ("baseP", "postsP"), ("deckL", "postsL"), ("baseL", "postsL"),
       ("deckP", "deckL"), ("baseP", "baseL"), ("postsP", "postsL")]
    # 저울 · 컵 · 전자부품
    + [("scale", "baseP"), ("scale", "loadcell"), ("scale", "cupP"), ("scale", "postsP"),
       ("cupP", "deckP"), ("cupP", "postsP"), ("loadcell", "baseP"), ("loadcell", "postsP"),
       ("cupL", "deckL"), ("cupL", "baseL"), ("cupL", "postsL"),
       ("ctrl", "baseL"), ("ctrl", "postsL"), ("baseP", "loadcell"), ("baseP", "cupP"),
       # 컵 꺼내는 길
       ("sweepP", "deckP"), ("sweepP", "postsP"), ("sweepP", "scale"), ("sweepP", "baseP"),
       ("sweepL", "deckL"), ("sweepL", "postsL"), ("sweepL", "baseL")]
    # 호퍼 · 홀 센서
    + [(f"hopper{i}", f"hopper{(i+1)%4}") for i in Q] + [(f"hopper{i}", f"powder{i}") for i in Q]
    + [(f"hopper{i}", f"bin{i}") for i in Q] + [(f"hopper{i}", f"auger{i}") for i in Q]
    + [(f"hall{i}", f"pill{i}") for i in Q] + [(f"hall{i}", f"byj{i}") for i in Q] + [(f"hall{i}", f"disk{i}") for i in Q]
)


# 일부러 겹치게 만든 쌍: 이 부피(mm3)까지는 정상
#   motor × powder: 모터 덮개 띠가 감속기를 약 0.3mm 눌러 잡음 (squeeze)
ALLOW = {**{(f"motor{i}", f"powder{i}"): 100 for i in Q}}   # 실제 띠 조임 76mm3. 넉넉히 두면 새 겹침을 숨김


def run(args, timeout=1800):
    p = subprocess.run([OPENSCAD] + args, capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=timeout)
    return p.returncode, p.stdout + p.stderr


def stl_bbox_volume(path):
    """ASCII/바이너리 STL 의 경계 상자와 부피(발산 정리)."""
    data = open(path, "rb").read()
    tris = []
    if data[:5] == b"solid" and b"facet" in data[:512]:
        vs = [tuple(map(float, m)) for m in re.findall(rb"vertex\s+(\S+)\s+(\S+)\s+(\S+)", data)]
        tris = [vs[i:i + 3] for i in range(0, len(vs) - 2, 3)]
    else:
        n = struct.unpack("<I", data[80:84])[0]
        for i in range(n):
            o = 84 + i * 50
            v = struct.unpack("<12f", data[o:o + 48])
            tris.append([v[3:6], v[6:9], v[9:12]])
    if not tris:
        return None, 0.0
    pts = [p for t in tris for p in t]
    mn = [min(p[k] for p in pts) for k in range(3)]
    mx = [max(p[k] for p in pts) for k in range(3)]
    vol = 0.0
    for a, b, c in tris:
        vol += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6
    return (mn, mx), abs(vol)


def check_parts():
    os.makedirs(OUT, exist_ok=True)
    ok = True
    for f, part, name in PARTS:
        out = os.path.join(OUT, name + ".stl")
        args = ["-o", out]
        if part:
            args += ["-D", f'part="{part}"']
        code, log = run(args + [os.path.join(HERE, f)])
        warns = [l for l in log.splitlines() if re.search(r"WARNING|ERROR", l)]
        m = re.search(r"Volumes:\s+(\d+)", log)
        if m and int(m.group(1)) != 2 and name not in ("coupon", "pins"):
            warns.append(f"WARNING: 떨어진 덩어리 {int(m.group(1)) - 1}개 (한 덩어리여야 함)")
        if code != 0 or not os.path.exists(out):
            print(f"[실패] {name}: 렌더 오류\n    " + "\n    ".join(warns or log.splitlines()[-5:]))
            ok = False
            continue
        bb, vol = stl_bbox_volume(out)
        size = [bb[1][k] - bb[0][k] for k in range(3)]
        fits = sorted(size[:2]) <= sorted(BED[:2]) and size[2] <= BED[2] or all(s <= min(BED) for s in size)
        fit_xy = (size[0] <= BED[0] and size[1] <= BED[1]) or (size[1] <= BED[0] and size[0] <= BED[1])
        fits = fit_xy and size[2] <= BED[2]
        flag = "OK " if fits and not warns else ("경고" if fits else "크기초과")
        if not fits or warns:
            ok = False      # 경고(떨어진 덩어리 등)도 실패로 봄
        print(f"[{flag}] {name:18s} {size[0]:6.1f} x {size[1]:6.1f} x {size[2]:6.1f} mm  부피 {vol/1000:6.1f} cm3")
        for w in warns:
            print("       ", w.strip())
    return ok


def clash_one(pair):
    a, b = pair
    src = f'use <{os.path.join(HERE, "assembly.scad").replace(os.sep, "/")}>\nintersection() {{ piece("{a}"); piece("{b}"); }}\n'
    with tempfile.NamedTemporaryFile("w", suffix=".scad", delete=False, dir=HERE, encoding="utf-8") as t:
        t.write(src)
        tmp = t.name
    out = tmp[:-5] + ".stl"
    code, log = run(["-o", out, tmp])
    empty = ("top level object is empty" in log) or not os.path.exists(out)
    vol, bb = 0.0, None
    if not empty:
        bb, vol = stl_bbox_volume(out)
        empty = vol < 1.0     # 1 mm3 미만은 면끼리 닿은 것
    for p in (tmp, out):
        if os.path.exists(p):
            os.remove(p)
    return a, b, empty, vol, bb


def check_rest():
    """알약: 대기 위치에서 칸과 출구가 겹치면 안 됨."""
    src = f'use <{os.path.join(HERE, "pill.scad").replace(os.sep, "/")}>\nrest_overlap_check();\n'
    with tempfile.NamedTemporaryFile("w", suffix=".scad", delete=False, dir=HERE, encoding="utf-8") as t:
        t.write(src)
        tmp = t.name
    out = tmp[:-5] + ".stl"
    code, log = run(["-o", out, tmp])
    empty = ("top level object is empty" in log) or not os.path.exists(out)
    for p in (tmp, out):
        if os.path.exists(p):
            os.remove(p)
    print(f"[{'OK ' if empty else '실패'}] 알약 대기 위치: 칸 ↔ 출구 겹침 없음" if empty else "[실패] 알약 대기 위치에서 칸이 출구 위에 걸침")
    return empty


def check_clash(only=None):
    from concurrent.futures import ThreadPoolExecutor
    pairs = [p for p in CLASH if not only or p[0] in only or p[1] in only]
    workers = max(1, (os.cpu_count() or 2) - 1)
    print(f"({len(pairs)}쌍, 동시에 {workers}개씩)")
    ok = True
    with ThreadPoolExecutor(workers) as ex:
        for a, b, empty, vol, bb in ex.map(clash_one, pairs):
            print(f"[{'OK ' if empty else '겹침'}] {a:10s} × {b:10s}" + ("" if empty else f"  겹친 부피 {vol:.1f} mm3  범위 {bb}"), flush=True)
            allowed = ALLOW.get((a, b), 0)
            if not empty and vol <= allowed:
                print(f"       ↳ 의도한 조임 (허용 {allowed} mm3 이하)")
                empty = True
            ok = ok and empty
    return ok


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    res = True
    if what in ("parts", "all"):
        print("=== 부품 렌더 · 크기 ===")
        res = check_parts() and res
    if what in ("rest", "all"):
        print("=== 알약 대기 위치 ===")
        res = check_rest() and res
    if what in ("clash", "all"):
        print("=== 조립 겹침 ===")
        res = check_clash(sys.argv[2:]) and res
    print("\n결과:", "통과" if res else "문제 있음")
