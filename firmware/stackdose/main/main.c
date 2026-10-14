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

static EventGroupHandle_t s_wifi_events;

static void wifi_event_handler(void* args, esp_event_base_t base, int32_t id, void* data)
{
    printf("event detected %" PRId32 "\n", id);
    if(base == WIFI_EVENT && id == WIFI_EVENT_STA_START) esp_wifi_connect();
    else if(base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t* event = (ip_event_got_ip_t*) data;
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

static bool json_get(const char* json, const char* key, char* out, int out_len) {
    char* key_ptr;
    key_ptr = strstr(json, key);
    if(key_ptr != NULL) {
        char* val_start  = key_ptr + strlen(key)+3;
        char* val_end = strchr(val_start , '"');
        if(val_end != NULL) {
            int status_len = val_end - val_start;
            if(status_len < out_len) {
                memcpy(out, val_start , status_len);
                out[status_len] = '\0';
                printf("out = %s\n", out);
                return true;
            }
        }
    }
    return false;
}


void app_main(void)
{
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

    // 붙을 Wi-Fi
    wifi_config_t wifi_config = {
        .sta = {
            .ssid = WIFI_SSID,
            .password = WIFI_PASS,
        },
    };

    s_wifi_events = xEventGroupCreate();

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));   // &: 설정 변수의 주소를 넘김
    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &wifi_event_handler, NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, &wifi_event_handler, NULL));
    ESP_ERROR_CHECK(esp_wifi_start());   // Wi-Fi 켜기 (연결은 아직 안 함 → 2-3)

    xEventGroupWaitBits(s_wifi_events, BIT0, pdFALSE, pdTRUE, portMAX_DELAY);

    printf("Wifi ready\n");

    char body[256];
    int http_code;

    http_code = http_request(HTTP_METHOD_GET, "http://"WIFI_IP":8000/device/next", body, sizeof(body));

    printf("http_code code = %d\n", http_code);
    printf("body = %s\n", body);

    char status_buf[32];
    if(json_get(body, "status", status_buf, sizeof(status_buf))){
        printf("status_buf %s\n", status_buf);
    }

    while (1)
    {
        vTaskDelay(100);
    }
    
}
