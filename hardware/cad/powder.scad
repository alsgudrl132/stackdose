// =====================================================================
// 가루 모듈: 스크류(오거) + 반으로 나눈 관 + JGA25-370 받침 + 호퍼
// ---------------------------------------------------------------------
// 로컬 좌표: 관의 축이 +Y 방향. y=0 은 출구 쪽 끝면(컵 중심 쪽), z=0 은 상판 윗면.
// 모터: 감속기 앞면을 관 끝 턱에 대고, 받침 + 덮개 띠로 "눌러서" 잡음(0.3mm 죄임).
//        받침 윗면을 축보다 1mm 낮춰, 볼트를 조이면 띠가 감속기를 누르게 함.
// 출력 부품:
//   powder_block()   아래 반쪽 관 + 모터 받침
//   powder_top()     위 반쪽 관 + 칼라(호퍼 받침 턱 포함)
//   powder_strap()   모터 덮개 띠
//   powder_hopper()  칼라에 씌우는 깔때기 (60° 벽) + 가루통 받침 테두리
//   auger()          스크류 (세워서 출력, 1줄 나선)
// =====================================================================
include <config.scad>
include <lib.scad>

part = "block";   // "block" | "top" | "strap" | "hopper" | "auger" | "module"

// ---- 관과 스크류 ----
tube_id     = 16;     // 관 구멍은 고정. 틈을 바꿀 땐 스크류만 다시 뽑음 (block·top 그대로)
auger_od    = tube_id - 2*auger_gap;
auger_core  = 6;
auger_pitch = 40;     // 크게 잡아야 세워서 출력할 때 날개 아래가 덜 처짐
auger_blade = 3.0;    // 날개 두께 (끝단 강도)
tube_od     = tube_id + 2*3;
axis_h      = 24;     // 상판 윗면 → 축
core_hw     = 12;     // 아래 블록 몸통 반폭
rail_hw     = 20.5;   // 나사 레일 바깥쪽
rail_t      = 6.5;    // 너트 홈 위 지붕 2.8mm 확보 (아래는 45° 받침)
flange_t    = 4;
endcap_t    = 3.8;    // 끝 핀 구멍(2.5) 앞 벽 1.3mm
L_in        = 81.2;   // endcap_t 를 늘린 만큼 줄여 전체 길이 L(85) 유지
L           = endcap_t + L_in;   // 관 끝 = 모터 감속기 앞면
narrow      = 16;     // 출구 쪽은 레일 없이 좁게 (네 모듈이 컵 위에서 모이도록)
outlet_w    = 13;
outlet_len  = 12;
tip_d       = 5;
tip_hole_d  = 2.5;    // 끝 핀 구멍 깊이 (막힌 구멍 — 앞으로 가루가 안 샘)
collar_y    = 55;
collar_od   = 33;     // 호퍼 슬리브가 씌워지는 지름
collar_wall = 2;
collar_h    = 15;
shoulder_d  = 41;     // 칼라 아래 턱 (호퍼가 얹힘)
powder_shoulder_t = 2;  // 턱 두께 (호퍼 높이 계산에도 씀)
screw_y     = [25, 78];
screw_x     = (core_hw + rail_hw) / 2;
wing_x      = 25;     // 앞 날개 볼트 (레일 밖이라 위에서 드라이버가 들어감)
wing_w      = 31;

// ---- 모터 받침 ----
gear_fit  = jga_gear_d/2 + 0.1;          // 받침·띠 구멍 반지름
split_dz  = 1.0;                          // 받침 윗면을 축보다 낮춘 양
squeeze   = 0.4;                          // 띠 구멍 중심을 축보다 낮춘 양 → 조이면 약 0.3mm 누름
sad_hw    = 24;
sad_len   = jga_gear_len;
strap_w   = 3;
strap_x   = gear_fit + strap_w + 3.7;
strap_y   = L + sad_len/2;
z_split   = axis_h - split_dz;
powder_bolt_len = 12;   // 띠 볼트 M3x12
powder_nut_drop = 8;    // 받침 윗면 → 너트 주머니 아랫면

// ---- 스크류 길이 ----
hub_d       = 12;
powder_hub_gap = 0.5;   // 스크류 허브 끝 ↔ 모터 돌기 틈
hub_hole    = jga_shaft_len - jga_boss_h - powder_hub_gap + 1.5;   // 축보다 1.5mm 깊게
hub_len     = hub_hole + 1;
tip_len     = tip_hole_d - 0.5;
auger_y_end = L - jga_boss_h - powder_hub_gap;
flight_len  = auger_y_end - hub_len - (endcap_t + 0.5);

// ---- 호퍼 ----
hop_sleeve_h = collar_h - 2;   // 칼라 끝까지 덮음 → 깔때기가 칼라 안쪽과 이어짐
hop_bot_id   = collar_od - 2*collar_wall;   // 칼라 안쪽과 같음
hop_top_id   = 70;                          // ★ 가루통 바닥에 뚫을 구멍 지름
hop_wall     = 2;
hop_cone_h   = (hop_top_id - hop_bot_id)/2 * tan(60);
hop_flange_d = 80;
hop_flange_t = 3;

