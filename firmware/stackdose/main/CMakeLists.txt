idf_component_register(SRCS "main.c" "scale.c" "powder.c" "pill.c" "dispense.c"
                       PRIV_REQUIRES nvs_flash esp_netif esp_event esp_wifi esp_driver_gpio esp_http_client
                                     esp_driver_i2c esp_driver_ledc esp_adc
                       INCLUDE_DIRS "")
