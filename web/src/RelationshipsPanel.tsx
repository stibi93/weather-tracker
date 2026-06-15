import { useEffect, useRef, useState } from "react";
import uPlot from "uplot";
import "uplot/dist/uPlot.min.css";
import { theme } from "./theme";

type Predictor = { label: string; lag_days: number; spearman_r: number | null };
type Primary = {
  title: string;
  x_label: string;
  y_label: string;
  r2: number | null;
  slope: number | null;
  intercept: number | null;
  n: number;
  points: [number, number][];
};
type Rel = { id: string; name: string; kind: string; primary: Primary; predictors: Predictor[] };

// Szórásdiagram + illesztett egyenes (uPlot; a pontokat x szerint rendezzük).
function Scatter({ primary, width, height }: { primary: Primary; width: number; height: number }) {
  const ref = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    if (!ref.current || primary.points.length < 2) return;
    const pts = [...primary.points].sort((a, b) => a[0] - b[0]);
    const xs = pts.map((p) => p[0]);
    const ys = pts.map((p) => p[1]);
    const slope = primary.slope ?? 0;
    const intercept = primary.intercept ?? 0;
    const line = xs.map((x) => slope * x + intercept);

    const opts: uPlot.Options = {
      width,
      height,
      legend: { show: false },
      cursor: { show: false },
      scales: { x: { time: false }, y: {} },
      axes: [
        {
          stroke: theme.inkSoft,
          grid: { stroke: theme.line, width: 1 },
          font: "11px Inter, system-ui, sans-serif",
          label: primary.x_label,
          labelSize: 28,
          labelFont: "11px Inter, system-ui, sans-serif",
        },
        {
          stroke: theme.inkSoft,
          grid: { stroke: theme.line, width: 1 },
          font: "11px Inter, system-ui, sans-serif",
          label: primary.y_label,
          labelSize: 30,
          labelFont: "11px Inter, system-ui, sans-serif",
          size: 52,
        },
      ],
      series: [
        {},
        {
          // szórás-pontok (vonal nélkül)
          paths: () => null,
          points: { show: true, size: 3, fill: "rgba(63,143,135,0.5)", stroke: "rgba(63,143,135,0.0)" },
        },
        {
          // illesztett egyenes
          stroke: "#b5562e",
          width: 2,
          points: { show: false },
        },
      ],
    };
    const u = new uPlot(opts, [xs, ys, line], ref.current);
    return () => u.destroy();
  }, [primary, width, height]);

  return <div ref={ref} className="scatter" />;
}

function rBar(r: number | null) {
  if (r == null) return <span className="r-na">—</span>;
  const pct = Math.min(Math.abs(r), 1) * 50;
  const pos = r >= 0;
  return (
    <span className="r-bar" title={`Spearman r = ${r}`}>
      <span className="r-track">
        <span
          className={`r-fill ${pos ? "pos" : "neg"}`}
          style={{ width: `${pct}%`, [pos ? "left" : "right"]: "50%" } as React.CSSProperties}
        />
      </span>
      <span className="r-num">{r > 0 ? `+${r.toFixed(2)}` : r.toFixed(2)}</span>
    </span>
  );
}

export function RelationshipsPanel({ id, width }: { id: string; width: number }) {
  const [rel, setRel] = useState<Rel | null>(null);
  useEffect(() => {
    let cancelled = false;
    setRel(null);
    fetch(`${import.meta.env.BASE_URL}data/relationships/${id}.json`)
      .then((r) => r.json())
      .then((d) => {
        if (!cancelled) setRel(d);
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  if (!rel) return <p className="detail-loading">Összefüggések betöltése…</p>;
  const r2 = rel.primary.r2;

  return (
    <div className="rel">
      <div className="rel-title">
        {rel.primary.title}
        {r2 != null && <span className="rel-r2">R² = {r2.toFixed(2)}</span>}
      </div>

      <Scatter primary={rel.primary} width={width} height={230} />

      <table className="rel-table">
        <thead>
          <tr>
            <th>Magyarázó változó (napi szintváltozásra)</th>
            <th>Késés</th>
            <th>Spearman r</th>
          </tr>
        </thead>
        <tbody>
          {rel.predictors.map((d) => (
            <tr key={d.label}>
              <td>{d.label}</td>
              <td>{d.lag_days} nap</td>
              <td>{rBar(d.spearman_r)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="rel-help">
        <p>
          <b>Δszint (napi szintváltozás):</b> a mai és tegnapi vízállás különbsége. Ezzel
          dolgozunk, mert a nyers vízszint felhalmozott állapot — nyersen korrelálva félrevezető
          (autokorreláció, szezonalitás).
        </p>
        <p>
          <b>Spearman r (−1…+1):</b> a rangkorreláció iránya és erőssége. +1 erős együttmozgás,
          −1 ellentétes, 0 nincs egyértelmű kapcsolat (kiugró értékekre robusztus).
        </p>
        <p>
          <b>Késés (nap):</b> hány nappal korábbi magyarázó változó magyarázza legjobban a mai
          szintváltozást
          (pl. eső 1–3 nap múlva emeli a szintet).
        </p>
        <p>
          <b>R² (0…1):</b> a fő kapcsolat mennyit magyaráz a szórásból. R²=0,20 ≈ a napi
          szintváltozás 20%-a; a többit szabályozás, talajvíz, mérési zaj adja.
        </p>
      </div>

      <p className="rel-caveat">
        ⚠️ <b>A korreláció nem okság.</b> Ezek statisztikai együttmozgások, nem bizonyított
        ok-okozat. A vízszintet a szabályozás (Sió-zsilip, kiskörei duzzasztó), a talajvíz és a
        felvízi folyamatok is befolyásolják, amelyeket itt nem modellezünk.
      </p>
    </div>
  );
}
