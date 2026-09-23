import { unit, kindLabel } from '../format'
import { PlusIcon, CloseIcon } from './Icons'

// 마크업만 있습니다. 입력값 상태 관리와 저장은 직접 붙이세요.
export default function PresetEditor({ preset, slots }) {
  const filled = slots.filter((s) => s.supplement)

  return (
    <section className="section" aria-labelledby="editor-title">
      <div className="section__head">
        <div>
          <p className="eyebrow">Edit stack</p>
          <h2 id="editor-title" className="section__title">프리셋 편집</h2>
        </div>
      </div>

      <form className="editor" onSubmit={(e) => e.preventDefault()}>
        <label className="field">
          <span className="field__label">이름</span>
          <input className="input input--name" defaultValue={preset.name} />
        </label>

        <fieldset className="field">
          <legend className="field__label">담을 것</legend>
          <div className="editor__rows">
            {preset.items.map((item) => {
              const slot = slots.find((s) => s.no === item.slot)
              return (
                <div key={item.slot} className={`editor__row is-${slot?.kind}`}>
                  <span className="select">
                    <select className="input" defaultValue={item.slot} aria-label="칸">
                      {filled.map((s) => (
                        <option key={s.no} value={s.no}>
                          {s.no}번 · {s.supplement} ({kindLabel(s.kind)})
                        </option>
                      ))}
                    </select>
                  </span>
                  <span className="input-unit">
                    <input
                      className="input input--num"
                      type="number"
                      inputMode="decimal"
                      min="0"
                      step={slot?.kind === 'powder' ? '0.1' : '1'}
                      defaultValue={item.amount}
                      aria-label="양"
                    />
                    <span aria-hidden="true">{unit(slot?.kind)}</span>
                  </span>
                  <button className="btn btn--icon" type="button" aria-label="항목 삭제">
                    <CloseIcon />
                  </button>
                </div>
              )
            })}
          </div>
          <button className="btn btn--add" type="button">
            <PlusIcon />
            항목 추가
          </button>
        </fieldset>

        <div className="editor__actions">
          <button className="btn btn--text btn--danger" type="button">프리셋 삭제</button>
          <button className="btn btn--line" type="button">취소</button>
          <button className="btn btn--solid" type="submit">저장</button>
        </div>
      </form>
    </section>
  )
}
