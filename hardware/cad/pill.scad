// =====================================================================
// 알약 모듈: 칸 3개짜리 회전 원판 + 28BYJ-48 + 원점 홀 센서
// ---------------------------------------------------------------------
// 로컬 좌표: 모터 축이 원점, z=0 은 상판 윗면. 출구는 +Y(90°) 방향.
// 원판이 120°씩 돌 때마다 한 알. 대기 위치: 칸이 30°·150°·270° (출구와 겹치지 않음).
// 출력 부품:
//   pill_skirt()  모터가 들어가는 치마 + 낙하관 (그대로 세워 출력)
//   pill_floor()  바닥 + 우물 + 덮개 턱 (그대로 출력)
//   pill_disk()   원판 (뒤집어 출력: 윗면이 바닥)
//   pill_cover()  덮개 + 호퍼
//   pill_spacer() 받침판 (얇은 알약일 때만. 원판과 함께 알약마다 뽑음)
//   (미끄럼관은 알약 상판에 붙어서 같이 출력됨 → frame.scad)
// =====================================================================
include <config.scad>
include <lib.scad>

part = "skirt";  // "skirt" | "floor" | "disk" | "cover" | "spacer" | "module"

pockets  = 3;
// 몸체(출구·낙하관·우물·덮개 창·미끄럼관)는 최대 알약 기준
slot_L   = pill_max_l + 1.8;      // 캡슐 길이 편차(±0.5) + 여유
slot_W   = pill_max_w + 1.0;
disk_t_max = pill_max_t + 0.8;     // 우물 깊이를 정하는 원판 최대 두께
// 원판 칸·두께는 칸에 넣을 알약 기준 → 정확히 한 알만 들어감
pocket_L = pill_l + 1.8;
pocket_W = pill_w + 1.0;
pill_fit_t = pill_t + 0.8;
// 얇은 알약은 원판을 얇게 뽑고 아래에 받침판을 깔아 원판 윗면 높이를 맞춤 (덮개 틈 유지)
pill_spacer_t = (disk_t_max - pill_fit_t >= 1) ? disk_t_max - pill_fit_t : 0;
disk_t   = disk_t_max - pill_spacer_t;
assert(pill_l <= pill_max_l && pill_w <= pill_max_w && pill_t <= pill_max_t, "칸에 넣을 알약이 최대 알약보다 큼");
// 한 칸에 한 알만: 두 알이 겹쳐 통째로 들어가거나, 세워진 두 알이 나란히 들어가면 안 됨
assert(disk_t < 2*pill_t - 0.3, "원판이 두꺼워 알약 두 알이 겹쳐 들어감");
assert(!(disk_t >= pill_w && pocket_W >= 2*pill_t), "세운 알약 두 알이 칸에 나란히 들어감");
pocket_r = 27;                     // 칸 중심 반지름 (대기 시 출구와 6° 이상 떨어지도록)
slot_far = sqrt(pow(pocket_r, 2) + pow((slot_L - slot_W)/2, 2)) + slot_W/2;
disk_d   = 2*(slot_far + 3);
hub_d    = 10;
out_a    = 90;                     // 출구 각도
rest_a   = 30;                     // 대기 시 0번 칸 각도
out_L    = slot_L + 2;             // 출구 구멍 (칸보다 1mm씩 큼)
out_W    = slot_W + 2;

floor_t  = 5;
skirt_h  = byj_body_h + 5;
gap_bot  = 0.5;                    // 원판 아래 틈
gap_top  = 1.5;                    // 원판 위 ↔ 덮개 (둘째 알약은 7mm 이상 튀어나와 긁힘)
well_h   = disk_t_max + gap_bot + gap_top;
well_d   = disk_d + 2;
cover_d  = well_d + 2.4;
pill_rim_h = 2;                    // 덮개 턱 테두리 (config 의 상판 rim_h 와 다른 값)
pill_rim_w = 1.6;
pill_mag_fit = 0.3;                // 자석 자리 지름 여유 (자석 오면 쿠폰 C줄 1·2번에 넣어 보고 조정)
base_d   = cover_d + 2*clear + 2*pill_rim_w;
skirt_w  = 2.4;
cover_t  = 2;
hopper_h = 70;                     // ★ 한 달 치가 들어가는지 확인
key_w    = 6;
chute_w  = 1.6;
win_a0   = out_a + 75;
win_a1   = out_a + 285;
tab_a    = [30, 210];              // 상판 핀 날개 2개 (마주 보게 → 돌지 않음, 전선 창 270° 를 피함)
tab_r    = base_d/2 + 5;
// 치마 ↔ 바닥: 나사 없이 턱에 얹음. 치마 윗면 안쪽 턱 + 돌림 방지 키, 바닥 아랫면에 맞는 홈
lip_r0   = base_d/2 - skirt_w;     // 턱 안쪽 반지름 (= 치마 안쪽 벽)
lip_w    = 1.2;
lip_h    = 2;
lip_key_a = 150;                   // 키 위치 (다른 것과 안 겹치는 곳)
win_w    = 24;  win_h = 14;        // 전선 창 (28BYJ-48 커넥터가 꽂힌 채 통과)
assert(win_w >= byj_conn_w + 2 && win_h >= byj_conn_t + 2, "치마 전선 창이 28BYJ 커넥터보다 작음");
mag_r    = 27.5;  mag_a = 350;     // 원점 자석 (대기 상태에서의 각도·반지름)
hub_down = floor_t - 2 + pill_spacer_t;   // 허브 아랫끝 높이는 받침판과 상관없이 같음 (모터 축에 물림)
pill_key_a = 180;                  // 받침판 돌림 방지 키 (출구 90°, 자석 350°, 덮개 키 0° 를 피함)

