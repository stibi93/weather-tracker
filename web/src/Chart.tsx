import { useEffect, useRef } from "react";
import uPlot from "uplot";
import "uplot/dist/uPlot.min.css";
import { theme } from "./theme";

export type Point = {
  date: string;
  value_cm: number;
  precip_mm: number | null;
  discharge_m3s: number | null;
  resolution?: string;
};

export type Metric = "level" | "discharge";

const HU_DATE = new Intl.DateTimeFormat("hu-HU", { year: "numeric", month: "short", day: "numeric" });
const PRECIP = "rgba(74, 122, 150, 0.38)";
const UNIT: Record<Metric, string> = { level: "cm", discharge: "m³/s" };

function mainValue(p: Point, metric: Metric): number | null {
  return metric === "discharge" ? p.discharge_m3s : p.value_cm;
}

// Kurzor-tooltip: a hoverelt pont dátuma, fő metrikája (cm vagy m³/s) és csapadéka (mm).
function cursorTooltip(unit: string): uPlot.Plugin {
  let tip: HTMLDivElement;
  return {
    hooks: {
      init: (u) => {
        tip = document.createElement("div");
        tip.className = "chart-tip";
        tip.style.display = "none";
        u.over.appendChild(tip);
      },
      setCursor: (u) => {
        const idx = u.cursor.idx;
        const left = u.cursor.left ?? -1;
        const top = u.cursor.top ?? -1;
        const main = idx != null ? u.data[2][idx] : null;
        if (idx == null || left < 0 || main == null) {
          tip.style.display = "none";
          return;
        }
        const date = HU_DATE.format(new Date((u.data[0][idx] as number) * 1000));
        const mm = u.data[1][idx];
        const precipRow = mm == null ? "" : `<span class="t-precip">${mm} mm csapadék</span>`;
        tip.innerHTML = `<span class="t-date">${date}</span><span class="t-val">${main} ${unit}</span>${precipRow}`;
        tip.style.display = "block";
        tip.style.left = `${left}px`;
        tip.style.top = `${top}px`;
      },
    },
  };
}

// Vékony React-wrapper az imperatív uPlot köré (canvas, sok pontra is gyors).
export function Chart({
  points,
  width,
  height,
  metric = "level",
}: {
  points: Point[];
  width: number;
  height: number;
  metric?: Metric;
}) {
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!ref.current) return;

    const xs = points.map((p) => Date.parse(p.date) / 1000);
    const precip = points.map((p) => p.precip_mm);
    const main = points.map((p) => mainValue(p, metric));

    const opts: uPlot.Options = {
      width,
      height,
      legend: { show: false },
      cursor: { y: false, points: { size: 7 } },
      plugins: [cursorTooltip(UNIT[metric])],
      scales: {
        x: { time: true },
        y: {},
        mm: { range: (_u, _min, max) => [0, Math.max(max ?? 1, 1)] },
      },
      axes: [
        {
          stroke: theme.inkSoft,
          grid: { show: false },
          ticks: { stroke: theme.line, width: 1 },
          font: "11px Inter, system-ui, sans-serif",
        },
        {
          scale: "y",
          stroke: theme.inkSoft,
          grid: { stroke: theme.line, width: 1 },
          ticks: { show: false },
          size: 50,
          font: "11px Inter, system-ui, sans-serif",
          values: (_u, vals) => vals.map((v) => `${v}`),
        },
        {
          scale: "mm",
          side: 1,
          stroke: "#4a7a96",
          grid: { show: false },
          ticks: { show: false },
          size: 40,
          font: "11px Inter, system-ui, sans-serif",
          values: (_u, vals) => vals.map((v) => `${v}`),
        },
      ],
      series: [
        {},
        {
          scale: "mm",
          paths: uPlot.paths.bars!({ size: [0.7, 18], align: 0 }),
          points: { show: false },
          fill: PRECIP,
          stroke: PRECIP,
          width: 0,
        },
        {
          scale: "y",
          stroke: theme.lake,
          width: 2,
          fill: "rgba(63, 143, 135, 0.10)",
          points: { show: false },
        },
      ],
    };

    const u = new uPlot(opts, [xs, precip, main], ref.current);
    return () => u.destroy();
  }, [points, width, height, metric]);

  return <div ref={ref} className="chart" />;
}
