import { unit, amountText } from '../format'
import { StopIcon, CheckIcon, AlertIcon } from './Icons'

const STATUS_TEXT = {
  waiting: '대기',
  running: '담는 중',
  done: '완료',
  failed: '실패',
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
  const pct = Math.min(100, (actual / target) * 100)
  return (
    <span className="meter" aria-hidden="true">
      <span className="meter__fill" style={{ width: `${pct}%` }} />
    </span>
  )
}

export default function DispensePanel({ dispense, slots }) {
  const done = dispense.steps.filter((s) => s.status === 'done').length

  return (
    <section className="run" aria-labelledby="run-title">
      <header className="run__head">
        <p className="eyebrow run__eyebrow">
          <span className="run__live" aria-hidden="true" />
          Now dosing
        </p>
        <h2 id="run-title" className="run__title">{dispense.preset}</h2>
        <p className="run__count" aria-label={`${dispense.steps.length}칸 중 ${done}칸 완료`}>
          <span className="run__done">{done}</span>
          <span className="run__total">/{dispense.steps.length}</span>
        </p>
      </header>

      <ol className="run__steps">
        {dispense.steps.map((step) => {
          const slot = slots.find((s) => s.no === step.slot)
          const kind = slot?.kind
          const pct = Math.round(Math.min(100, (step.actual / step.target) * 100))
          return (
            <li key={step.slot} className={`step step--${step.status} is-${kind}`}>
              <div className="step__top">
                <span className="step__no">{step.slot}</span>
                <span className="step__name">{slot?.supplement}</span>
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

      <button className="btn btn--stop" type="button">
        <StopIcon />
        멈추기
      </button>
    </section>
  )
}
