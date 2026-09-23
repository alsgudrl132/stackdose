const STATE_TEXT = {
  idle: '대기 중',
  dispensing: '담는 중',
  offline: '연결 끊김',
}

export default function DeviceStatus({ device }) {
  const state = device.online ? device.state : 'offline'

  return (
    <p className={`device device--${state}`} role="status">
      <span className="device__dot" aria-hidden="true" />
      <span className="device__state">{STATE_TEXT[state]}</span>
      <span className="device__seen">신호 {device.lastSeen}</span>
    </p>
  )
}
