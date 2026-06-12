import { useEffect, useState } from "react";
import { Chart, type Point } from "./Chart";

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
  const [expanded, setExpanded] = useState(false);
  const [big, setBig] = useState(bigSize);

  useEffect(() => {
    if (!expanded) return;
    setBig(bigSize());
    const onResize = () => setBig(bigSize());
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, [expanded]);

  const size = expanded ? big : NORMAL_SIZE;

  useEffect(() => {
    let cancelled = false;
    setDoc(null);
    fetch(`${import.meta.env.BASE_URL}data/water-levels/${id}.json`)
      .then((r) => r.json())
      .then((d) => {
        if (!cancelled) setDoc(d);
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  const cutoff = rangeYears ? Date.now() - rangeYears * 365 * 864e5 : 0;
  const points = doc ? doc.series.filter((p) => Date.parse(p.date) >= cutoff) : [];

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
            <span className="value">{doc.latest ? `${doc.latest.value_cm} cm` : "—"}</span>
            <span className="date">{doc.latest?.date ?? ""}</span>
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

          <Chart points={points} width={size.w} height={size.h} />

          <div className="chart-legend">
            <span className="cl-line" /> Vízállás (cm)
            <span className="cl-bar" /> Csapadék (mm)
          </div>

          <p className="detail-src">
            {doc.station} · {doc.source}
          </p>
        </>
      )}
    </aside>
  );
}
