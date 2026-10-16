import { useEffect, useRef, useState } from 'react'
import { api } from '../api'
import { unit, kindLabel } from '../format'
import { PlusIcon, CloseIcon } from './Icons'

// 프리셋 추가 · 수정. preset.no 가 null 이면 새 프리셋
// 입력 중에는 이 컴포넌트 안에서만 값을 들고 있다가, 저장할 때 서버에 보냄
export default function PresetEditor({ preset, slots, onSaved, onDeleted, onCancel }) {
  const isNew = preset.no == null
  const [name, setName] = useState(preset.name)
  // 양은 입력칸 글자 그대로 들고 있다가 저장할 때 숫자로 바꿈 (지우는 중에 0 이 박히지 않게)
  const [items, setItems] = useState(preset.items.map((i) => ({ slot: i.slot, amount: String(i.amount) })))
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const ref = useRef(null)

  // 편집을 열면 화면을 편집 칸으로 옮김 (휴대폰에서는 아래쪽에 있어서)
  useEffect(() => {
    ref.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }, [])

  const filled = slots.filter((s) => s.supplement)
  const unused = filled.filter((s) => !items.some((i) => i.slot === s.no))

  const addItem = () => {
    if (unused.length === 0) return
    setItems([...items, { slot: unused[0].no, amount: '1' }])
  }
  const updateItem = (index, patch) =>
    setItems(items.map((item, i) => (i === index ? { ...item, ...patch } : item)))
  const removeItem = (index) => setItems(items.filter((_, i) => i !== index))

  const save = async (e) => {
    e.preventDefault()
    const body = {
      name: name.trim(),
      items: items.map((i) => ({ slot: Number(i.slot), amount: Number(i.amount) })),
    }
    // 서버도 검사하지만, 흔한 실수는 보내기 전에 알려 줌
    if (body.items.some((i) => !Number.isInteger(i.amount) || i.amount < 1)) {
      setError('양은 1 이상의 정수로 적어 주세요')
      return
    }
    setBusy(true)
    setError('')
    try {
      if (isNew) await api.createPreset(body)
      else await api.updatePreset(preset.no, body)
      await onSaved()
    } catch (err) {
      setError(err.message)
      setBusy(false)
    }
  }

  const remove = async () => {
    if (!window.confirm(`'${preset.name}' 프리셋을 지울까요?`)) return
    setBusy(true)
    setError('')
    try {
      await api.deletePreset(preset.no)
      await onDeleted()
    } catch (err) {
      setError(err.message)
      setBusy(false)
    }
  }

  return (
    <section className="section" aria-labelledby="editor-title" ref={ref}>
      <div className="section__head">
        <div>
          <p className="eyebrow">{isNew ? 'New stack' : 'Edit stack'}</p>
          <h2 id="editor-title" className="section__title">{isNew ? '새 프리셋' : '프리셋 편집'}</h2>
        </div>
      </div>

      <form className="editor" onSubmit={save}>
        <label className="field">
          <span className="field__label">이름</span>
          <input
            className="input input--name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="예: 아침"
            required
          />
        </label>

        <fieldset className="field">
          <legend className="field__label">담을 것</legend>
          <div className="editor__rows">
            {items.map((item, index) => {
              const slot = slots.find((s) => s.no === item.slot)
              // 고를 수 있는 칸: 채워진 칸 + 지금 고른 칸(그사이 비워졌어도 보이게)
              const options = slots.filter((s) => s.supplement || s.no === item.slot)
              return (
                <div key={index} className={`editor__row is-${slot?.kind}`}>
                  <span className="select">
                    <select
                      className="input"
                      value={item.slot}
                      onChange={(e) => updateItem(index, { slot: Number(e.target.value) })}
                      aria-label="칸"
                    >
                      {options.map((s) => (
                        <option
                          key={s.no}
                          value={s.no}
                          disabled={s.no !== item.slot && items.some((i) => i.slot === s.no)}
                        >
                          {s.no}번 · {s.supplement ?? '빈 칸'} ({kindLabel(s.kind)})
                        </option>
                      ))}
                    </select>
                  </span>
                  <span className="input-unit">
                    <input
                      className="input input--num"
                      type="number"
                      inputMode="numeric"
                      min="1"
                      step="1"
                      value={item.amount}
                      onChange={(e) => updateItem(index, { amount: e.target.value })}
                      aria-label="양"
                      required
                    />
                    <span aria-hidden="true">{unit(slot?.kind)}</span>
                  </span>
                  <button
                    className="btn btn--icon"
                    type="button"
                    aria-label="항목 삭제"
                    onClick={() => removeItem(index)}
                  >
                    <CloseIcon />
                  </button>
                </div>
              )
            })}
          </div>
          <button className="btn btn--add" type="button" onClick={addItem} disabled={unused.length === 0}>
            <PlusIcon />
            {unused.length === 0 ? '더 넣을 칸이 없어요' : '항목 추가'}
          </button>
          <p className="note">가루는 g, 알약은 개수예요. 기계가 정수만 읽어서 소수점은 안 돼요.</p>
        </fieldset>

        {error && <p className="form-error" role="alert">{error}</p>}

        <div className="editor__actions">
          {!isNew && (
            <button className="btn btn--text btn--danger" type="button" onClick={remove} disabled={busy}>
              프리셋 삭제
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
