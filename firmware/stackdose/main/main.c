/*
 * SPDX-FileCopyrightText: 2010-2022 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: CC0-1.0
 */

#include <stdio.h>
#include <inttypes.h>
#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_chip_info.h"
#include "esp_system.h"
#include "nvs_flash.h"
#include "esp_netif.h"
#include "esp_event.h"
#include "esp_wifi.h"
#include "driver/gpio.h"
#include "wifi_secret.h"
#include "freertos/event_groups.h"
#include "esp_http_client.h"
#include <string.h>
#include <stdbool.h>
#include "board.h"      // 핀 배정 (wiring.md 와 같음)
#include "scale.h"      // 저울 (HX711)
#include "powder.h"     // 가루 모터 (DRV8833)
#include "pill.h"       // 알약 원판 (MCP23017 + 28BYJ, 홀 센서)
#include "dispense.h"   // 담기 로직 (위 셋을 조합)
#include "rom/ets_sys.h" // esp_rom_delay_us: 마이크로초 단위로 기다리기

// 스택도즈 기계 펌웨어 (ESP32, ESP-IDF)
//   Wi-Fi에 붙은 뒤 서버(FastAPI)에 일감을 묻고, 있으면 start → (담기) → finish 를 보고함
//   backend/virtual_device.py 가 하던 일을 C로 옮기는 중

// "IP 받음" 신호등 (FreeRTOS 이벤트 그룹). 핸들러가 BIT0 을 켜고, app_main 이 그걸 기다림
static EventGroupHandle_t s_wifi_events;

