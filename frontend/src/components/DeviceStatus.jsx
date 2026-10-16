const STATE_TEXT = {
  idle: '대기 중',
  dispensing: '담는 중',
  offline: '기계 꺼짐',
}

// 마지막 신호가 몇 초 전인지 (기계는 2초마다 서버에 일감을 물어봄)
function seenText(sec) {
  if (sec == null) return '없음'
  if (sec < 3) return '방금'
  if (sec < 60) return `${sec}초 전`
  return `${Math.floor(sec / 60)}분 전`
}

export default function DeviceStatus({ device, serverDown }) {
  if (serverDown) {
    return (
      <p className="device device--offline" role="status">
        <span className="device__dot" aria-hidden="true" />
        <span className="device__state">서버 꺼짐</span>
      </p>
    )
  }

  const state = device?.state ?? 'offline'

  return (
    <p className={`device device--${state}`} role="status">
      <span className="device__dot" aria-hidden="true" />
      <span className="device__state">{STATE_TEXT[state]}</span>
      <span className="device__seen">신호 {seenText(device?.seen_sec)}</span>
    </p>
  )
}
