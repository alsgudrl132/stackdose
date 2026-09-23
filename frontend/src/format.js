// 칸 종류로 단위가 정해집니다 (가루 g, 알약 알).
export const unit = (kind) => (kind === 'powder' ? 'g' : '알')

export const kindLabel = (kind) => (kind === 'powder' ? '가루' : '알약')

// 화면에 보이는 숫자: 가루는 소수 한 자리, 알약은 정수
export const amountText = (kind, value) =>
  kind === 'powder' ? Number(value).toFixed(1) : String(value)