z_floor  = skirt_h;
z_well   = skirt_h + floor_t;
z_ledge  = z_well + well_h;
z_disk   = z_well + gap_bot + pill_spacer_t;   // 원판 아랫면

function pill_deck_holes() = [for (a = tab_a) [tab_r*cos(a), tab_r*sin(a)]];
function pill_outlet_xy()  = [pocket_r*cos(out_a), pocket_r*sin(out_a)];
function pill_wire_xy()    = [0, -(base_d/2 - 10)];
function pill_ledge_z()    = z_ledge;
function pill_disk_z()     = z_disk;
function pill_well_z()     = z_well;
function pill_rest_a()     = rest_a;
function pill_base_r()     = base_d/2;

echo(str("알약 원판 지름 = ", disk_d, ", 모듈 지름 = ", base_d, ", 원판 두께 = ", disk_t, ", 받침판 = ", pill_spacer_t));

module out_slot2d(L = out_L, W = out_W) translate(pill_outlet_xy()) rotate(out_a) slot2d(L, W);
module pockets2d(rot, L = slot_L, W = slot_W)
    for (i = [0 : pockets - 1]) rotate(rot + i * 360/pockets) translate([pocket_r, 0]) slot2d(L, W);

// 대기 위치에서 칸과 출구가 겹치지 않는지 (check.py 가 씀)
module rest_overlap_check() intersection() { linear_extrude(1) pockets2d(rest_a); linear_extrude(1) out_slot2d(); }

module pill_skirt() {
    difference() {
        union() {
            difference() {
                cylinder(d = base_d, h = skirt_h);
                translate([0, 0, -1]) cylinder(d = base_d - 2*skirt_w, h = skirt_h + 2);
            }
            linear_extrude(skirt_h) difference() {           // 낙하관
                offset(r = chute_w) out_slot2d();
                out_slot2d();
            }
            for (s = [-1, 1]) translate([s * 9 - 2, pocket_r + out_W/2, 0])   // 낙하관을 치마 벽에 붙이는 살
                cube([4, base_d/2 - pocket_r - out_W/2 - 0.5, skirt_h]);
            for (a = tab_a)   rotate(a) translate([base_d/2 - 2, -6, 0]) cube([12, 12, 4]);
            translate([0, 0, skirt_h - 0.01]) lip_ring(0);
        }
        translate([0, 0, -1]) linear_extrude(skirt_h + 2) out_slot2d();
        translate([-win_w/2, -base_d/2 - 1, -1]) cube([win_w, skirt_w + 2, win_h + 1]);   // 전선 창
        for (p = pill_deck_holes()) translate([p[0], p[1], -1]) cylinder(d = pin_hole, h = 6);
    }
}

// 턱 고리 + 키 (g = 한쪽 여유: 0 이면 치마 턱, clear 면 바닥 홈)
module lip_ring(g) {
    h = lip_h + (g > 0 ? 0.4 : 0);
    difference() {
        cylinder(r = lip_r0 + lip_w + g, h = h);
        translate([0, 0, -1]) cylinder(r = lip_r0 - g, h = h + 2);
    }
    rotate(lip_key_a) translate([lip_r0 - g, -(4 + 2*g)/2, 0]) cube([skirt_w - 0.6 + 2*g, 4 + 2*g, h]);
}

