// 가루 모터: JGA25-370 (6V 77RPM) ×4, DRV8833 ×2 로 돌림
#pragma once

#include <stdbool.h>
#include "esp_err.h"

// 핀 준비 (모터 핀 8개 출력 LOW, nFAULT 입력)
esp_err_t powder_init(void);

// slot 번 칸(1~4) 모터를 speed 로 돌림
//   speed: 1~100 = 앞으로 (가루가 나오는 쪽), -1~-100 = 뒤로 (막힘 풀기), 0 = 멈춤
//   ⚠ 전원 때문에 모터는 한 번에 하나만 돌림 (wiring.md "한 번에 하나만")
void powder_set(int slot, int speed);

// 드라이버 이상 (과전류 · 과열). 모터가 막혀서 전류가 크게 흐를 때도 켜짐
bool powder_fault(void);
