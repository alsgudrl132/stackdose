import { useState } from 'react'
import { unit, amountText } from '../format'
import { StopIcon, CheckIcon, AlertIcon } from './Icons'

const STATUS_TEXT = {
  waiting: '대기',
  running: '담는 중',
  done: '완료',
  failed: '실패',
  canceled: '취소',
}

// 패널 위쪽 영문 머리말: 요청 전체의 상태
const HEAD_TEXT = {
  requested: 'Queued',
  running: 'Now dosing',
  done: 'Done',
  canceled: 'Canceled',
  failed: 'Failed',
}

// 가루는 무게라 눈금 막대로, 알약은 한 알씩 떨어지니 칸으로 보여 줍니다.
function StepGauge({ kind, actual, target }) {
  if (kind === 'pill') {
    return (
      <span className="pips" aria-hidden="true">
        {Array.from({ length: target }, (_, i) => (
          <span key={i} className={`pip${i < actual ? ' pip--on' : ''}`} />
        ))}
      </span>
    )
  }
  const pct = target > 0 ? Math.min(100, (actual / target) * 100) : 0
  return (
    <span className="meter" aria-hidden="true">
      <span className="meter__fill" style={{ width: `${pct}%` }} />
    </span>
  )
}

// 아래쪽 버튼: 기계가 아직 안 가져간 요청만 취소할 수 있음 (담는 중에는 펌웨어가 멈춤 신호를 아직 안 봄)
function CancelButton({ dispense, onCancel }) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  if (dispense.status === 'running') {
    return (
      <button className="btn btn--stop" type="button" disabled>
        <StopIcon />
        담는 중에는 멈출 수 없어요
      </button>
    )
  }
  if (dispense.status !== 'requested') return null

  const cancel = async () => {
    setBusy(true)
    setError('')
    try {
      await onCancel(dispense.id)
    } catch (e) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      <button className="btn btn--stop" type="button" onClick={cancel} disabled={busy}>
        <StopIcon />
        {busy ? '취소하는 중…' : '취소하기'}
      </button>
      {error && <p className="run__error" role="alert">{error}</p>}
    </>
  )
}

export default function DispensePanel({ dispense, slots, onCancel }) {
  if (!dispense) {
    return (
      <section className="run run--idle" aria-labelledby="run-title">
        <header className="run__head">
          <p className="eyebrow run__eyebrow">Ready</p>
          <h2 id="run-title" className="run__title">담는 중인 것 없음</h2>
        </header>
        <p className="run__note">아래 프리셋에서 담기를 누르면 여기에 진행 상황이 보여요.</p>
      </section>
    )
  }

  const done = dispense.steps.filter((s) => s.status === 'done').length
  const live = dispense.status === 'running'

  return (
    <section className={`run run--${dispense.status}`} aria-labelledby="run-title">
      <header className="run__head">
        <p className="eyebrow run__eyebrow">
          {live && <span className="run__live" aria-hidden="true" />}
          {HEAD_TEXT[dispense.status] ?? dispense.status}
          <span className="run__id">#{dispense.id}</span>
        </p>
        <h2 id="run-title" className="run__title">{dispense.name ?? '삭제된 프리셋'}</h2>
        <p className="run__count" aria-label={`${dispense.steps.length}칸 중 ${done}칸 완료`}>
          <span className="run__done">{done}</span>
          <span className="run__total">/{dispense.steps.length}</span>
        </p>
      </header>

      {dispense.status === 'requested' && (
        <p className="run__note">기계가 가져가기를 기다리는 중이에요.</p>
      )}
      {dispense.status === 'failed' && (
        <p className="run__error" role="alert">
          기계가 담다가 멈췄어요. 통이 비었거나 가루가 막혔는지 확인해 주세요.
        </p>
      )}

      <ol className="run__steps">
        {dispense.steps.map((step) => {
          const slot = slots.find((s) => s.no === step.slot)
          const kind = slot?.kind
          const pct = step.target > 0 ? Math.round(Math.min(100, (step.actual / step.target) * 100)) : 0
          return (
            <li key={step.slot} className={`step step--${step.status} is-${kind}`}>
              <div className="step__top">
                <span className="step__no">{step.slot}</span>
                <span className="step__name">{slot?.supplement ?? '빈 칸'}</span>
                <span className="step__status">
                  {step.status === 'done' && <CheckIcon />}
                  {step.status === 'failed' && <AlertIcon />}
                  {STATUS_TEXT[step.status]}
                </span>
              </div>
              <p className="step__reading">
                <span className="step__actual">{amountText(kind, step.actual)}</span>
                <span className="step__target">
                  / {amountText(kind, step.target)} <small>{unit(kind)}</small>
                </span>
                <span className="step__pct">{pct}%</span>
              </p>
              <StepGauge kind={kind} actual={step.actual} target={step.target} />
            </li>
          )
        })}
      </ol>

      <CancelButton dispense={dispense} onCancel={onCancel} />
    </section>
  )
}
