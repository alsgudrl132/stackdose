#include "powder.h"
#include "board.h"
#include "driver/ledc.h"   // 속도 조절(PWM)을 쓸 때

// 칸 번호 → 그 모터의 IN1 · IN2 핀 (POWDER_PINS[slot - 1])
static const gpio_num_t POWDER_PINS[4][2] = {
    { PIN_POWDER1_IN1, PIN_POWDER1_IN2 },
    { PIN_POWDER2_IN1, PIN_POWDER2_IN2 },
    { PIN_POWDER3_IN1, PIN_POWDER3_IN2 },
    { PIN_POWDER4_IN1, PIN_POWDER4_IN2 },
};

esp_err_t powder_init(void)
{
    // TODO
    // 1. POWDER_PINS 8개를 출력으로, 모두 LOW (= 멈춤)
    // 2. PIN_DRV_FAULT 는 입력 (10kΩ 풀업이 회로에 있음)
    (void)POWDER_PINS;   // 채우고 나면 지우기 (아직 안 써서 나는 경고 막기용)
    return ESP_OK;
}

void powder_set(int slot, int speed)
{
    // TODO
    // DRV8833 진리표 (IN1, IN2):
    //   1, 0 → 앞으로      0, 1 → 뒤로      0, 0 → 멈춤 (스르르)      1, 1 → 브레이크
    //
    // 1단계 (먼저 이것만): 속도 무시하고 gpio_set_level 로 켜고 끄기만
    //   speed > 0 → IN1=1, IN2=0 / speed < 0 → IN1=0, IN2=1 / 0 → 둘 다 0
    // 2단계 (목표 무게 근처에서 느리게 하고 싶을 때): 켜는 쪽 핀을 LEDC PWM 으로
    //   ledc_timer_config (주파수 약 20kHz → 모터 소리가 안 들림) + ledc_channel_config
    //   ledc_set_duty(..., 듀티) + ledc_update_duty. 듀티 = 최대값 × |speed| / 100
    //   한 번에 모터 하나만 돌리니 PWM 채널은 하나를 돌려 써도 됨
    (void)slot;
    (void)speed;
}

bool powder_fault(void)
{
    // TODO: gpio_get_level(PIN_DRV_FAULT) 가 0 이면 이상
    return false;
}
