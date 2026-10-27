#include "scale.h"
#include "board.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "rom/ets_sys.h"   // esp_rom_delay_us: 마이크로초 단위로 기다리기

static int32_t s_tare = 0;   // scale_tare() 때 잰 값 (영점)

esp_err_t scale_init(void)
{
    // 1. DT 핀: gpio_set_direction(PIN_HX711_DT, GPIO_MODE_INPUT)
    // 2. SCK 핀: 출력으로 만들고 gpio_set_level(PIN_HX711_SCK, 0)
    return ESP_OK;
}

esp_err_t scale_read_raw(int32_t* out)
{
    // (HX711 데이터시트의 타이밍 그림 대로)
    // 1. DT 가 LOW 가 될 때까지 기다림 = 새 값 준비됨. 너무 오래(예: 200ms) 안 되면 ESP_ERR_TIMEOUT
    //    (HX711 은 1초에 10번 값을 만듦 → 최대 약 100ms 기다리면 나옴)
    // 2. 24번 반복: SCK HIGH → 1us 기다림 → DT 를 읽어서 한 비트씩 왼쪽으로 쌓음 → SCK LOW → 1us
    //    (먼저 나오는 비트가 가장 큰 자리. value = (value << 1) | 읽은값)
    // 3. SCK 를 한 번 더 HIGH → LOW (25번째 펄스 = 다음에도 A채널, 증폭 128배로 읽겠다는 뜻)
    // 4. 24비트 음수 처리: 23번 비트가 1이면 위쪽 8비트를 1로 채움 (value |= 0xFF000000)
    //    → int32_t 로 *out 에 넣기
    // 주의: 2~3번 사이에 다른 작업이 끼면(SCK 가 60us 넘게 HIGH) HX711 이 꺼짐
    //       → 짧게 끝나니 지금은 그냥 두고, 값이 튀면 그때 portDISABLE_INTERRUPTS 를 생각
    *out = 0;
    return ESP_ERR_NOT_SUPPORTED;
}

esp_err_t scale_tare(void)
{
    // scale_read_raw 를 몇 번(예: 10번) 읽어 평균을 s_tare 에 저장
    //       한 번만 읽으면 흔들림이 그대로 영점이 됨
    s_tare = 0;
    return ESP_ERR_NOT_SUPPORTED;
}

esp_err_t scale_read_grams(float* out)
{
    // raw 를 읽고 (raw - s_tare) / SCALE_COUNTS_PER_GRAM
    *out = 0.0f;
    return ESP_ERR_NOT_SUPPORTED;
}
