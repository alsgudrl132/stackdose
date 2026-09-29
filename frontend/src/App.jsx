import "./App.css";
import { device, dispense } from "./data/mock";
import { Mark } from "./components/Icons";
import DeviceStatus from "./components/DeviceStatus";
import SlotGrid from "./components/SlotGrid";
import PresetList from "./components/PresetList";
import PresetEditor from "./components/PresetEditor";
import DispensePanel from "./components/DispensePanel";
import { useEffect, useState } from "react";

export default function App() {
  const [slots, setSlots] = useState([]);
  const [presets, setPresets] = useState([]);

  const getSlots = async () => {
    const res = await fetch("http://localhost:8000/slots");
    const data = await res.json();
    setSlots(data);
  };

  const getPresets = async () => {
    const res = await fetch("http://localhost:8000/presets");
    const data = await res.json();
    setPresets(data);
  };

  useEffect(() => {
    getSlots();
    getPresets();
  }, []);

  return (
    <div className="app">
      <header className="topbar">
        <h1 className="brand">
          <Mark />
          <span>stackdose</span>
        </h1>
        <DeviceStatus device={device} />
      </header>

      <main className="layout">
        {/* 매일 쓰는 것: 지금 담는 것 → 프리셋 */}
        <div className="layout__main">
          <DispensePanel dispense={dispense} slots={slots} />
          <PresetList presets={presets} slots={slots} />
        </div>

        {/* 가끔 보는 것: 남은 양, 프리셋 고치기 */}
        <div className="layout__side">
          <SlotGrid slots={slots} />
          {presets[0] && <PresetEditor preset={presets[0]} slots={slots} />}
        </div>
      </main>
    </div>
  );
}
