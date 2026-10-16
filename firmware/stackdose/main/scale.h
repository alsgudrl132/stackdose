// 저울: HX711 + 로드셀 1kg (가루 컵이 올라가는 곳)
#pragma once

#include <stdint.h>
#include "esp_err.h"

// 1g 에 HX711 숫자가 얼마나 변하는지 ★ 부품이 오면 직접 재서 바꾸기
//   재는 법: 빈 컵으로 scale_tare() → 무게를 아는 물건(예: 100g 추, 물 100ml)을 올림
//            → (그때 raw - tare 값) / 100 을 여기에 넣음
#define SCALE_COUNTS_PER_GRAM   400.0f

// 핀 준비: DT 는 입력, SCK 는 출력 LOW (SCK 가 60us 넘게 HIGH 면 HX711 이 꺼짐)
esp_err_t scale_init(void);

// HX711 에서 값 한 번 읽기 (24비트, 부호 있음). 준비가 안 되면 ESP_ERR_TIMEOUT
esp_err_t scale_read_raw(int32_t* out);

// 지금 올라가 있는 무게를 0 으로 (빈 컵을 올린 뒤, 담기 시작 전에 부름)
esp_err_t scale_tare(void);

// 영점 기준 무게 (g)
esp_err_t scale_read_grams(float* out);
