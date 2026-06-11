import { MapView } from "./MapView";
import { theme } from "./theme";

export function App() {
  return (
    <div className="app">
      <MapView />

      <header className="panel header">
        <h1>Magyar vízállás-térkép</h1>
        <p>Nagy tavak és folyók aktuális vízállása · vidd a kurzort egy víztest fölé</p>
      </header>

      <div className="panel legend">
        <span className="legend-row">
          <span className="dot" style={{ background: theme.lake }} /> Tó
        </span>
        <span className="legend-row">
          <span className="dot" style={{ background: theme.river }} /> Folyó
        </span>
      </div>

      <footer className="attribution">
        Forrás: Országos Vízügyi Főigazgatóság
      </footer>
    </div>
  );
}
