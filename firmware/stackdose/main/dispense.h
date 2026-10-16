// 담기: 서버가 준 amounts[8] 대로 칸마다 담음 (scale · powder · pill 을 조합)
#pragma once

#include <stdbool.h>
#include "board.h"

// 가루 slot 번 칸(1~4)에서 grams 만큼 (저울을 보면서)
bool dispense_powder(int slot, int grams);

// 알약 slot 번 칸(5~8)에서 count 알
bool dispense_pill(int slot, int count);

// 일감 하나: amounts[i] 가 0 이 아닌 칸만 차례로. 하나라도 실패하면 false
bool dispense_job(const int amounts[SLOT_COUNT]);
