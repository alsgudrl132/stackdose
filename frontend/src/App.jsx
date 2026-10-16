import "./App.css";
import { useCallback, useEffect, useState } from "react";
import { api } from "./api";
import { Mark } from "./components/Icons";
import DeviceStatus from "./components/DeviceStatus";
import SlotGrid from "./components/SlotGrid";
import SlotEditor from "./components/SlotEditor";
import PresetList from "./components/PresetList";
import PresetEditor from "./components/PresetEditor";
import DispensePanel from "./components/DispensePanel";

// 기계 상태와 지금 담는 것을 몇 ms 마다 다시 물어볼지 (기계가 서버에 묻는 주기와 같게)
const POLL_MS = 2000;

const NEW_PRESET = { no: null, name: "", items: [] };

export default function App() {
  const [slots, setSlots] = useState([]);
  const [presets, setPresets] = useState([]);
  const [device, setDevice] = useState(null);
  const [current, setCurrent] = useState(null); // 가장 최근 담기 요청 (없으면 null)
  const [serverDown, setServerDown] = useState(false);
  const [editingPreset, setEditingPreset] = useState(null); // 편집 중인 프리셋 (새 프리셋이면 NEW_PRESET)
  const [editingSlotNo, setEditingSlotNo] = useState(null);

  const loadSlots = useCallback(async () => setSlots(await api.slots()), []);
  const loadPresets = useCallback(async () => setPresets(await api.presets()), []);

  // 기계 상태 + 지금 담는 것. 서버가 꺼져 있으면 위쪽 상태에 표시
  const poll = useCallback(async () => {
    try {
      const [d, c] = await Promise.all([api.device(), api.currentDispense()]);
      setDevice(d);
      setCurrent(c);
      setServerDown(false);
    } catch {
      setServerDown(true);
    }
  }, []);

  useEffect(() => {
    Promise.all([loadSlots(), loadPresets()]).catch(() => setServerDown(true));
    poll();
    const timer = setInterval(poll, POLL_MS);
    return () => clearInterval(timer); // 화면이 사라지면 반복을 멈춤
  }, [loadSlots, loadPresets, poll]);

  // 담기가 끝나면 서버가 남은 양을 줄여 두니, 칸 목록을 다시 받음
  const currentDone = current?.status === "done" ? current.id : null;
  useEffect(() => {
    if (currentDone !== null) loadSlots().catch(() => {});
  }, [currentDone, loadSlots]);

  const startDispense = async (presetNo) => {
    await api.dispense(presetNo);
    await poll(); // 2초를 기다리지 않고 바로 패널에 보이게
  };

  const cancelDispense = async (id) => {
    await api.cancelDispense(id);
    await poll();
  };

  const closePresetEditor = () => setEditingPreset(null);
  const afterPresetChange = async () => {
    await loadPresets();
    closePresetEditor();
  };

  const editingSlot = slots.find((s) => s.no === editingSlotNo);
  const afterSlotChange = async () => {
    await loadSlots();
    setEditingSlotNo(null);
  };

  return (
    <div className="app">
      <header className="topbar">
        <h1 className="brand">
          <Mark />
          <span>stackdose</span>
        </h1>
        <DeviceStatus device={device} serverDown={serverDown} />
      </header>

      {serverDown && (
        <p className="banner" role="alert">
          서버에 연결할 수 없어요. backend 폴더에서 uvicorn 이 켜져 있는지 확인해 주세요.
        </p>
      )}

      <main className="layout">
        {/* 매일 쓰는 것: 지금 담는 것 → 프리셋 */}
        <div className="layout__main">
          <DispensePanel dispense={current} slots={slots} onCancel={cancelDispense} />
          <PresetList
            presets={presets}
            slots={slots}
            editingNo={editingPreset?.no}
            onDispense={startDispense}
            onEdit={setEditingPreset}
            onNew={() => setEditingPreset(NEW_PRESET)}
          />
        </div>

        {/* 가끔 보는 것: 남은 양, 프리셋 고치기 */}
        <div className="layout__side">
          {editingPreset && (
            <PresetEditor
              key={editingPreset.no ?? "new"}
              preset={editingPreset}
              slots={slots}
              onSaved={afterPresetChange}
              onDeleted={afterPresetChange}
              onCancel={closePresetEditor}
            />
          )}
          <SlotGrid
            slots={slots}
            selectedNo={editingSlotNo}
            onSelect={(no) => setEditingSlotNo(no === editingSlotNo ? null : no)}
          />
          {editingSlot && (
            <SlotEditor
              key={editingSlot.no}
              slot={editingSlot}
              onSaved={afterSlotChange}
              onCancel={() => setEditingSlotNo(null)}
            />
          )}
        </div>
      </main>
    </div>
  );
}
