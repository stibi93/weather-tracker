import { useEffect, useState } from "react";
import { Chart, type Metric, type Point, type Secondary } from "./Chart";

type Doc = {
  id: string;
  name: string;
  station: string;
  unit: string;
  source: string;
  latest: { date: string; value_cm: number } | null;
  series: Point[];
};

const RANGES: { label: string; years: number | null }[] = [
  { label: "1 év", years: 1 },
  { label: "5 év", years: 5 },
  { label: "Teljes", years: null },
];

const NORMAL_SIZE = { w: 400, h: 260 };

function bigSize() {
  const vw = typeof window !== "undefined" ? window.innerWidth : 1200;
  return { w: Math.max(320, Math.min(vw - 140, 900)), h: 460 };
}

export function DetailPanel({ id, onClose }: { id: string; onClose: () => void }) {
  const [doc, setDoc] = useState<Doc | null>(null);
  const [rangeYears, setRangeYears] = useState<number | null>(5);
  const [metric, setMetric] = useState<Metric>("level");
  const [secondary, setSecondary] = useState<Secondary>("precip");
  const [expanded, setExpanded] = useState(false);
  const [big, setBig] = useState(bigSize);

  useEffect(() => {
    let cancelled = false;
    setDoc(null);
    setMetric("level");
    fetch(`${import.meta.env.BASE_URL}data/water-levels/${id}.json`)
      .then((r) => r.json())
      .then((d) => {
        if (!cancelled) setDoc(d);
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  useEffect(() => {
    if (!expanded) return;
    setBig(bigSize());
    const onResize = () => setBig(bigSize());
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, [expanded]);

  const size = expanded ? big : NORMAL_SIZE;
  const cutoff = rangeYears ? Date.now() - rangeYears * 365 * 864e5 : 0;
  const points = doc ? doc.series.filter((p) => Date.parse(p.date) >= cutoff) : [];
  const hasDischarge = doc?.series.some((p) => p.discharge_m3s != null) ?? false;

  const lastPoint = doc?.series[doc.series.length - 1];
  const headline =
    metric === "discharge"
      ? lastPoint?.discharge_m3s != null
        ? `${lastPoint.discharge_m3s} m³/s`
        : "—"
      : doc?.latest
        ? `${doc.latest.value_cm} cm`
        : "—";
  const mainLabel = metric === "discharge" ? "Vízhozam (m³/s)" : "Vízállás (cm)";

  return (
    <aside className={`panel detail${expanded ? " detail--expanded" : ""}`}>
      <button
        className="detail-resize"
        onClick={() => setExpanded((e) => !e)}
        aria-label={expanded ? "Kisebb nézet" : "Nagyobb nézet"}
        title={expanded ? "Kisebb" : "Nagyobb"}
      >
        {expanded ? "⤡" : "⤢"}
      </button>
      <button className="detail-close" onClick={onClose} aria-label="Bezárás">
        ×
      </button>

      {!doc ? (
        <p className="detail-loading">Betöltés…</p>
      ) : (
        <>
          <h2>{doc.name}</h2>
          <div className="detail-latest">
            <span className="value">{headline}</span>
            <span className="date">{doc.latest?.date ?? ""}</span>
          </div>

          {hasDischarge && (
            <div className="metric-switch">
              <button
                className={metric === "level" ? "active" : ""}
                onClick={() => setMetric("level")}
              >
                Vízállás
              </button>
              <button
                className={metric === "discharge" ? "active" : ""}
                onClick={() => setMetric("discharge")}
              >
                Vízhozam
              </button>
            </div>
          )}

          <div className="metric-switch">
            <button
              className={secondary === "precip" ? "active" : ""}
              onClick={() => setSecondary("precip")}
            >
              Csapadék
            </button>
            <button
              className={secondary === "temp" ? "active" : ""}
              onClick={() => setSecondary("temp")}
            >
              Hőmérséklet
            </button>
            <button
              className={secondary === "et0" ? "active" : ""}
              onClick={() => setSecondary("et0")}
            >
              Párolgás
            </button>
          </div>

          <div className="ranges">
            {RANGES.map((r) => (
              <button
                key={r.label}
                className={rangeYears === r.years ? "active" : ""}
                onClick={() => setRangeYears(r.years)}
              >
                {r.label}
              </button>
            ))}
          </div>

          <Chart points={points} width={size.w} height={size.h} metric={metric} secondary={secondary} />

          <div className="chart-legend">
            <span className="cl-line" /> {mainLabel}
            {secondary === "precip" && (
              <>
                <span className="cl-bar" /> Csapadék (mm)
              </>
            )}
            {secondary === "temp" && (
              <>
                <span className="cl-line cl-temp" /> Hőmérséklet (°C)
              </>
            )}
            {secondary === "et0" && (
              <>
                <span className="cl-line cl-et0" /> Párolgás (mm)
              </>
            )}
          </div>

          <p className="detail-src">
            {doc.station} · {doc.source}
          </p>
        </>
      )}
    </aside>
  );
}
