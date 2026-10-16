import { useState } from "react";
import { unit } from "../format";
import { PlusIcon, ArrowIcon } from "./Icons";

function PresetCard({ preset, slots, editing, onDispense, onEdit }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const dispense = async () => {
    setBusy(true);
    setError("");
    try {
      await onDispense(preset.no);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <li className={`stack${editing ? " stack--editing" : ""}`}>
      <div className="stack__body">
        <div className="stack__head">
          <h3 className="stack__name">{preset.name}</h3>
          <span className="stack__count">{preset.items.length}종</span>
        </div>
        <ul className="stack__items">
          {preset.items.map((item) => {
            const slot = slots.find((s) => s.no === item.slot);
            return (
              <li key={item.slot} className={`stack__item is-${slot?.kind}`}>
                <span className="stack__supp">
                  {slot?.supplement ?? "빈 칸"}
                </span>
                <span className="stack__amount">
                  {item.amount}
                  <small>{unit(slot?.kind)}</small>
                </span>
              </li>
            );
          })}
        </ul>
        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}
      </div>

      <div className="stack__actions">
        <button
          className="btn btn--go"
          type="button"
          onClick={dispense}
          disabled={busy || preset.items.length === 0}
        >
          {busy ? "요청 중…" : "담기"}
          <ArrowIcon />
        </button>
        <button
          className="btn btn--text"
          type="button"
          aria-pressed={editing}
          onClick={() => onEdit(preset)}
        >
          편집
        </button>
      </div>
    </li>
  );
}

export default function PresetList({ presets, slots, editingNo, onDispense, onEdit, onNew }) {
  return (
    <section className="section" aria-labelledby="presets-title">
      <div className="section__head">
        <div>
          <p className="eyebrow">Stacks</p>
          <h2 id="presets-title" className="section__title">
            프리셋
          </h2>
        </div>
        <button className="btn btn--line" type="button" onClick={onNew}>
          <PlusIcon />새 프리셋
        </button>
      </div>

      {presets.length === 0 ? (
        <p className="note">프리셋이 없어요. 새 프리셋을 만들어 보세요.</p>
      ) : (
        <ul className="stacks">
          {presets.map((p) => (
            <PresetCard
              key={p.no}
              preset={p}
              slots={slots}
              editing={editingNo === p.no}
              onDispense={onDispense}
              onEdit={onEdit}
            />
          ))}
        </ul>
      )}
    </section>
  );
}
