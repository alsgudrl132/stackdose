import { useEffect, useRef, useState } from 'react'
import { api } from '../api'
import { unit, kindLabel } from '../format'

// 칸 하나 고치기: 넣어 둔 것의 이름과 남은 양. 이름을 비우고 저장하면 빈 칸이 됨
export default function SlotEditor({ slot, onSaved, onCancel }) {
  const [name, setName] = useState(slot.supplement ?? '')
  const [remaining, setRemaining] = useState(String(slot.remaining ?? 0))
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    ref.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }, [])

  const send = async (body) => {
    setBusy(true)
    setError('')
    try {
      await api.updateSlot(slot.no, body)
      await onSaved()
    } catch (err) {
      setError(err.message)
      setBusy(false)
    }
  }

  const save = (e) => {
    e.preventDefault()
    const amount = Number(remaining)
    if (!Number.isInteger(amount) || amount < 0) {
      setError('남은 양은 0 이상의 정수로 적어 주세요')
      return
    }
    send({ supplement: name.trim() || null, remaining: amount })
  }

  return (
    <section className={`section is-${slot.kind}`} aria-labelledby="slot-editor-title" ref={ref}>
      <div className="section__head">
        <div>
          <p className="eyebrow">Slot {slot.no} · {kindLabel(slot.kind)}</p>
          <h2 id="slot-editor-title" className="section__title">
            {slot.supplement ? `${slot.no}번 칸 고치기` : `${slot.no}번 칸 채우기`}
          </h2>
        </div>
      </div>

      <form className="editor" onSubmit={save}>
        <label className="field">
          <span className="field__label">넣어 둔 것</span>
          <input
            className="input input--name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder={slot.kind === 'powder' ? '예: 크레아틴' : '예: 오메가3'}
          />
        </label>

        <label className="field">
          <span className="field__label">남은 양</span>
          <span className="input-unit">
            <input
              className="input input--num"
              type="number"
              inputMode="numeric"
              min="0"
              step="1"
              value={remaining}
              onChange={(e) => setRemaining(e.target.value)}
              disabled={!name.trim()}
            />
            <span aria-hidden="true">{unit(slot.kind)}</span>
          </span>
        </label>

        {error && <p className="form-error" role="alert">{error}</p>}

        <div className="editor__actions">
          {slot.supplement && (
            <button
              className="btn btn--text btn--danger"
              type="button"
              onClick={() => send({ supplement: null, remaining: 0 })}
              disabled={busy}
            >
              비우기
            </button>
          )}
          <button className="btn btn--line" type="button" onClick={onCancel} disabled={busy}>취소</button>
          <button className="btn btn--solid" type="submit" disabled={busy}>
            {busy ? '저장 중…' : '저장'}
          </button>
        </div>
      </form>
    </section>
  )
}
