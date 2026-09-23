// 화면 확인용 가짜 데이터입니다. 나중에 백엔드 API 응답으로 바꿉니다.
// 1번, 5번 칸과 '아침' 프리셋은 backend/stackdose.db 예시 행과 같습니다.

export const device = {
  online: true,
  state: "dispensing", // idle | dispensing | offline
  lastSeen: "방금",
};

// kind: powder = 가루 칸(스크류, g), pill = 알약 칸(원판, 알)
// export const slots = [
//   { no: 1, supplement: '크레아틴', kind: 'powder', remaining: 250 },
//   { no: 2, supplement: 'BCAA', kind: 'powder', remaining: 40 },
//   { no: 3, supplement: null, kind: 'powder', remaining: 0 },
//   { no: 4, supplement: null, kind: 'powder', remaining: 0 },
//   { no: 5, supplement: '오메가3', kind: 'pill', remaining: 60 },
//   { no: 6, supplement: '비타민D', kind: 'pill', remaining: 8 },
//   { no: 7, supplement: null, kind: 'pill', remaining: 0 },
//   { no: 8, supplement: null, kind: 'pill', remaining: 0 },
// ]

export const presets = [
  {
    no: 1,
    name: "아침",
    items: [
      { slot: 1, amount: 5 },
      { slot: 5, amount: 2 },
    ],
  },
  {
    no: 2,
    name: "운동 후",
    items: [
      { slot: 1, amount: 5 },
      { slot: 2, amount: 7 },
    ],
  },
];

// 배출 진행 화면 예시: '아침' 프리셋을 담는 중
export const dispense = {
  preset: "아침",
  steps: [
    { slot: 1, target: 5, actual: 3.2, status: "running" },
    { slot: 5, target: 2, actual: 0, status: "waiting" },
  ],
};