function powder_deck_holes() = [[-wing_x, narrow + 5], [wing_x, narrow + 5]];      // 상판 핀 2개
pin_at = [[-screw_x, screw_y[0]], [screw_x, screw_y[1]]];                              // 위·아래 관 맞춤 핀 2개 (대각선)
function powder_collar_y() = collar_y;
function powder_collar_top() = axis_h + tube_od/2 + collar_h;
function powder_hopper_top() = axis_h + tube_od/2 + powder_shoulder_t + hop_sleeve_h + hop_cone_h + hop_flange_t;
function powder_outlet_rect() = [-outlet_w/2, outlet_w/2, endcap_t, endcap_t + outlet_len];
function powder_motor_rear_y() = L + jga_len;
function powder_tube_id() = tube_id;        // 쿠폰 고리가 실제 관과 같게

module bore(y0, y1, d, zc = axis_h) {
    translate([0, y0, zc]) rotate([-90, 0, 0]) cylinder(d = d, h = y1 - y0);
}

// 네 모듈이 컵 위에서 X자로 모이므로, 각 모듈은 자기 90° 구역 안에만 (옆 모듈과 1.2mm 틈)
wedge_gap = 0.6;
module own_sector() {
    v = -powder_d + wedge_gap * sqrt(2);
    translate([0, 0, -1]) linear_extrude(200) polygon([[0, v], [400, 400 + v], [-400, 400 + v]]);
}

module powder_block() intersection() {
    own_sector();
    difference() {
        union() {
            translate([-core_hw, 0, 0]) cube([2*core_hw, L, axis_h]);
            for (s = [-1, 1]) mirror([s < 0 ? 1 : 0, 0, 0]) hull() {
                translate([core_hw - 0.01, narrow, axis_h - rail_t - (rail_hw - core_hw)]) cube([0.01, L - narrow, rail_t + rail_hw - core_hw]);
                translate([rail_hw - 0.01, narrow, axis_h - rail_t]) cube([0.01, L - narrow, rail_t]);
            }
            for (s = [-1, 1]) mirror([s < 0 ? 1 : 0, 0, 0]) translate([core_hw, narrow, 0]) cube([wing_w - core_hw, 10, 4]);
            translate([-sad_hw, L, 0]) cube([2*sad_hw, sad_len, z_split]);                 // 모터 받침
        }
        bore(endcap_t, L + 0.01, tube_id);
        bore(L, L + sad_len + 1, 2*gear_fit);
        bore(endcap_t - tip_hole_d, endcap_t + 0.01, tip_d + 2*clear);                     // 막힌 핀 구멍
        translate([-outlet_w/2, endcap_t, -1]) cube([outlet_w, outlet_len, axis_h + 1]);
        for (p = pin_at) translate([p[0], p[1], axis_h - 3.5]) cylinder(d = pin_hole, h = 4);   // 막힌 핀 구멍
        for (sx = [-1, 1]) mirror([sx < 0 ? 1 : 0, 0, 0]) {
            translate([strap_x, strap_y, z_split - powder_bolt_len]) cylinder(d = m3_hole, h = powder_bolt_len + 1);
            translate([strap_x, strap_y, z_split - powder_nut_drop]) m3_nut_slot(sad_hw - strap_x + 1);
        }
        for (p = powder_deck_holes()) translate([p[0], p[1], -1]) cylinder(d = pin_hole, h = 6);
    }
}

module powder_top() {
    difference() {
        union() {
            intersection() {
                bore(0, L, tube_od);
                translate([-tube_od, -1, axis_h]) cube([2*tube_od, L + 2, tube_od]);
            }
            for (s = [-1, 1]) mirror([s < 0 ? 1 : 0, 0, 0]) translate([10, narrow, axis_h]) cube([rail_hw - 10, L - narrow, flange_t]);
            translate([0, collar_y, axis_h]) cylinder(d = collar_od, h = tube_od/2 + collar_h);
            // 호퍼가 얹히는 턱 (아래는 45° 경사 → 서포트 없음)
            translate([0, collar_y, axis_h + tube_od/2 - (shoulder_d - collar_od)/2]) {
                cylinder(d1 = collar_od, d2 = shoulder_d, h = (shoulder_d - collar_od)/2);
                translate([0, 0, (shoulder_d - collar_od)/2 - 0.01]) cylinder(d = shoulder_d, h = powder_shoulder_t);
            }
        }
        translate([0, endcap_t, axis_h]) rotate([-90, 0, 0])
            linear_extrude(L + 1 - endcap_t) rotate(180) teardrop_flat2d(tube_id, 1.2);
        bore(endcap_t - tip_hole_d, endcap_t + 0.01, tip_d + 2*clear);
        translate([0, collar_y, axis_h - 1]) cylinder(d = collar_od - 2*collar_wall, h = tube_od + collar_h);
        for (p = pin_at) translate([p[0], p[1], axis_h - 1]) cylinder(d = pin_hole, h = flange_t + 2);
    }
}

