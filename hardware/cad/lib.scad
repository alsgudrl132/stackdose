// 공통 도형. include <config.scad> 뒤에 include 하세요.

module slot2d(L, W) {           // 긴 방향이 Y인 둥근 직사각형
    hull() {
        translate([0, -(L - W)/2]) circle(d = W);
        translate([0,  (L - W)/2]) circle(d = W);
    }
}

module sector2d(a0, a1, R) {
    polygon(concat([[0, 0]], [for (a = [a0 : 5 : a1]) [R*cos(a), R*sin(a)]], [[R*cos(a1), R*sin(a1)]]));
}

// JGA25-370 축: 한쪽만 깎인 D컷 (깎인 면이 +X)
module dshaft_jga2d(c) {
    r = jga_shaft_d/2;
    intersection() {
        circle(d = jga_shaft_d + 2*c);
        translate([-r - c, -r - c]) square([jga_shaft_flat + 2*c, jga_shaft_d + 2*c]);
    }
}

// 28BYJ-48 축: 양쪽이 깎인 D컷
module dshaft_byj2d(c) {
    intersection() {
        circle(d = byj_shaft_d + 2*c);
        square([byj_shaft_flat + 2*c, byj_shaft_d * 2], center = true);
    }
}

// 가로로 뚫는 구멍용 물방울 모양 (뾰족한 쪽이 +Y → 출력 시 위쪽)
module teardrop2d(d) {
    union() {
        circle(d = d);
        polygon([[-d/2*cos(45), d/2*sin(45)], [0, d/2/sin(45)], [d/2*cos(45), d/2*sin(45)]]);
    }
}

// 꼭대기를 잘라 낸 물방울 (얇은 벽을 뚫지 않게)
module teardrop_flat2d(d, cap) {
    intersection() {
        teardrop2d(d);
        translate([-d, -d]) square([2*d, d + d/2 + cap]);
    }
}

module m3_nut_pocket(h) {        // 세로 육각 주머니
    cylinder(d = m3_nut_af / cos(30), h = h, $fn = 6);
}

// 옆에서 너트를 밀어 넣는 홈: +X 방향으로 열림
module m3_nut_slot(len) {
    hull() {
        m3_nut_pocket(m3_nut_t);
        translate([len, 0, 0]) m3_nut_pocket(m3_nut_t);
    }
}

module slotted_hole(d, len, h) { // X 방향 긴 구멍
    hull() {
        translate([-len/2, 0, 0]) cylinder(d = d, h = h);
        translate([ len/2, 0, 0]) cylinder(d = d, h = h);
    }
}
