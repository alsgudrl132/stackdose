// =====================================================================
// 뼈대: 스테이션마다 바닥판 · 상판, 공통 기둥
//   가루 스테이션(P): 210×210, 기둥 7개
//   알약 스테이션(L): 205×205, 기둥 7개 + 미끄럼관 4개가 상판에 붙어 있음
//   앞쪽(-Y)은 컵을 꺼내는 길이라 가루 쪽 기둥이 없음
// 전역 좌표 (원점 = 바닥판 윗면 높이)
// 나사 없음: 기둥은 양 끝 네모 돌기를 판 구멍에 끼우고, 상판은 기둥 위에 얹음.
//            모듈은 상판의 핀 구멍에 핀을 넣고 얹음.
// =====================================================================
include <config.scad>
include <lib.scad>
include <layout.scad>
use <powder.scad>
use <pill.scad>
use <scale.scad>
use <electronics.scad>

part = "baseP";   // "baseP" | "deckP" | "baseL" | "deckL" | "post" | "pins" | "pegtest"

motor_wire_r = 128;   // 가루 모터 전선 구멍 (컵 중심에서 대각선 거리, 모터 몸통 아래)
frame_wire_hole = [20, 12];   // 알약 상판 전선 구멍: 28BYJ 커넥터가 꽂힌 채 통과 (+홀 센서 선)
assert(frame_wire_hole[0] >= byj_conn_w + 2 && frame_wire_hole[1] >= byj_conn_t + 2, "알약 상판 전선 구멍이 28BYJ 커넥터보다 작음");
peg_off = -post_w/2 + peg_w/2;   // 돌기는 기둥 한쪽 면에 붙어 있음 (눕혀서 출력할 때 바닥에 닿게)

// 기둥: 조립 위치로 모델링 (z 0 ~ deck_z)
module post() {
    translate([-post_w/2, -post_w/2, 0]) cube([post_w, post_w, deck_z]);
    for (z = [-peg_h, deck_z]) translate([peg_off - peg_w/2, -peg_w/2, z - 0.01 * sign(z)]) cube([peg_w, peg_w, peg_h + 0.01]);
}
module peg_holes(posts, z0, t) for (p = posts) translate([p[0] + peg_off - peg_hole/2, p[1] - peg_hole/2, z0 - 1]) cube([peg_hole, peg_hole, t + 2]);

// 핀 구멍 (위에서 3mm 막힌 구멍)
module pin_holes(pts, ztop) for (p = pts) translate([p[0], p[1], ztop - 3]) cylinder(d = pin_hole, h = 4);

module plate(center, size, z0, t) translate([center[0] - size[0]/2, center[1] - size[1]/2, z0]) cube([size[0], size[1], t]);

// 케이블 타이 구멍 한 쌍 (a = 전선 방향)
module tie_pair(p, a, z0, t) translate([p[0], p[1], z0 - 1]) rotate(a)
    for (s = [-1, 1]) translate([-1.5, s * 5 - 1, 0]) cube([3, 2, t + 2]);

module baseP() difference() {
    union() { plate(cupP, sizeP, -base_t, base_t); powder_boards(); }
    peg_holes(postsP, -base_t, base_t);
    pin_holes(scale_base_holes(), 0);
    powder_boards(true);
    // 로드셀 전선 → HX711 → 뒤쪽 가장자리
    for (p = [[-75, 30], [0, 85], [60, 85]]) tie_pair(add2(cupP, p), 0, -base_t, base_t);
}

module baseL() difference() {
    union() {
        plate(cupL, sizeL, -base_t, base_t);
        pill_boards();
        translate([cupL[0], cupL[1], -0.01]) difference() {       // 알약 컵 받침 링
            cylinder(d = cup_d_at(4) + 2*clear + 4, h = 4);
            translate([0, 0, -1]) cylinder(d = cup_d_at(4) + 2*clear, h = 6);
        }
    }
    peg_holes(postsL, -base_t, base_t);
    pill_boards(true);
    // ULN → MCP 점퍼 다발, 뒤쪽 가장자리로
    for (p = [[-35, 40], [35, 40], [-40, 88], [40, 88]]) tie_pair(add2(cupL, p), 0, -base_t, base_t);
}

