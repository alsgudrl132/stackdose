#include "pill.h"
#include "board.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/i2c_master.h"
#include "esp_adc/adc_oneshot.h"

// MCP23017 레지스터 주소 (IOCON.BANK = 0, 켤 때 기본값)
#define MCP_IODIRA   0x00   // 핀 방향 A (0 = 출력)
#define MCP_IODIRB   0x01   // 핀 방향 B
#define MCP_GPIOA    0x12   // 핀 값 A (GPA0~7)
#define MCP_GPIOB    0x13   // 핀 값 B (GPB0~7)

// 28BYJ-48 반스텝 순서: ULN2003 의 IN1~IN4 네 비트 (8단계 → 처음으로)
static const uint8_t HALF_STEP[8] = {
    0b0001, 0b0011, 0b0010, 0b0110, 0b0100, 0b1100, 0b1000, 0b1001,
};

// 홀 센서 ADC 채널 (5~8번 칸 순서)
static const adc_channel_t HALL_CH[4] = { HALL1_CH, HALL2_CH, HALL3_CH, HALL4_CH };

static i2c_master_dev_handle_t s_mcp;          // MCP23017 과 통신할 때 쓰는 손잡이
static adc_oneshot_unit_handle_t s_adc;        // ADC1 손잡이
static uint8_t s_gpio[2];                      // MCP 의 지금 핀 값 [A, B] (다른 모터 핀을 안 건드리려고 기억해 둠)

// MCP23017 레지스터 하나에 값 쓰기: [레지스터 주소, 값] 두 바이트를 보냄
static esp_err_t mcp_write(uint8_t reg, uint8_t value)
{
    // uint8_t buf[2] = { reg, value }; i2c_master_transmit(s_mcp, buf, 2, 100)
    (void)reg;
    (void)value;
    return ESP_ERR_NOT_SUPPORTED;
}

esp_err_t pill_init(void)
{
    // 1. I2C 버스: i2c_master_bus_config_t (i2c_port = I2C_NUM_0, sda/scl = PIN_I2C_SDA/SCL,
    //    clk_source = I2C_CLK_SRC_DEFAULT, flags.enable_internal_pullup = true) → i2c_new_master_bus
    // 2. 장치 추가: i2c_device_config_t (device_address = MCP23017_ADDR, scl_speed_hz = 100000)
    //    → i2c_master_bus_add_device(..., &s_mcp)
    // 3. mcp_write(MCP_IODIRA, 0x00), mcp_write(MCP_IODIRB, 0x00)  → 16핀 모두 출력
    //    mcp_write(MCP_GPIOA, 0x00), mcp_write(MCP_GPIOB, 0x00)    → 모두 LOW
    // 4. ADC1: adc_oneshot_new_unit(unit_id = ADC_UNIT_1) → HALL_CH 4개를
    //    adc_oneshot_config_channel (atten = ADC_ATTEN_DB_12: 0~3.3V 를 읽을 수 있게)
    //    (mV 로 바꾸려면 adc_cali_create_scheme_line_fitting 도 준비. 처음엔 raw 로 봐도 됨)
    (void)s_adc;   // (void) 줄들은 채우고 나면 지우기 (아직 안 써서 나는 경고 막기용)
    (void)HALL_CH;
    (void)s_mcp;
    (void)mcp_write;
    return ESP_OK;
}

esp_err_t pill_step(int slot, int steps)
{
    // 1. 칸 → MCP 어디인지: 5번 = GPA0~3, 6번 = GPA4~7, 7번 = GPB0~3, 8번 = GPB4~7
    //    (어느 레지스터인지 + 아래 4비트인지 위 4비트인지)
    // 2. |steps| 번 반복: HALF_STEP 다음 칸(음수면 이전 칸)의 4비트를 그 자리에 넣고
    //    (같은 레지스터의 다른 모터 4비트는 s_gpio 에 있는 값 그대로) → mcp_write → 1~2ms 기다림
    //    (너무 빠르면 모터가 못 따라오고 떨기만 함. ESP32 에 바로 꽂은 테스트에서 칸 사이 1500us 가 잘 돌았음,
    //     main.c 의 motor_test 참고. I2C 로 보내는 시간이 더해지니 실물에서 다시 맞추기)
    // 3. 다 돌았으면 pill_release(slot)
    (void)slot;
    (void)steps;
    (void)HALF_STEP;
    (void)s_gpio;
    return ESP_ERR_NOT_SUPPORTED;
}

esp_err_t pill_release(int slot)
{
    // 그 칸의 4비트만 0 으로 → mcp_write
    (void)slot;
    return ESP_ERR_NOT_SUPPORTED;
}

int hall_read_mv(int slot)
{
    // adc_oneshot_read(s_adc, HALL_CH[slot - PILL_FIRST], &raw)
    //       (mV 는 adc_cali_raw_to_voltage. 아니면 raw 그대로 돌려서 기준값을 raw 로 정해도 됨)
    (void)slot;
    return 0;
}

esp_err_t pill_home(int slot)
{
    // 1. 먼저 자석이 없을 때 값(기준, 약 1650mV)을 알아 둠. 처음엔 손으로 원판을 돌리며 찍어 보고 정하기
    // 2. 몇 스텝씩 돌면서 hall_read_mv 가 기준에서 충분히(예: 300mV 넘게) 벗어나면 = 자석 위
    //    한 바퀴(PILL_STEPS_PER_REV)를 다 돌아도 못 찾으면 ESP_ERR_NOT_FOUND (자석 빠짐, 센서 선 빠짐)
    // 3. PILL_HOME_OFFSET_STEPS 만큼 더 돌아서 대기 위치에 세움 → pill_release
    (void)slot;
    return ESP_ERR_NOT_SUPPORTED;
}