module pill_floor() {
    difference() {
        union() {
            translate([0, 0, z_floor]) cylinder(d = base_d, h = floor_t + well_h + pill_rim_h);
        }
        translate([0, 0, z_floor - 0.01]) lip_ring(clear);                                  // 치마 턱이 들어가는 홈
        translate([0, 0, z_well]) cylinder(d = well_d, h = well_h + 1);
        translate([0, 0, z_ledge]) cylinder(d = cover_d + 2*clear, h = pill_rim_h + 1);
        translate([0, 0, z_floor - 1]) cylinder(d = hub_d + 2*clear, h = floor_t + 2);
        translate([0, 0, z_floor - 1]) linear_extrude(floor_t + 2) out_slot2d();
        // 모터 귀: 관통 구멍 + 윗면(우물 쪽) 너트 주머니 → 아래에서 M3x5 로 조임
        for (s = [-1, 1]) translate([s * byj_ear_span/2, -byj_shaft_off, 0]) {
            translate([0, 0, z_floor - 1]) cylinder(d = m3_hole, h = floor_t + 2);
            translate([0, 0, z_well - m3_nut_t - 0.8]) m3_nut_pocket(m3_nut_t + 0.81);   // 0.8 깊게 → M3x5 끝이 원판에 안 닿음
        }
        // 홀 센서 자리: 아래에서 파서 바닥을 1.2mm 만 남김 (자석과 1.7mm)
        // 센서 납작한 면(글씨 면)이 위. 다리+단선은 바깥쪽 홈을 따라 치마 벽까지
        rotate(mag_a) translate([mag_r, 0, z_floor - 0.01]) {
            translate([-(hall_l + 0.6)/2, -(hall_w + 0.6)/2, 0]) cube([hall_l + 0.6, hall_w + 0.6, floor_t - 1.2]);
            translate([0, -3.5, 0]) cube([lip_r0 - mag_r - 1, 7, 1.8]);
        }
        translate([cover_d/2 - 1, -key_w/2, z_ledge]) cube([pill_rim_w + clear + 2, key_w, pill_rim_h + 1]);
        // 받침판 돌림 방지 키 홈 (원판 윗면보다 낮아서 알약이 빠질 틈은 없음)
        rotate(pill_key_a) translate([well_d/2 - 1, -key_w/2, z_well - 0.01]) cube([3, key_w, disk_t_max]);
    }
}

// 받침판: 얇은 알약일 때 우물 바닥에 깔아 원판 윗면 높이를 맞춤. 출구 구멍은 바닥과 같은 자리 (키로 맞춤)
module pill_spacer() {
    if (pill_spacer_t > 0) difference() {
        union() {
            cylinder(d = well_d - 2*clear, h = pill_spacer_t);
            rotate(pill_key_a) translate([well_d/2 - 1.5, -(key_w - 2*clear)/2, 0]) cube([3.5 - clear, key_w - 2*clear, pill_spacer_t]);
        }
        translate([0, 0, -1]) cylinder(d = hub_d + 2*clear + 1, h = pill_spacer_t + 2);
        translate([0, 0, -1]) linear_extrude(pill_spacer_t + 2) out_slot2d();
    }
}

// 원판: 로컬 z=0 이 원판 아랫면. 대기 각도로 돌려서 씀.
d_from = (byj_boss_h + byj_shaft_len - byj_flat_len) - (floor_t + gap_bot + pill_spacer_t);   // 축 D컷이 시작되는 높이
module pill_disk() {
    difference() {
        union() {
            cylinder(d = disk_d, h = disk_t);
            translate([0, 0, -hub_down]) cylinder(d = hub_d, h = hub_down + 0.01);
        }
        // 칸(칸에 넣을 알약 크기) + 윗면 1mm 모따기 (반쯤 걸친 알약이 끼지 않게)
        translate([0, 0, -1]) linear_extrude(disk_t + 2) pockets2d(0, pocket_L, pocket_W);
        for (i = [0 : pockets - 1]) rotate(i * 360/pockets) translate([pocket_r, 0, disk_t - 1]) hull() {
            linear_extrude(0.01) slot2d(pocket_L, pocket_W);
            translate([0, 0, 1]) linear_extrude(0.02) slot2d(pocket_L + 2, pocket_W + 2);
        }
        // 축: 아래는 둥근 구멍, D컷 구간만 D자
        translate([0, 0, -hub_down - 1]) cylinder(d = byj_shaft_d + 2*clear, h = hub_down + 1 + d_from);
        translate([0, 0, d_from]) linear_extrude(disk_t + hub_down) dshaft_byj2d(byj_d_clear);
        // 원점 자석 (칸 사이, 아랫면에 박음)
        rotate(mag_a - rest_a) translate([mag_r, 0, -0.01]) cylinder(d = mag_d + pill_mag_fit, h = mag_t + 0.2);
    }
}