module deck_body(center, size, notch = 0) {
    plate(center, size, deck_z, deck_t);
    translate([0, 0, deck_z - rim_h]) difference() {
        plate(center, size, 0, rim_h + 0.01);
        plate(center, [size[0] - 2*rim_w, size[1] - 2*rim_w], -1, rim_h + 2);
        if (notch > 0)     // 앞 테두리 홈: 컵을 들어서 앞으로 뺄 때 지나가는 길
            translate([center[0] - notch/2, center[1] - size[1]/2 - 1, -1]) cube([notch, rim_w + 2, rim_h + 2]);
    }
}

module deckP() difference() {
    deck_body(cupP, sizeP, cup_top_d + 12);
    peg_holes(postsP, deck_z, deck_t);
    pin_holes([for (i = [0:3], p = powder_deck_holes()) powder_xy(p, i)], deck_top);
    // 가루 낙하 구멍 4개 (출구마다)
    r = powder_outlet_rect();
    translate([0, 0, deck_z - 1]) linear_extrude(deck_t + 2)
        for (i = [0:3]) translate(cupP) rotate(powder_a[i] - 90) translate([0, powder_d])
            translate([r[0] - 1.5, r[2] - 1.5]) square([r[1] - r[0] + 3, r[3] - r[2] + 3]);
    // 모터 전선 구멍 (모터 몸통 바로 아래)
    for (i = [0:3]) translate([0, 0, deck_z - 1])
        translate(add2(cupP, rot2([motor_wire_r, 0], powder_a[i]))) cylinder(d = 9, h = deck_t + 2);
}

module deckL() difference() {
    union() {
        deck_body(cupL, sizeL);
        for (i = [0:3]) at_slide(i) pill_slide_solid();       // 미끄럼관 (상판과 한 덩어리)
    }
    for (i = [0:3]) at_slide(i) pill_slide_hole();
    peg_holes(postsL, deck_z, deck_t);
    pin_holes([for (i = [0:3], p = pill_deck_holes()) pill_xy(p, i)], deck_top);
    translate([0, 0, deck_z - 1]) linear_extrude(deck_t + 2) for (i = [0:3]) {
        // 전선 구멍: 28BYJ-48 커넥터(실측 15×5.5)가 꽂힌 채로 + 홀 센서 선 3가닥
        translate(pill_xy(pill_wire_xy(), i)) rotate(pill_phi[i] + 90) square(frame_wire_hole, center = true);
    }
}

// 핀: 한 판에 모아서 출력 (가루 4×(상판 2 + 관 2) + 알약 4×2 + 저울 2 = 26개, 여분 4)
module pins() for (i = [0:29]) translate([(i % 6) * 8, floor(i / 6) * 8, 0]) cylinder(d = pin_d, h = pin_len);

// 기둥 돌기 시험 조각: 큰 판을 뽑기 전에 기둥 돌기가 판 구멍에 맞는지 확인.
// 구멍은 바닥판·상판과 같은 peg_holes() 로 뚫음 (숫자를 따로 적지 않음)
frame_pegtest_w = 18;
module pegtest() difference() {
    translate([-frame_pegtest_w/2, -frame_pegtest_w/2, 0]) cube([frame_pegtest_w, frame_pegtest_w, base_t]);
    peg_holes([[-peg_off, 0]], 0, base_t);
}

if      (part == "baseP") baseP();
else if (part == "baseL") baseL();
else if (part == "deckP") translate([0, 0, deck_top]) rotate([180, 0, 0]) deckP();   // 뒤집어 출력
else if (part == "deckL") translate([0, 0, deck_top]) rotate([180, 0, 0]) deckL();
else if (part == "post")  translate([0, 0, post_w/2]) rotate([0, -90, 0]) post();      // 눕혀서 출력 (돌기가 바닥 쪽)
else if (part == "pins")  pins();
else if (part == "pegtest") pegtest();