// Wi-Fi · IP 소식이 오면 불리는 함수 (JS 의 addEventListener 에 넘기는 핸들러와 같음)
//   base: 어느 쪽 소식인지 (WIFI_EVENT / IP_EVENT)
//   id:   그중 어떤 소식인지 (WIFI_EVENT_STA_START, IP_EVENT_STA_GOT_IP ...)
//   data: 소식에 딸려 온 정보 (종류마다 타입이 달라서 void* 로 옴)
static void wifi_event_handler(void* args, esp_event_base_t base, int32_t id, void* data)
{
    printf("event detected %" PRId32 "\n", id);
    if(base == WIFI_EVENT && id == WIFI_EVENT_STA_START) esp_wifi_connect();   // Wi-Fi 켜졌으면 → 공유기에 연결 시도
    else if(base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {                  // IP 받았으면 → 찍고 신호등 켜기
        ip_event_got_ip_t* event = (ip_event_got_ip_t*) data;                 // data 를 "IP 정보" 타입으로 보고 꺼냄
        printf("got ip: " IPSTR "\n", IP2STR(&event->ip_info.ip));
        xEventGroupSetBits(s_wifi_events, BIT0);
    }
}

// HTTP 요청을 보내고 응답 본문을 buf 에 글자로 담음 (Python 의 requests.get / requests.post 역할)
//   method: HTTP_METHOD_GET 또는 HTTP_METHOD_POST
//   buf, buf_len: 응답을 담을 칸과 그 크기 (넘치는 부분은 잘림)
//   돌려주는 값: 상태 코드 (200, 404, 409 ...), 연결 자체가 실패하면 -1
static int http_request(esp_http_client_method_t method, const char* url, char* buf, int buf_len)
{
    esp_http_client_config_t config = { .url = url, .method = method };
    esp_http_client_handle_t client = esp_http_client_init(&config);
    buf[0] = '\0';   // 실패해도 buf 는 빈 글자로

    if (esp_http_client_open(client, 0) != ESP_OK) {   // 0: 보낼 본문 없음
        esp_http_client_cleanup(client);
        return -1;
    }
    esp_http_client_fetch_headers(client);
    int n = esp_http_client_read_response(client, buf, buf_len - 1);   // 끝에 '\0' 자리 하나 남김
    buf[n > 0 ? n : 0] = '\0';                                         // C 문자열은 '\0' 으로 끝남

    int status = esp_http_client_get_status_code(client);
    esp_http_client_close(client);
    esp_http_client_cleanup(client);
    return status;
}

// JSON 글자에서 글자 값 하나를 꺼내 out 에 담음 (예: "status":"requested" → requested)
//   파서 없이 strstr 로 찾는 간단한 방식이라, 우리 서버처럼 응답 모양을 아는 경우에만 씀
//   out, out_len: 결과를 담을 칸과 그 크기 (칸은 부르는 쪽이 준비함)
//   돌려주는 값: 찾아서 담았으면 true, 키가 없거나 칸이 모자라면 false (이때 out 은 믿으면 안 됨)
static bool json_get(const char* json, const char* key, char* out, int out_len) {
    char* key_ptr;
    key_ptr = strstr(json, key);
    if(key_ptr != NULL) {
        char* val_start  = key_ptr + strlen(key)+3;   // 키 뒤의 ":" 3칸을 건너뛰면 값의 첫 글자
        char* val_end = strchr(val_start , '"');      // 값을 닫는 따옴표
        if(val_end != NULL) {
            int status_len = val_end - val_start;     // 주소끼리 빼면 사이의 글자 수
            if(status_len < out_len) {                // '\0' 자리까지 들어가야 함 (넘치면 버퍼 오버플로)
                memcpy(out, val_start , status_len);
                out[status_len] = '\0';               // C 문자열 끝 표시
                return true;
            }
        }
    }
    return false;
}

// JSON 글자에서 숫자 값 하나를 꺼내 *out 에 넣음 (예: "id":10 → 10)
//   out: 숫자를 넣을 변수의 주소 (부를 때 &id 처럼 넘김)
//   돌려주는 값: 키를 찾았으면 true, 없으면 false
static bool json_get_int(const char* json, const char* key, int* out) {
    char* key_ptr;
    key_ptr = strstr(json, key);
    if(key_ptr != NULL) {
        char* val_start  = key_ptr + strlen(key)+2;   // 숫자는 따옴표가 없어서 ": 2칸만 건너뜀
        *out = atoi(val_start);                       // 숫자가 끝나는 곳(, 나 })에서 알아서 멈춤 → 몇 자리든 됨
        return true;
    }
    return false;
}

// 테스트: 28BYJ-48 (ULN2003) 을 ESP32 핀에 바로 꽂아서 알약 한 칸(1/3 바퀴)만큼 돌림 (2026-10-16 확인)
//   실제 기계에서는 MCP23017 을 거쳐서 돌림 → 이 코드는 pill.c 의 pill_step() 으로 옮겨 갈 예정
//   배선 (테스트용): IN1~IN4 = GPIO25, 26, 27, 13 / ULN2003 + = 5V, - = GND
static void motor_test(void)
{
    // 반스텝 순서: 코일 하나 → 둘 → 하나 ... 8단계 (맨 오른쪽 비트 = IN1, 맨 왼쪽 = IN4)
    static const uint8_t HALF_STEP[8] = { 0b0001, 0b0011, 0b0010, 0b0110, 0b0100, 0b1100, 0b1000, 0b1001 };
    static const gpio_num_t MOTOR_PINS[4] = { GPIO_NUM_25, GPIO_NUM_26, GPIO_NUM_27, GPIO_NUM_13 };   // IN1~IN4
    gpio_reset_pin(MOTOR_PINS[0]);
    gpio_reset_pin(MOTOR_PINS[1]);
    gpio_reset_pin(MOTOR_PINS[2]);
    gpio_reset_pin(MOTOR_PINS[3]);

    gpio_set_direction(MOTOR_PINS[0], GPIO_MODE_OUTPUT);
    gpio_set_direction(MOTOR_PINS[1], GPIO_MODE_OUTPUT);
    gpio_set_direction(MOTOR_PINS[2], GPIO_MODE_OUTPUT);
    gpio_set_direction(MOTOR_PINS[3], GPIO_MODE_OUTPUT);

    for (int i = 0; i < 1365; i++) {              // 1365칸 ≈ 1/3 바퀴 = 알약 한 칸 (한 바퀴 약 4096칸)
        uint8_t pattern = HALF_STEP[i % 8];       // 이번에 켤 모양 (8개를 계속 돌려 씀)
        for (int j = 0; j < 4; j++) {             // 핀 4개를 하나씩
            gpio_set_level(MOTOR_PINS[j], (pattern >> j) & 1);   // pattern 의 j번째 비트 = IN(j+1) 켤지
        }
        // 칸 사이 1.5ms (실측: 1500us 면 잘 돎. 더 짧으면 힘이 약해짐). 한 칸 약 2초
        // vTaskDelay 는 최소 10ms(1틱)라 너무 느려서 바쁜 대기를 씀 → 5초 넘게 돌리면 감시견이 재부팅함
        esp_rom_delay_us(1500);
    }

    for (int j = 0; j < 4; j++) {                 // 다 돌면 전부 끄기 (모터가 뜨거워지지 않게)
        gpio_set_level(MOTOR_PINS[j], 0);
    }
}

void app_main(void)
{
    motor_test();   // 테스트: 켤 때마다 한 번 돎. 다 쓰면 지우기

    // 0. 기계 준비: Wi-Fi 보다 먼저 (켜지자마자 모터 핀을 LOW 로 잡아서 저절로 돌지 않게)
    ESP_ERROR_CHECK(powder_init());
    ESP_ERROR_CHECK(pill_init());
    ESP_ERROR_CHECK(scale_init());

    ESP_ERROR_CHECK(
        nvs_flash_init()
    );
    ESP_ERROR_CHECK(
        esp_netif_init()
    );
    ESP_ERROR_CHECK(
        esp_event_loop_create_default()
    );
    
    // 공유기에 붙는 쪽(STA) 네트워크 인터페이스
    esp_netif_create_default_wifi_sta();

    // Wi-Fi 드라이버 초기화 (기본 설정)
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    // 붙을 Wi-Fi (이름 · 비밀번호는 git 에 안 올라가는 wifi_secret.h 에 있음)
    wifi_config_t wifi_config = {
        .sta = {
            .ssid = WIFI_SSID,
            .password = WIFI_PASS,
        },
    };

    s_wifi_events = xEventGroupCreate();   // 핸들러 등록보다 먼저 (신호등이 없는데 IP 소식이 오면 죽음)

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));   // &: 설정 변수의 주소를 넘김
    // 소식 구독: Wi-Fi 소식은 전부, IP 소식은 "IP 받음"만. start 전에 해야 "켜졌어" 소식을 안 놓침
    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &wifi_event_handler, NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, &wifi_event_handler, NULL));
    ESP_ERROR_CHECK(esp_wifi_start());   // Wi-Fi 켜기 → 핸들러가 연결 → IP 받음

    // IP 받을 때까지 여기서 멈춰 기다림 (JS 의 await). 이 아래부터는 서버를 부를 수 있음
    xEventGroupWaitBits(s_wifi_events, BIT0, pdFALSE, pdTRUE, portMAX_DELAY);

    printf("Wifi ready\n");

    char body[256];   // 서버 응답을 담을 칸 (요청마다 덮어씀)
    int http_code;

    // 2초마다 서버에 일감을 묻는 반복 (virtual_device.py 의 while True). 쉬는 동안 CPU 를 양보함
    while (1)
    {
        // 1. 일감 있는지 묻기 (없으면 body = null)
        http_code = http_request(HTTP_METHOD_GET, "http://"WIFI_IP":8000/device/next", body, sizeof(body));

        printf("http_code code = %d\n", http_code);
        printf("body = %s\n", body);

        char status[32];
        if(json_get(body, "status", status, sizeof(status))){
            printf("status %s\n", status);
        }

        // 칸별 담을 양 꺼내기: "amounts":[5,0,0,0,2,0,0,0] → amounts[0..7]
        //   자리 0~3 = 가루 1~4번 칸 (g), 자리 4~7 = 알약 5~8번 칸 (알). 0 이면 그 칸은 건너뜀
        //   start/finish 응답이 body 를 덮어쓰기 전에 꺼내 둬야 함
        int amounts[SLOT_COUNT] = {0};   // 못 읽으면 전부 0 → 아무것도 안 담음
        char* p = strstr(body, "amounts");
        if (p != NULL) {
            p = strchr(p, '[');
            p = p + 1;                          
            for (int i = 0; i < 8; i++) {       
                amounts[i] = atoi(p);           
                if (i < 7) {                    
                    p = strchr(p, ',') + 1;    
                }
                printf("amount[%d] = %d\n", i, amounts[i]);
            }
        }

        // 2. 일감이 있을 때만 (id 를 찾았을 때만) 기계가 일함: start → 담기 → finish
        int id;
        if(json_get_int(body, "id", &id)){
            printf("id %d\n", id);

            char url[64];   // f-string 대신 칸에 URL 을 만들어 씀 (snprintf 는 칸 크기를 넘지 않게 잘라 줌)
            snprintf(url, sizeof(url), "http://"WIFI_IP":8000/dispenses/%d/start", id);
            if(200 == http_request(HTTP_METHOD_POST, url, body, sizeof(body))){   // start 가 받아들여졌을 때만 (409: 이미 누가 가져감, -1: 연결 실패)
                printf("body = %s\n", body);

                // 실제 담기 (dispense.c). 지금은 부품이 없어서 가짜
                // TODO: 실패하면 finish 대신 실패를 알려야 함 → 서버에 실패 보고 API 가 생기면 바꾸기
                if (!dispense_job(amounts)) {
                    printf("dispense failed\n");
                }

                snprintf(url, sizeof(url), "http://"WIFI_IP":8000/dispenses/%d/finish", id);
                http_request(HTTP_METHOD_POST, url, body, sizeof(body));
                printf("body = %s\n", body);
            }
        }

        vTaskDelay(200);   // 2초
    }
    
}