// 모터 덮개 띠 (조립 위치로 모델링). 구멍 중심이 축보다 squeeze 만큼 낮음 → 조이면 누름.
module powder_strap() {
    difference() {
        union() {
            intersection() {
                bore(L + 2, L + sad_len - 2, 2*(gear_fit + strap_w), axis_h - squeeze);
                translate([-sad_hw, L, z_split]) cube([2*sad_hw, sad_len, gear_fit + strap_w + 2]);
            }
            translate([-sad_hw, L + 2, z_split]) cube([2*sad_hw, sad_len - 4, 4]);
        }
        bore(L, L + sad_len + 1, 2*gear_fit, axis_h - squeeze);
        for (sx = [-1, 1]) translate([sx * strap_x, strap_y, z_split - 1]) cylinder(d = m3_hole, h = 6);
    }
}

// 호퍼 (조립 위치로 모델링): 칼라에 씌우는 슬리브 → 60° 깔때기 → 가루통 받침 테두리
module powder_hopper() {
    z0 = axis_h + tube_od/2 + powder_shoulder_t;     // 턱 위
    translate([0, collar_y, z0]) difference() {
        union() {
            cylinder(d = collar_od + 2*clear + 2*hop_wall, h = hop_sleeve_h);
            translate([0, 0, hop_sleeve_h - 0.01]) cylinder(d1 = collar_od + 2*clear + 2*hop_wall, d2 = hop_top_id + 2*hop_wall / sin(60), h = hop_cone_h);
            translate([0, 0, hop_sleeve_h + hop_cone_h - 0.02]) cylinder(d = hop_flange_d, h = hop_flange_t);
        }
        translate([0, 0, -1]) cylinder(d = collar_od + 2*clear, h = hop_sleeve_h + 1.01);
        translate([0, 0, hop_sleeve_h - 0.02]) cylinder(d1 = hop_bot_id, d2 = hop_top_id, h = hop_cone_h + 0.03);
        translate([0, 0, hop_sleeve_h + hop_cone_h - 0.5]) cylinder(d = hop_top_id, h = hop_flange_t + 1);
    }
}

// 스크류: 출력 방향(모터 쪽이 아래)으로 만듦. z=0 이 모터 쪽 끝. 1줄 나선.
module auger(od = auger_od) {      // od: 쿠폰에서 틈별 조각을 만들 때만 바꿈
    difference() {
        union() {
            cylinder(d = hub_d, h = hub_len);
            translate([0, 0, hub_len - 0.01]) {
                cylinder(d = auger_core, h = flight_len + 0.5 + 0.02);
                intersection() {
                    cylinder(d = od, h = flight_len);
                    linear_extrude(height = flight_len, twist = 360 * flight_len / auger_pitch,
                                   slices = ceil(flight_len * 2))
                        translate([0, -auger_blade/2]) square([od/2 + 1, auger_blade]);
                }
            }
            translate([0, 0, hub_len + flight_len + 0.5]) cylinder(d = tip_d, h = tip_len);
        }
        translate([0, 0, -0.01]) linear_extrude(hub_hole) dshaft_jga2d(jga_d_clear);
    }
}

module auger_placed() {
    translate([0, auger_y_end, axis_h]) rotate([90, 0, 0]) auger();
}

// 모터 모형 (검사용)
module jga_ghost() {
    bore(L, L + jga_gear_len, jga_gear_d, axis_h - 0.1);           // 받침 바닥에 얹힘
    bore(L + jga_gear_len, L + jga_len, jga_motor_d, axis_h - 0.1);
    translate([0, L, axis_h - 0.1]) rotate([90, 0, 0]) {
        cylinder(d = jga_boss_d, h = jga_boss_h);
        linear_extrude(jga_shaft_len) dshaft_jga2d(0);
    }
}

module powder_module() {
    color("Tan") powder_block();
    color("Wheat", 0.8) powder_top();
    color("BurlyWood") powder_strap();
    color("Khaki", 0.8) powder_hopper();
    color("Peru") auger_placed();
    %jga_ghost();
}

hz0 = axis_h + tube_od/2 + powder_shoulder_t;
if      (part == "block")  powder_block();
else if (part == "top")    powder_top();
else if (part == "strap")  translate([0, 0, L + sad_len - 2]) rotate([-90, 0, 0]) translate([0, 0, -z_split]) powder_strap();
else if (part == "hopper") translate([0, 0, hop_sleeve_h + hop_cone_h + hop_flange_t]) rotate([180, 0, 0]) translate([0, -collar_y, -hz0]) powder_hopper();   // 테두리를 바닥에
else if (part == "auger")  auger();
else if (part == "module") powder_module();
