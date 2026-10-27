#include "dispense.h"
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "scale.h"
#include "powder.h"
#include "pill.h"

// 지금은 부품이 없어서 "담는 척"(printf + 1초)만 함. 부품이 오면 아래 빈 곳을 채우기
// 이 파일이 이 기계의 핵심 로직 (면접에서 설명할 부분)

bool dispense_powder(int slot, int grams)
{
    printf("[가짜] 가루 %d번 칸 %dg\n", slot, grams);
    vTaskDelay(pdMS_TO_TICKS(1000));

    // (HANDOFF 9장 펌웨어 메모: 무게 폐루프)
    // 1. scale_tare() → 지금 컵 무게를 0 으로
    // 2. powder_set(slot, 100) 으로 돌리면서 짧게(예: 100ms) 쉬며 scale_read_grams 를 반복해서 봄
    // 3. 목표 근처(예: 목표 - 1g)면 느리게 (powder_set(slot, 40)). 스크류가 멈춰도 떨어지는 가루가 있음
    // 4. 목표에 닿으면 powder_set(slot, 0)
    // 5. 실패 처리
    //    - 무게가 몇 초 동안 안 늘면 = 막힘 → 잠깐 뒤로(powder_set(slot, -100) 0.3초) 후 다시
    //      몇 번 해도 안 되면 false (통이 비었거나 가루가 굳음)
    //    - powder_fault() 가 true 면 바로 멈추고 false
    //    - 전체 시간 제한 (예: 60초)
    // 6. ⚠ 어떤 길로 끝나든 마지막엔 반드시 powder_set(slot, 0)
    (void)scale_read_grams;
    (void)powder_set;
    return true;
}

bool dispense_pill(int slot, int count)
{
    printf("[가짜] 알약 %d번 칸 %d알\n", slot, count);
    vTaskDelay(pdMS_TO_TICKS(1000));

    // 1. pill_home(slot) 로 원점 → 대기 위치 (실패하면 false)
    // 2. count 번: pill_step(slot, PILL_STEPS_PER_PILL) → 잠깐 기다림 (알약이 떨어질 시간)
    // 3. pill_release(slot)
    // (나중에) 한 알마다 저울로 무게가 늘었는지 확인하면 "안 떨어짐"도 잡을 수 있음
    (void)pill_home;
    return true;
}

bool dispense_job(const int amounts[SLOT_COUNT])
{
    // 1. i = 0 ~ SLOT_COUNT-1 돌면서 amounts[i] 가 0 이면 건너뜀
    // 2. 칸 번호 = i + 1. POWDER_FIRST~POWDER_LAST 면 dispense_powder, 아니면 dispense_pill
    // 3. 하나라도 false 면 바로 멈추고 false (나머지 칸은 담지 않음)
    (void)amounts;
    printf("[가짜] dispense_job: 아직 안 만듦\n");
    vTaskDelay(pdMS_TO_TICKS(3000));
    return true;
}
