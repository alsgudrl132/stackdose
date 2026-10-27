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

// ---- 속도 조절 (PWM, ESP32 의 LEDC 기능) ----
// 핀을 1초에 2만 번 켰다 껐다 해서, 켜진 비율(듀티)만큼만 전기를 보냄 → 모터가 그만큼 느리게 돎
// 모터는 한 번에 하나만 돌리니 채널 하나를 "지금 켜는 핀"에 옮겨 붙여 가며 씀
#define PWM_MODE     LEDC_LOW_SPEED_MODE
#define PWM_TIMER    LEDC_TIMER_0
#define PWM_CHANNEL  LEDC_CHANNEL_0
#define PWM_FREQ_HZ  20000                  // 2만 Hz: 사람 귀에 거의 안 들림
#define PWM_BITS     LEDC_TIMER_10_BIT      // 듀티를 0 ~ 1023 단계로 나눔
#define PWM_MAX      1023                   // 듀티 최대값 = 100% (2^10 - 1)

static gpio_num_t pwm_pin = GPIO_NUM_NC;    // 지금 PWM 이 붙어 있는 핀 (없으면 NC)

// 핀을 PWM 에서 떼고 보통 출력 LOW 로 되돌림
static void pin_low(gpio_num_t pin)
{
    gpio_reset_pin(pin);                        // LEDC 에 묶여 있던 연결을 풀고 보통 GPIO 로
    gpio_set_direction(pin, GPIO_MODE_OUTPUT);
    gpio_set_level(pin, 0);
}

// 핀을 PWM 에서 떼고 보통 출력 HIGH 로 (느린 감쇠에서 "계속 켜 두는 쪽")
static void pin_high(gpio_num_t pin)
{
    if (pwm_pin == pin) pwm_pin = GPIO_NUM_NC;
    gpio_reset_pin(pin);
    gpio_set_direction(pin, GPIO_MODE_OUTPUT);
    gpio_set_level(pin, 1);
}

// pin 에 PWM 채널을 붙이고 duty(0~PWM_MAX)로 켬
static void pin_pwm(gpio_num_t pin, uint32_t duty)
{
    if (pwm_pin != GPIO_NUM_NC && pwm_pin != pin) pin_low(pwm_pin);   // 다른 핀에 붙어 있었으면 먼저 뗌
    ledc_channel_config_t ch = {
        .gpio_num   = pin,
        .speed_mode = PWM_MODE,
        .channel    = PWM_CHANNEL,
        .timer_sel  = PWM_TIMER,
        .duty       = duty,
        .hpoint     = 0,
    };
    ledc_channel_config(&ch);
    pwm_pin = pin;
}

esp_err_t powder_init(void)
{
    // 모터 핀 8개(가루 4칸 × IN1·IN2)를 출력으로 만들고 전부 LOW = 멈춤
    // 켜지자마자 부르는 이유: 전원이 들어온 직후 핀이 떠 있으면 모터가 저절로 돌 수 있음
    for (int i = 0; i < 4; i++) {          // i = 칸 (0 → 1번 칸)
        for (int j = 0; j < 2; j++) {      // j = 0 → IN1, 1 → IN2
            gpio_num_t pin = POWDER_PINS[i][j];
            gpio_reset_pin(pin);                         // 핀을 기본 상태로 (다른 기능이 잡고 있었으면 풀어 줌)
            gpio_set_direction(pin, GPIO_MODE_OUTPUT);   // 출력 = ESP32 가 HIGH/LOW 를 내보냄
            gpio_set_level(pin, 0);                      // LOW
        }
    }
    // (nFAULT 는 산 모듈 VLT-MD012 에 핀이 없어서 설정하지 않음)

    // PWM 타이머 하나 준비 (주파수와 듀티 단계 수). 채널은 모터를 켤 때 그 핀에 붙임
    ledc_timer_config_t timer = {
        .speed_mode      = PWM_MODE,
        .timer_num       = PWM_TIMER,
        .duty_resolution = PWM_BITS,
        .freq_hz         = PWM_FREQ_HZ,
        .clk_cfg         = LEDC_AUTO_CLK,
    };
    return ledc_timer_config(&timer);
}

void powder_set(int slot, int speed)
{
    if (slot < POWDER_FIRST || slot > POWDER_LAST) return;   // 가루 칸(1~4)이 아니면 아무것도 안 함
    gpio_num_t in1 = POWDER_PINS[slot - 1][0];               // 칸 번호는 1부터, 배열은 0부터
    gpio_num_t in2 = POWDER_PINS[slot - 1][1];

    // DRV8833 진리표 (IN1, IN2):
    //   1, 0 → 앞으로      0, 1 → 뒤로      0, 0 → 멈춤 (스르르)      1, 1 → 브레이크
    //
    // 속도: speed 의 크기(1~100) → 듀티(0~PWM_MAX). 100 을 넘게 줘도 100 으로
    int pct = speed < 0 ? -speed : speed;   // 크기만 (부호는 아래 if 에서 방향으로 씀)
    if (pct > 100) pct = 100;
    uint32_t duty = 0;  
    duty = PWM_MAX * pct / 100;
    // 방향 + 느린 감쇠(slow decay): 한쪽 핀은 계속 HIGH, 다른 쪽에 "거꾸로 된" PWM
    //   켜진 시간 = (1, 0) 앞으로 / 꺼진 시간 = (1, 1) 브레이크 → 전류가 천천히 줄어서 속도가 듀티에 거의 비례
    //   (처음엔 반대쪽을 LOW 로 두는 빠른 감쇠였는데, 2만 Hz 에서는 60% 를 줘도 거의 안 돌았음 2026-10-27)
    //   반대쪽 핀이 LOW 인 시간이 "켜진 시간"이라 PWM 값은 PWM_MAX - duty
    if(speed < 0) {
        pin_high(in2);
        pin_pwm(in1, PWM_MAX - duty);
    }
    else if(speed > 0) {
        pin_high(in1);
        pin_pwm(in2, PWM_MAX - duty);
    }
    else {
        pin_low(in1);
        pin_low(in2);
        if (pwm_pin == in1 || pwm_pin == in2) pwm_pin = GPIO_NUM_NC;   // 이 칸 핀에서 PWM 이 떨어졌음
    }
}

bool powder_fault(void)
{
    // 산 모듈(VLT-MD012)에 nFAULT 핀이 없어서 항상 false. 막힘은 "무게가 안 늘어남"으로 dispense 쪽에서 알아냄
    return false;
}
