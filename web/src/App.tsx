import { useState } from "react";
import { MapView } from "./MapView";
import { DetailPanel } from "./DetailPanel";
import { theme } from "./theme";

export function App() {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  return (
    <div className="app">
      <MapView onSelect={setSelectedId} selectedId={selectedId} />

      <header className="panel header">
        <h1>Magyar vízállás-térkép</h1>
        <p>Nagy tavak és folyók vízállása · kattints egy víztestre a többéves grafikonért</p>
      </header>

      <div className="panel legend">
        <span className="legend-row">
          <span className="dot" style={{ background: theme.lake }} /> Tó
        </span>
        <span className="legend-row">
          <span className="dot" style={{ background: theme.river }} /> Folyó
        </span>
      </div>

      {selectedId && <DetailPanel id={selectedId} onClose={() => setSelectedId(null)} />}

      <footer className="attribution">Forrás: Országos Vízügyi Főigazgatóság</footer>
    </div>
  );
}