module pill_cover() {
    band_r0 = pocket_r - slot_W/2 - 2;
    band_r1 = slot_far + 1;
    difference() {
        union() {
            cylinder(d = cover_d, h = cover_t);
            translate([cover_d/2 - 1, -(key_w - 2*clear)/2, 0]) cube([pill_rim_w + 1, key_w - 2*clear, cover_t]);
            difference() {
                cylinder(d = well_d, h = cover_t + hopper_h);
                translate([0, 0, -1]) cylinder(d = well_d - 4, h = cover_t + hopper_h + 2);
            }
        }
        translate([0, 0, -1]) linear_extrude(cover_t + 2) intersection() {
            difference() { circle(r = band_r1); circle(r = band_r0); }
            sector2d(win_a0, win_a1, disk_d);
        }
        // 긁는 모서리(창이 끝나는 쪽) 아래를 45° 로 깎음 → 알약을 끼우지 않고 눌러 넣음
        rotate(win_a1) translate([band_r0, -0.01, -0.01]) rotate([90, 0, 90])
            linear_extrude(band_r1 - band_r0) polygon([[0, 0], [1.6, 0], [0, 1.6]]);
    }
}

// ---- 상판 아래 미끄럼관: 출구 → 컵 입구 (알약 상판과 한 덩어리로 출력) ----
// 로컬 좌표: 원점 = 알약 컵 중심, +Y = 모듈 방향, z 는 전역(바닥판 윗면 기준)
slide_r_top = pill_s * sqrt(2) - pocket_r;
slide_r_bot = 22;
slide_z_top = deck_z;
slide_z_bot = 87;                         // 컵을 4mm 들어 빼도 안 닿는 높이
slide_wall  = 1.6;

module slide_rect(r, z, grow) {
    translate([0, r, z]) linear_extrude(0.01) offset(delta = grow) square([out_L, out_W], center = true);
}

module pill_slide_solid() hull() { slide_rect(slide_r_top, slide_z_top + 0.5, slide_wall); slide_rect(slide_r_bot, slide_z_bot, slide_wall); }
module pill_slide_hole()  hull() { slide_rect(slide_r_top, slide_z_top + deck_t + 1, 0); slide_rect(slide_r_bot, slide_z_bot - 1, 0); }
module pill_slide() difference() { pill_slide_solid(); pill_slide_hole(); }

// ---- 검사용 모형 ----
module byj_ghost(rot = 0) {
    translate([0, -byj_shaft_off, z_floor - byj_body_h]) cylinder(d = byj_body_d, h = byj_body_h);
    // 파란 전선 덮개: 축 반대쪽으로 튀어나옴 (높이는 몰라서 몸통 높이 전체로 크게 잡음)
    translate([-byj_cover_w/2, -byj_shaft_off - byj_cover_r, z_floor - byj_body_h]) cube([byj_cover_w, byj_cover_r, byj_body_h]);
    translate([0, 0, z_floor]) cylinder(d = byj_boss_d, h = byj_boss_h);
    translate([0, 0, z_floor + byj_boss_h]) {
        cylinder(d = byj_shaft_d, h = byj_shaft_len - byj_flat_len);
        translate([0, 0, byj_shaft_len - byj_flat_len]) rotate(rot) linear_extrude(byj_flat_len) dshaft_byj2d(0);
    }
}
module hall_ghost() rotate(mag_a) translate([mag_r, 0, z_floor + floor_t - 1.2 - hall_t - 0.05])
    translate([-hall_l/2, -hall_w/2, 0]) cube([hall_l, hall_w, hall_t]);

module pill_module(explode = 0) {
    color("SteelBlue", 0.9) { pill_skirt(); pill_floor(); }
    color("Gold") translate([0, 0, z_disk]) rotate(rest_a) pill_disk();
    color("Orange") translate([0, 0, z_well]) pill_spacer();
    color("White", 0.5) translate([0, 0, z_ledge + explode]) pill_cover();
    %byj_ghost(rest_a); %hall_ghost();
}

if      (part == "skirt")  pill_skirt();
else if (part == "floor")  translate([0, 0, -z_floor]) pill_floor();
else if (part == "disk")   translate([0, 0, disk_t]) rotate([180, 0, 0]) pill_disk();
else if (part == "cover")  pill_cover();
else if (part == "spacer") pill_spacer();
else if (part == "module") pill_module(20);
