// =====================================================================
// 공차 쿠폰 — 큰 부품보다 먼저 출력 (약 30~40분)
// ---------------------------------------------------------------------
// 1줄: 8mm 핀 구멍 (여유 0.1~0.5) → 핀이 "돌지만 흔들리지 않는" 칸 = clear
// 2줄: JGA25-370 축 D구멍 → 모터 축이 "손으로 꽉 끼는" 칸 (스크류 허브)
// 3줄: 28BYJ-48 축 D구멍 → 같은 기준 (알약 원판 허브)
// 4줄: M3 구멍 3.2~3.6 → 나사가 "힘 없이 지나가는" 가장 작은 칸 = m3_hole
// 5줄: M3 너트 주머니 5.6~6.0 → 너트가 "눌러야 들어가고 안 빠지는" 칸 = m3_nut_af
// 오른쪽: 스크류 20mm 조각 + 관 고리 → 날개가 처지지 않는지, 관 안에서 도는지
// =====================================================================
include <config.scad>
include <lib.scad>
use <powder.scad>

cs   = [0.1, 0.2, 0.3, 0.4, 0.5];
dcs  = [0.0, 0.05, 0.1, 0.15, 0.2];
m3s  = [3.2, 3.3, 3.4, 3.5, 3.6];
nuts = [5.6, 5.7, 5.8, 5.9, 6.0];
pitch = 14;
rows_y = [8, 20, 32, 44, 56];

module label(s, x, y) translate([x, y, 2.4]) linear_extrude(1) text(s, size = 2.6, halign = "center", valign = "center");

difference() {
    cube([len(cs) * pitch + 12, 66, 3]);
    for (i = [0 : 4]) {
        x = 16 + i * pitch;
        translate([x, rows_y[0], -1]) cylinder(d = 8 + 2*cs[i], h = 5);
        translate([x, rows_y[1], -1]) linear_extrude(5) dshaft_jga2d(dcs[i]);
        translate([x, rows_y[2], -1]) linear_extrude(5) dshaft_byj2d(dcs[i]);
        translate([x, rows_y[3], -1]) cylinder(d = m3s[i], h = 5);
        translate([x, rows_y[4], 3 - m3_nut_t]) cylinder(d = nuts[i] / cos(30), h = 5, $fn = 6);
        translate([x, rows_y[4], -1]) cylinder(d = 3.4, h = 5);
    }
    for (r = [0 : 4]) label(str(["C", "J", "B", "M", "H"][r]), 5, rows_y[r]);
    for (i = [0 : 4]) label(str(i + 1), 16 + i * pitch, 63);
}
// 끼워 볼 8mm 핀
translate([-8, 8, 0]) cylinder(d = 8, h = 10);
// 스크류 조각과 관 고리 (실제 치수와 같음)
translate([len(cs) * pitch + 26, 14, 0]) intersection() {
    auger();
    translate([-10, -10, 0]) cube([20, 20, 30.5]);
}
translate([len(cs) * pitch + 26, 44, 0]) difference() {
    cylinder(d = 15 + 2*0.8 + 2*2.4, h = 12);
    translate([0, 0, -1]) cylinder(d = 15 + 2*0.8, h = 14);
}
