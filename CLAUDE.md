# stackdose

보충제 디스펜서 (가루 4칸 스크류 + 로드셀, 알약 4칸 원판). 웹 프리셋 → 1회분을 컵 두 개(가루 컵은 저울 위, 알약 컵은 알약 스테이션)에 담음.

**처음 세션이면 [docs/HANDOFF.md](docs/HANDOFF.md)를 먼저 끝까지 읽으세요.** 상태, 결정 이유, 치수, 검사, 부품, 남은 일이 모두 거기 있습니다.

## 규칙

- 설계 숫자는 `hardware/cad/config.scad`에서만 고칩니다. ★ 값은 추정치이니 사실처럼 말하지 않습니다.
- 설계를 고치면 `cd hardware/cad && python check.py`를 돌립니다 (약 10분, 한글이 깨지면 `PYTHONIOENCODING=utf-8`). 결과를 숨기지 않습니다.
- 부품 파일끼리는 `use`로 부르고, `include`는 config·lib·layout만 합니다. 새 변수에는 부품 접두어를 붙입니다 (include 변수가 소리 없이 덮어써짐).
- 모든 출력물은 서포트 없이 Ender-3 SE(220×220×250)에 들어가야 합니다.
- 나사는 20개가 목표입니다. 힘받는 곳만 나사를 쓰고, 나머지는 핀·돌기·턱·한 덩어리로 합니다. 토이 프로젝트라 과하게 설계하지 않습니다.
- 부품은 디바이스마트만 쓰고, `tools/devicemart/` 스크립트로 확인한 것만 알려 줍니다.
- 출력 순서: 쿠폰 → 모듈 1벌씩 → 나머지 → 큰 판은 마지막 (보드 받침이 바닥판에 붙어 있어서, 보드 실측이 먼저).

## 폴더

- `hardware/cad/`: OpenSCAD 설계, STL, `check.py`, `overhang.py`
- `hardware/wiring.md`: 핀 배정, 전원, 선 길이
- `hardware/parts.md`: 부품표
- `backend/` · `frontend/` · `firmware/`: 아직 없음 (다음 단계)
