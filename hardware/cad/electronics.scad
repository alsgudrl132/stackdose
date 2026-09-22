// =====================================================================
// 전자부품 받침
//   ctrl_plate  제어판 (알약 스테이션 뒤, 탁자 위): 만능기판 + ESP32 + DC 잭을 한 판에
//   board_tray  작은 보드 받침 (ULN2003 ×4, MCP23017 → 알약 바닥판 / HX711 → 가루 바닥판, 바닥판에 붙어 있음)
// 나사 없음: 제어판은 한 판으로 출력, 작은 보드 받침은 바닥판과 한 덩어리.
// =====================================================================
include <config.scad>
include <lib.scad>

part = "ctrl";   // "ctrl" | "uln" | "mcp" | "hx" | "all"

wall   = 2.5;
lift   = 4;      // 보드 아랫면 높이 (납땜 자국 여유)
ledge  = 1.5;    // 보드 가장자리를 받치는 턱 폭

// ---- 알약 바닥판 위 배치 (알약 컵 기준) ----
uln_rel = [[62, 62], [-62, 62], [-62, -62], [62, -62]];   // pill_phi 45,135,225,315 모듈 아래
mcp_rel = [0, 62];
hx_rel  = [-55, 55];                                      // 가루 컵 기준

// 작은 보드 받침: 바닥판과 한 덩어리로 출력. 가장자리 턱 위에 보드, 짧은 두 변은 열려 있음(커넥터·핀).
// 보드는 케이블 타이 하나로 묶음: 받침 양옆 바닥판 구멍 → 바닥판 아랫면 홈 → 보드 위.
module board_tray(w, d, t) {
    ow = w + 2*clear; od = d + 2*clear;
    difference() {
        translate([-ow/2, -od/2 - wall, 0]) cube([ow, od + 2*wall, lift + t + 1.2]);
        translate([-ow/2 - 1, -od/2, lift]) cube([ow + 2, od, t + 5]);                          // 보드 자리
        translate([-ow/2 - 1, -od/2 + ledge, 1.5]) cube([ow + 2, od - 2*ledge, lift]);            // 납땜 자국 자리
    }
}
// 바닥판에서 파낼 것 (z=0 = 바닥판 윗면)
module board_tray_cut(w, d) {
    od = d + 2*clear;
    for (s = [-1, 1]) translate([-2.5, s * (od/2 + wall + 1.5) - 1.25, -base_t - 1]) cube([5, 2.5, base_t + 2]);
    translate([-2.5, -(od/2 + wall + 3), -base_t - 0.01]) cube([5, od + 2*wall + 6, 1.6]);
}

// ---- 제어판 ----
plate_t = 3;
pb_at   = [-45, 0];       // 제어판 기준
esp_at  = [30, 0];        // ESP32 는 세로로 (USB 가 +Y = 뒤쪽 가장자리)
dcj_at  = [78, 20];       // DC 잭은 +X 가장자리로 꽂음
groove_z = plate_t + 5;   // 만능기판 아랫면 높이
groove_d = 2;
esp_h   = 30;             // ESP32 아랫면 높이: 핀(약 8) + 점퍼 암 커넥터(14) + 굽힘 여유

module pb_holder() {       // 긴 두 변 홈에 밀어 넣음 (-X 쪽으로 넣고 +X 끝에서 멈춤)
    ow = pb_w + 2*wall; od = pb_d + 2*clear;
    difference() {
        union() for (s = [-1, 1]) translate([-ow/2, s > 0 ? od/2 - groove_d : -od/2 - wall, 0])
            cube([ow, wall + groove_d, groove_z + pb_t + 2*clear + 1.5]);
        translate([-ow/2 - 1, -od/2, groove_z]) cube([ow - wall + 1, od, pb_t + 2*clear]);
        translate([-ow/2 - 1, -od/2 + groove_d, groove_z]) cube([ow + 2, od - 2*groove_d, 20]);
    }
    translate([ow/2 - wall, -od/2 - wall, 0]) cube([wall, od + 2*wall, groove_z]);   // 끝 멈춤 (보드 아래까지만)
}

module esp_cradle() {      // 짧은 두 끝만 받침, 긴 두 변은 열림 → 점퍼를 먼저 꽂고 올려놓음
    L = esp_d; W = esp_w;  // 세로로 놓음: X 폭 = esp_d, Y 길이 = esp_w
    for (s = [-1, 1]) difference() {
        translate([-L/2 - wall, s > 0 ? W/2 - 3 : -W/2 - wall, 0]) cube([L + 2*wall, 3 + wall, esp_h + esp_t + 2]);
        translate([-L/2 - clear, -W/2 - clear, esp_h]) cube([L + 2*clear, W + 2*clear, 10]);
        if (s > 0) translate([-6, W/2 - 5, esp_h - 2]) cube([12, 10, 10]);    // USB 자리
    }
}

module dcj_clamp() {
    difference() {
        union() {
            translate([-10, -(dcj_d/2 + 3), 0]) cube([20, dcj_d + 6, dcj_d/2 + 4]);
        }
        translate([-11, 0, dcj_d/2 + 4]) rotate([0, 90, 0]) cylinder(d = dcj_d + 2*clear, h = 22);
        translate([-2, -(dcj_d/2 + 4), 0.9]) cube([4, dcj_d + 8, 1.8]);   // 케이블 타이 홈
    }
}

module ctrl_plate() {
    difference() {
        translate([-ctrl_size[0]/2, -ctrl_size[1]/2, 0]) cube([ctrl_size[0], ctrl_size[1], plate_t]);
        // 케이블 타이 구멍: 제어판 앞 가장자리 (스테이션 쪽 전선 다발)
        for (x = [-70, -20, 30]) for (dx = [-5, 5]) translate([x + dx - 1.5, -ctrl_size[1]/2 + 5, -1]) cube([3, 2, plate_t + 2]);
    }
    translate([pb_at[0], pb_at[1], 0]) pb_holder();
    translate([esp_at[0], esp_at[1], plate_t - 0.01]) esp_cradle();
    translate([dcj_at[0], dcj_at[1], plate_t - 0.01]) dcj_clamp();
}

// ---- 바닥판에 붙는 받침 (frame.scad 가 씀) ----
module pill_boards(cut = false) {
    for (r = uln_rel) translate([cupL[0] + r[0], cupL[1] + r[1], 0])
        if (cut) board_tray_cut(uln_w, uln_d); else board_tray(uln_w, uln_d, uln_t);
    translate([cupL[0] + mcp_rel[0], cupL[1] + mcp_rel[1], 0])
        if (cut) board_tray_cut(mcp_w, mcp_d); else board_tray(mcp_w, mcp_d, mcp_t);
}
module powder_boards(cut = false) translate([cupP[0] + hx_rel[0], cupP[1] + hx_rel[1], 0])
    if (cut) board_tray_cut(hx_w, hx_d); else board_tray(hx_w, hx_d, hx_t);
module boards_placed() { pill_boards(); powder_boards(); }
module ctrl_placed() translate([ctrl_c[0], ctrl_c[1], -base_t]) ctrl_plate();

module electronics_all() {
    boards_placed();
    ctrl_placed();
}

if      (part == "ctrl") ctrl_plate();
else if (part == "uln")  board_tray(uln_w, uln_d, uln_t);
else if (part == "mcp")  board_tray(mcp_w, mcp_d, mcp_t);
else if (part == "hx")   board_tray(hx_w, hx_d, hx_t);
else if (part == "all")  electronics_all();
