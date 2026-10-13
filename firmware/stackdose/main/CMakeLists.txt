idf_component_register(SRCS "main.c"
                       PRIV_REQUIRES nvs_flash esp_netif esp_event esp_wifi esp_driver_gpio esp_http_client
                       INCLUDE_DIRS "")
