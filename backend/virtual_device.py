# 가상 디스펜서: 진짜 기계(나중에 ESP32) 대신 백엔드 API 로만 대화하는 프로그램
# 2초마다 "다음 일감 있어요?" 물어보고(폴링), 있으면 맡기 → 담는 척 → 완료 보고
# 실행: backend 폴더에서 python virtual_device.py (uvicorn 서버가 켜져 있어야 함). 끌 때는 Ctrl+C
import requests
import time

while True:
    # 다음 일감 (requested 중 가장 오래된 것). 없으면 None
    status = requests.get("http://localhost:8000/device/next").json()

    if status == None:
        print("일감 없음")
    else:
        # 일감 맡기: requested → running
        startResult = requests.post(f"http://localhost:8000/dispenses/{status['id']}/start")
        print(startResult.json())
        # 200 일 때만 진행. 409 면 다른 기계가 먼저 가져간 것이라 건드리지 않음
        if startResult.status_code == 200:
            time.sleep(3)   # 담는 척 (진짜 기계라면 여기서 모터를 돌림)
            # 완료 보고: running → done
            finishResult = requests.post(f"http://localhost:8000/dispenses/{status['id']}/finish").json()
            print(finishResult)
    time.sleep(2)   # 한 바퀴마다 2초 쉬고 다시 확인
