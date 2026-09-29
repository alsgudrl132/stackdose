import { unit } from "../format";
import { PlusIcon, ArrowIcon } from "./Icons";

function PresetCard({ preset, slots }) {
  const postDispense = async (no) => {
    const res = await fetch(`http://localhost:8000/presets/${no}/dispense`, {
      method: "POST",
    });
    const data = await res.json();
    console.log(data);
  };

  return (
    <li className="stack">
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
      </div>

      <div className="stack__actions">
        <button
          className="btn btn--go"
          type="button"
          onClick={() => postDispense(preset.no)}
        >
          담기
          <ArrowIcon />
        </button>
        <button className="btn btn--text" type="button">
          편집
        </button>
      </div>
    </li>
  );
}

export default function PresetList({ presets, slots }) {
  return (
    <section className="section" aria-labelledby="presets-title">
      <div className="section__head">
        <div>
          <p className="eyebrow">Stacks</p>
          <h2 id="presets-title" className="section__title">
            프리셋
          </h2>
        </div>
        <button className="btn btn--line" type="button">
          <PlusIcon />새 프리셋
        </button>
      </div>

      <ul className="stacks">
        {presets.map((p) => (
          <PresetCard key={p.no} preset={p} slots={slots} />
        ))}
      </ul>
    </section>
  );
}
