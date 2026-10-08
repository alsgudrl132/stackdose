// =====================================================================
// 전체 조립 미리보기 + 겹침 검사용 배치 (8칸)
// ---------------------------------------------------------------------
// OpenSCAD 에서 이 파일을 "파일 → 열기"로 여세요 (복사해 붙이면 include 를 못 찾음).
// show = "all"   : 전체 조립 (F5)
// show = 부품 이름 : 그 부품만 조립 위치에 (check.py 가 씀)
// =====================================================================
include <config.scad>
include <lib.scad>
include <layout.scad>
use <powder.scad>
use <pill.scad>
use <scale.scad>
use <electronics.scad>
use <frame.scad>

show = "all";
bin_w = 85;       // ★ 가루통 바닥 한 변 (다이소 용기)
bin_h = 150;      // ★

lift_out = 4.5;
module cup_sweep(xy, z0) {
    hull() { cup_ghost(xy, z0 + 0.6); cup_ghost(xy, z0 + lift_out); }
    hull() { cup_ghost(xy, z0 + lift_out); cup_ghost(add2(xy, [0, -150]), z0 + lift_out); }
}

module piece(name) {
    if (name == "baseP")  baseP();
    if (name == "deckP")  deckP();
    if (name == "baseL")  baseL();
    if (name == "deckL")  deckL();
    if (name == "postsP") for (p = postsP) translate([p[0], p[1], 0]) post();
    if (name == "postsL") for (p = postsL) translate([p[0], p[1], 0]) post();
    for (i = [0:3]) {
        if (name == str("powder", i))  at_powder(i) { powder_block(); powder_top(); powder_strap(); }
        if (name == str("hopper", i))  at_powder(i) powder_hopper();
        if (name == str("auger", i))   at_powder(i) auger_placed();
        if (name == str("motor", i))   at_powder(i) jga_ghost();
        if (name == str("bin", i))     at_powder(i) translate([0, powder_collar_y(), powder_hopper_top()])
                                           rotate(-(powder_a[i] - 90)) translate([-bin_w/2, -bin_w/2, 0]) cube([bin_w, bin_w, bin_h]);
        if (name == str("pill", i))    at_pill(i) { pill_skirt(); pill_floor(); }
        if (name == str("disk", i))    at_pill(i) translate([0, 0, pill_disk_z()]) rotate(pill_rest_a()) pill_disk();
        if (name == str("pspacer", i)) at_pill(i) translate([0, 0, pill_well_z()]) pill_spacer();
        if (name == str("hall", i))    at_pill(i) hall_ghost();
        if (name == str("pilltop", i)) at_pill(i) translate([0, 0, pill_ledge_z()]) pill_cover();
        if (name == str("byj", i))     at_pill(i) byj_ghost(pill_rest_a());
    }
    if (name == "scale")    { pedestal(); tray(); spacers_placed(); }
    if (name == "loadcell") loadcell_ghost();
    if (name == "cupP")     cup_ghost(cupP, cup_z_powder());
    if (name == "cupL")     cup_ghost(cupL, 0);
    // 컵 꺼내는 길: 4.5mm 들어 올린 뒤 앞(-Y)으로 150mm
    if (name == "sweepP")   cup_sweep(cupP, cup_z_powder());
    if (name == "sweepL")   cup_sweep(cupL, 0);
    if (name == "ctrl")     ctrl_placed();
}

if (show == "all") {
    color("Beige") { piece("baseP"); piece("baseL"); }
    color("Beige", 0.7) { piece("deckP"); piece("deckL"); }
    color("Linen") { piece("postsP"); piece("postsL"); }
    for (i = [0:3]) {
        color("Tan") piece(str("powder", i));
        color("Khaki", 0.7) piece(str("hopper", i));
        color("Peru") piece(str("auger", i));
        color("SteelBlue") piece(str("pill", i));
        color("Gold") piece(str("disk", i));
        color("Orange") piece(str("pspacer", i));
        color("White", 0.5) piece(str("pilltop", i));
        %piece(str("motor", i)); %piece(str("byj", i)); %piece(str("bin", i)); %piece(str("hall", i));
    }
    color("DimGray") piece("scale");
    color("SlateGray") piece("ctrl");
    %piece("loadcell"); %piece("cupP"); %piece("cupL");
} else {
    piece(show);
}
