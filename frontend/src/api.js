// 백엔드 주소와 요청 도우미. 화면 코드는 fetch 를 직접 쓰지 않고 여기 함수만 부릅니다.
// 실패하면 서버가 보낸 detail(이유)을 담아 에러를 던집니다 → 화면에서 try/catch 로 보여 줌
const API = 'http://localhost:8000'

async function request(method, path, body) {
  const res = await fetch(`${API}${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  })
  const data = await res.json().catch(() => null)
  if (!res.ok) {
    // 400 · 404 · 409 는 detail 이 글자, 422(모양이 틀림)는 목록이라 기본 문구로
    const detail = typeof data?.detail === 'string' ? data.detail : '요청이 실패했어요'
    throw new Error(detail)
  }
  return data
}

export const api = {
  slots: () => request('GET', '/slots'),
  updateSlot: (no, body) => request('PUT', `/slots/${no}`, body),

  presets: () => request('GET', '/presets'),
  createPreset: (body) => request('POST', '/presets', body),
  updatePreset: (no, body) => request('PUT', `/presets/${no}`, body),
  deletePreset: (no) => request('DELETE', `/presets/${no}`),

  dispense: (presetNo) => request('POST', `/presets/${presetNo}/dispense`),
  cancelDispense: (id) => request('POST', `/dispenses/${id}/cancel`),
  currentDispense: () => request('GET', '/dispenses/current'),

  device: () => request('GET', '/device'),
}
