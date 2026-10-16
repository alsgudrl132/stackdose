// 핀 배정과 기계 숫자 (hardware/wiring.md 와 같아야 함. 배선을 바꾸면 둘 다 고치기)
#pragma once

#include "driver/gpio.h"
#include "hal/adc_types.h"

// ---- 칸 ----
// 칸 번호는 서버의 amounts[8] 과 같게 1~8 로 씀 (amounts[i] = i+1 번 칸)
#define SLOT_COUNT        8
#define POWDER_FIRST      1   // 가루 1~4번 칸 (스크류 + DC 모터, 양 = g)
#define POWDER_LAST       4
#define PILL_FIRST        5   // 알약 5~8번 칸 (원판 + 28BYJ, 양 = 알)
#define PILL_LAST         8

// ---- I2C: MCP23017 (알약 모터 4개를 대신 켜 주는 IO 확장 칩) ----
#define PIN_I2C_SDA       GPIO_NUM_21
#define PIN_I2C_SCL       GPIO_NUM_22
#define MCP23017_ADDR     0x20   // A0·A1·A2 를 GND 에 연결했을 때

// ---- HX711 (로드셀 → 무게) ----
#define PIN_HX711_DT      GPIO_NUM_18   // 데이터 (HX711 → ESP32)
#define PIN_HX711_SCK     GPIO_NUM_33   // 클럭 (ESP32 → HX711)

// ---- DRV8833 ×2 (가루 모터 4개). 모터마다 IN1 · IN2 두 핀 ----
#define PIN_POWDER1_IN1   GPIO_NUM_25   // DRV8833 #1 AIN1
#define PIN_POWDER1_IN2   GPIO_NUM_26   // DRV8833 #1 AIN2
#define PIN_POWDER2_IN1   GPIO_NUM_27   // DRV8833 #1 BIN1
#define PIN_POWDER2_IN2   GPIO_NUM_13   // DRV8833 #1 BIN2
#define PIN_POWDER3_IN1   GPIO_NUM_32   // DRV8833 #2 AIN1
#define PIN_POWDER3_IN2   GPIO_NUM_23   // DRV8833 #2 AIN2
#define PIN_POWDER4_IN1   GPIO_NUM_4    // DRV8833 #2 BIN1
#define PIN_POWDER4_IN2   GPIO_NUM_19   // DRV8833 #2 BIN2
#define PIN_DRV_FAULT     GPIO_NUM_5    // 두 드라이버의 nFAULT 를 묶음. LOW = 과전류 · 과열

// ---- 홀 센서 ×4 (알약 원판 원점). 모두 ADC1 이라 Wi-Fi 를 켜도 읽힘 ----
#define HALL1_CH          ADC_CHANNEL_0   // GPIO36 (VP), 5번 칸
#define HALL2_CH          ADC_CHANNEL_3   // GPIO39 (VN), 6번 칸
#define HALL3_CH          ADC_CHANNEL_6   // GPIO34,      7번 칸
#define HALL4_CH          ADC_CHANNEL_7   // GPIO35,      8번 칸
