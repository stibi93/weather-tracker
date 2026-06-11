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

export function DetailPanel({ id, onClose }: { id: string; onClose: () => void }) {
  const [doc, setDoc] = useState<Doc | null>(null);
  const [rangeYears, setRangeYears] = useState<number | null>(5);

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
    <aside className="panel detail">
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

          <Chart points={points} width={336} height={200} />

          <p className="detail-src">
            {doc.station} · {doc.source}
          </p>
        </>
      )}
    </aside>
  );
}
