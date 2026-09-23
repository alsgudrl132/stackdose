import { unit, kindLabel } from "../format";

// 화면 표시용 기준입니다. 실제 "부족" 규칙은 백엔드에서 정하세요.
const LOW = { powder: 50, pill: 10 };
// 막대 표시용: 부족 기준의 5배를 막대 끝으로 봅니다 (실제 통 용량이 아닙니다).
const SCALE = 5;

// 한 줄 전체가 버튼입니다 (빈 칸은 채우기, 찬 칸은 수정).
function SlotRow({ slot }) {
  const empty = !slot.supplement;
  const low = !empty && slot.remaining < LOW[slot.kind];
  const pct = empty
    ? 0
    : Math.min(100, (slot.remaining / (LOW[slot.kind] * SCALE)) * 100);
  const u = unit(slot.kind);

  const label = empty
    ? `${slot.no}번 ${kindLabel(slot.kind)} 칸 비어 있음, 채우기`
    : `${slot.no}번 ${slot.supplement} ${slot.remaining}${u} 남음${low ? ", 부족" : ""}, 수정`;

  return (
    <li>
      <button
        type="button"
        aria-label={label}
        className={`inv is-${slot.kind}${empty ? " inv--empty" : ""}${low ? " inv--low" : ""}`}
      >
        <span className="inv__no">{slot.no}</span>
        <span className="inv__name">
          {empty ? "비어 있음" : slot.supplement}
          {low && <span className="inv__flag">부족</span>}
        </span>
        <span className="inv__qty">
          {empty ? (
            <span className="inv__fill-cta">+ 채우기</span>
          ) : (
            <>
              {slot.remaining}
              <small>{u}</small>
            </>
          )}
        </span>
        <span className="inv__bar" aria-hidden="true">
          <span className="inv__level" style={{ width: `${pct}%` }} />
          <span className="inv__mark" style={{ left: `${100 / SCALE}%` }} />
        </span>
      </button>
    </li>
  );
}

export default function SlotGrid({ slots }) {
  const groups = [
    { kind: "powder", title: "가루", sub: "Powder · g" },
    { kind: "pill", title: "알약", sub: "Pills · 알" },
  ];
  const lowCount = slots.filter(
    (s) => s.supplement && s.remaining < LOW[s.kind],
  ).length;

  return (
    <section className="section" aria-labelledby="slots-title">
      <div className="section__head">
        <div>
          <p className="eyebrow">Inventory</p>
          <h2 id="slots-title" className="section__title">
            남은 양
          </h2>
        </div>
        {lowCount > 0 && <p className="section__alert">{lowCount}칸 부족</p>}
      </div>

      <div className="inventory">
        {groups.map((g) => (
          <div key={g.kind} className={`inventory__group is-${g.kind}`}>
            <h3 className="inventory__title">
              {g.title}
              <span>{g.sub}</span>
            </h3>
            <ul className="inventory__list">
              {slots
                .filter((s) => s.kind === g.kind)
                .map((s) => (
                  <SlotRow key={s.no} slot={s} />
                ))}
            </ul>
          </div>
        ))}
      </div>
      <p className="note">
        줄을 누르면 채우거나 고칩니다. 막대가 세로선 왼쪽으로 가면 부족입니다.
      </p>
    </section>
  );
}
