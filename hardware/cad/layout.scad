// 모듈 배치 (frame.scad · assembly.scad 가 같이 씀). include <config.scad> 뒤에 include.

pill_phi = [45, 135, 225, 315];                    // 알약 컵 중심에서 본 모듈 방향

function rot2(p, a) = [p[0]*cos(a) - p[1]*sin(a), p[0]*sin(a) + p[1]*cos(a)];
function add2(a, b) = [a[0] + b[0], a[1] + b[1]];

// 가루 모듈 i: 출구 끝이 컵 중심에서 powder_d 떨어짐, 로컬 +Y 가 바깥쪽
function powder_xy(p, i) = add2(cupP, rot2(add2(p, [0, powder_d]), powder_a[i] - 90));
module at_powder(i) translate([cupP[0], cupP[1], deck_top]) rotate(powder_a[i] - 90) translate([0, powder_d, 0]) children();

// 알약 모듈 i: 로컬 +Y(출구)가 알약 컵 중심을 향함
function pill_center(i) = add2(cupL, rot2([pill_s * sqrt(2), 0], pill_phi[i]));
function pill_xy(p, i) = add2(pill_center(i), rot2(p, pill_phi[i] + 90));
module at_pill(i) translate([pill_center(i)[0], pill_center(i)[1], deck_top]) rotate(pill_phi[i] + 90) children();

// 미끄럼관 i: 로컬 +Y 가 모듈 쪽
function slide_xy(p, i) = add2(cupL, rot2(p, pill_phi[i] - 90));
module at_slide(i) translate([cupL[0], cupL[1], 0]) rotate(pill_phi[i] - 90) children();
