// =====================================================================
// 저울: 로드셀 받침(고정 끝 + 과부하 멈춤대) + 컵 쟁반(움직이는 끝) + 간격 와셔
// 전역 좌표 (원점 = 바닥판 윗면 가운데). 로드셀은 X 방향으로 누움.
// 고정 끝(전선 나오는 쪽) = M5x15 두 개, 아래에서 위로.
// 움직이는 끝 = M4x12 두 개, 쟁반 위에서 아래로.
// =====================================================================
include <config.scad>
include <lib.scad>

part = "pedestal";   // "pedestal" | "tray" | "spacer" | "all"

lc_x0   = cupP[0] - lc_l/2;       // 고정 끝
lc_x1   = cupP[0] + lc_l/2;       // 움직이는 끝
ped_h   = 12;
lc_z0   = ped_h;                  // 로드셀 아랫면
sp_h    = 3;                      // 간격 와셔 두께 (쟁반이 로드셀 몸통에 닿지 않게)
tray_z0 = lc_z0 + lc_h + sp_h;    // 쟁반 아랫면
tray_t  = 7;
ring_h  = 4;
tray_d  = cup_d_at(4) + 2*clear + 2*3;
cup_z0  = tray_z0 + tray_t;       // 컵 바닥 높이
strip_h = 6;                      // 받침 아래 띠 + 날개
stop_gap = 1.0;                   // 멈춤대 ↔ 로드셀 아랫면 (1kg 에서 휘는 양보다 큼)
stop_x  = lc_x1 - 4;

// 바닥판 핀 2개 (대각선) — 받침은 나사 없이 핀에 얹음
function scale_base_holes() = [[lc_x0 + 12, 20], [stop_x, -16]];
function cup_top_z() = cup_z0 + cup_h;
function cup_z_powder() = cup_z0;
function scale_tray_top() = cup_z0;

// 볼트 물림 길이 (로드셀 나사산에 들어가는 길이)
m5_bite = 15 - (ped_h - lc_fix_head_h);
m4_bite = 12 - (tray_t - lc_load_head_h) - sp_h;
echo(str("M5 물림 ", m5_bite, "mm, M4 물림 ", m4_bite, "mm (로드셀 두께 ", lc_h, ")"));
assert(m5_bite >= 5 && m5_bite < lc_h, "M5 길이 확인");
assert(m4_bite >= 5 && m4_bite < lc_h, "M4 길이 확인");

module pedestal() {
    difference() {
        union() {
            translate([lc_x0 - 4, -lc_w/2 - 4, 0]) cube([lc_holes[1] + 8, lc_w + 8, ped_h]);
            translate([lc_x0 + 4, -26, 0]) cube([16, 52, strip_h]);              // 고정 날개
            translate([lc_x0 - 4, -8, 0]) cube([lc_l + 8, 16, strip_h]);         // 멈춤대까지 띠
            translate([stop_x - 8, -22, 0]) cube([16, 44, strip_h]);             // 멈춤대 쪽 날개
            translate([stop_x - 4, -lc_w/2, 0]) cube([8, lc_w, lc_z0 - stop_gap]); // 멈춤대
        }
        for (h = [lc_holes[0], lc_holes[1]]) translate([lc_x0 + h, 0, 0]) {
            translate([0, 0, -1]) cylinder(d = lc_fix_bolt_d, h = ped_h + 2);
            translate([0, 0, -0.01]) cylinder(d = lc_fix_head_d, h = lc_fix_head_h);   // 머리 (아래에서)
        }
        for (p = scale_base_holes()) translate([p[0], p[1], -1]) cylinder(d = pin_hole, h = strip_h + 2);
    }
}

module tray() {
    difference() {
        union() {
            translate([0, 0, tray_z0]) hull() {
                translate([cupP[0], cupP[1], 0]) cylinder(d = tray_d, h = tray_t);
                translate([lc_x1 - lc_holes[1] - 6, -8, 0]) cube([lc_holes[1] + 6, 16, tray_t]);
            }
            // 컵 받침 링: 링 꼭대기 높이에서의 컵 지름에 맞춤
            translate([cupP[0], cupP[1], cup_z0 - 0.01]) difference() {
                cylinder(d = cup_d_at(ring_h) + 2*clear + 4, h = ring_h);
                translate([0, 0, -1]) cylinder(d = cup_d_at(ring_h) + 2*clear, h = ring_h + 2);
            }
        }
        for (h = lc_holes) translate([lc_x1 - h, 0, tray_z0]) {
            translate([0, 0, -1]) cylinder(d = lc_load_bolt_d, h = tray_t + 2);
            translate([0, 0, tray_t - lc_load_head_h]) cylinder(d = lc_load_head_d, h = lc_load_head_h + 1);
        }
    }
}

module spacer() {
    difference() { cylinder(d = 10, h = sp_h); translate([0, 0, -1]) cylinder(d = lc_load_bolt_d, h = sp_h + 2); }
}

module spacers_placed() {
    for (h = lc_holes) translate([lc_x1 - h, 0, lc_z0 + lc_h]) spacer();
}

module loadcell_ghost() {
    translate([lc_x0, -lc_w/2, lc_z0]) cube([lc_l, lc_w, lc_h]);
}

module cup_ghost(xy, z0) {
    translate([xy[0], xy[1], z0]) cylinder(d1 = cup_bottom_d, d2 = cup_top_d, h = cup_h);
}

module scale_all() {
    color("DimGray") pedestal();
    color("LightGray") tray();
    color("Gray") spacers_placed();
    %loadcell_ghost();
    %cup_ghost(cupP, cup_z0);
}

if      (part == "pedestal") pedestal();
else if (part == "tray")     translate([0, 0, -tray_z0]) tray();
else if (part == "spacer")   spacer();
else if (part == "all")      scale_all();
