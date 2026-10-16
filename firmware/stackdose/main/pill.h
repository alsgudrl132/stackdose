// 알약 원판: 28BYJ-48 ×4 (ULN2003 ×4) 를 MCP23017 (I2C) 로 돌림, 원점은 홀 센서 ×4
#pragma once

#include <stdbool.h>
#include "esp_err.h"

// 28BYJ-48 반스텝(half-step) 기준 한 바퀴 ★ 기어비가 정확히 64가 아니라 실제로는 약 4076
#define PILL_STEPS_PER_REV      4096
// 원판 칸이 3개라 한 알 = 120° = 한 바퀴의 1/3
#define PILL_STEPS_PER_PILL     (PILL_STEPS_PER_REV / 3)
// 원점(자석이 센서 위)에서 대기 위치까지 ★ 원판을 조립한 뒤 맞추기 (자석은 대기 상태에서 350°)
#define PILL_HOME_OFFSET_STEPS  0

// I2C 준비 + MCP23017 의 16핀을 모두 출력 LOW 로 + 홀 센서용 ADC 준비
esp_err_t pill_init(void);

// slot 번 칸(5~8) 원판을 steps 만큼 (음수면 반대로). 끝나면 코일을 끔
esp_err_t pill_step(int slot, int steps);

// slot 번 칸 모터의 네 핀을 모두 LOW (쉬는 동안 열 안 나게)
esp_err_t pill_release(int slot);

// slot 번 칸 홀 센서 전압 (mV). 자석이 없으면 약 1650, 자석이 오면 위나 아래로 크게 움직임
int hall_read_mv(int slot);

// 원점 찾기: 자석이 센서 위에 올 때까지 조금씩 돌고 → 대기 위치까지 오프셋만큼 더 돔
esp_err_t pill_home(int slot);
