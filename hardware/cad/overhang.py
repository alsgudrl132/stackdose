"""출력 방향 그대로의 STL 에서 서포트가 필요할 만한 면을 찾는다.

- 아래를 향하고, 수평에서 45° 이내로 누운 면(= 벽에서 45° 넘게 기운 면)만 센다.
- 출력판 위(최저 z 에서 0.3mm 이내)는 제외.
- 면들을 한 덩어리로 묶어서 넓이와 위치를 보여 준다. 폭이 좁은 것(구멍 천장, 너트 홈 천장)은 다리(브리지)로 뽑히므로 괜찮다.
"""
import os, sys, math
from check import stl_bbox_volume, OUT
import re, struct


def load(path):
    data = open(path, "rb").read()
    if data[:5] == b"solid" and b"facet" in data[:512]:
        vs = [tuple(map(float, m)) for m in re.findall(rb"vertex\s+(\S+)\s+(\S+)\s+(\S+)", data)]
        return [vs[i:i + 3] for i in range(0, len(vs) - 2, 3)]
    n = struct.unpack("<I", data[80:84])[0]
    return [[struct.unpack("<3f", data[84 + i * 50 + 12 + k * 12: 84 + i * 50 + 24 + k * 12]) for k in range(3)] for i in range(n)]


def analyze(path, limit_deg=44):
    tris = load(path)
    zmin = min(p[2] for t in tris for p in t)
    bad = []
    for a, b, c in tris:
        u = [b[i] - a[i] for i in range(3)]
        v = [c[i] - a[i] for i in range(3)]
        n = [u[1]*v[2] - u[2]*v[1], u[2]*v[0] - u[0]*v[2], u[0]*v[1] - u[1]*v[0]]
        area2 = math.sqrt(sum(x*x for x in n))
        if area2 == 0:
            continue
        nz = n[2] / area2
        if nz < -math.cos(math.radians(limit_deg)) and min(a[2], b[2], c[2]) > zmin + 0.3:
            bad.append((area2 / 2, a, b, c))
    # 꼭짓점을 공유하는 면끼리 한 덩어리로 (union-find)
    parent = list(range(len(bad)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    owner = {}
    for i, (_, a, b, c) in enumerate(bad):
        for p in (a, b, c):
            k = tuple(round(x, 3) for x in p)
            if k in owner:
                ra, rb = find(i), find(owner[k])
                if ra != rb:
                    parent[ra] = rb
            else:
                owner[k] = i
    groups = {}
    for i, (area, a, b, c) in enumerate(bad):
        g = groups.setdefault(find(i), [0, [1e9, 1e9, 1e9], [-1e9, -1e9, -1e9]])
        g[0] += area
        for p in (a, b, c):
            for j in range(3):
                g[1][j] = min(g[1][j], p[j]); g[2][j] = max(g[2][j], p[j])
    return sum(b[0] for b in bad), groups, zmin


if __name__ == "__main__":
    names = sys.argv[1:] or sorted(f[:-4] for f in os.listdir(OUT) if f.endswith(".stl"))
    for name in names:
        total, groups, zmin = analyze(os.path.join(OUT, name + ".stl"))
        # 폭(짧은 변)이 8mm 넘는 덩어리만 경고 — 그보다 좁으면 다리로 뽑힘
        wide = []
        for (k, (area, mn, mx)) in groups.items():
            w = min(mx[0] - mn[0], mx[1] - mn[1])
            if area > 4 and w > 8:
                wide.append((area, mn, mx))
        flag = "OK " if not wide else "확인"
        print(f"[{flag}] {name:18s} 기운 아랫면 합계 {total:7.1f} mm2" + ("" if not wide else f"  넓은 곳 {len(wide)}개"))
        for area, mn, mx in sorted(wide, reverse=True)[:5]:
            print(f"        {area:6.1f} mm2  x {mn[0]:.1f}~{mx[0]:.1f}  y {mn[1]:.1f}~{mx[1]:.1f}  z {mn[2]:.1f}~{mx[2]:.1f}")
