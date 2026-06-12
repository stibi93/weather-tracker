import { useEffect, useRef } from "react";
import uPlot from "uplot";
import "uplot/dist/uPlot.min.css";
import { theme } from "./theme";

export type Point = {
  date: string;
  value_cm: number;
  precip_mm: number | null;
  discharge_m3s: number | null;
  temp_c: number | null;
  resolution?: string;
};

export type Metric = "level" | "discharge";
export type Secondary = "precip" | "temp";

const HU_DATE = new Intl.DateTimeFormat("hu-HU", { year: "numeric", month: "short", day: "numeric" });
const PRECIP = "rgba(74, 122, 150, 0.38)";
const TEMP = theme.gold;
const UNIT: Record<Metric, string> = { level: "cm", discharge: "m³/s" };

function mainValue(p: Point, metric: Metric): number | null {
  return metric === "discharge" ? p.discharge_m3s : p.value_cm;
}
function secondaryValue(p: Point, secondary: Secondary): number | null {
  return secondary === "temp" ? p.temp_c : p.precip_mm;
}

// Kurzor-tooltip: dátum, fő metrika és aktív másodlagos érték (csapadék mm vagy hőmérséklet °C).
function cursorTooltip(mainUnit: string, secondary: Secondary): uPlot.Plugin {
  let tip: HTMLDivElement;
  const secText = (v: number) => (secondary === "temp" ? `${v} °C` : `${v} mm csapadék`);
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
        const sec = u.data[1][idx];
        const secRow = sec == null ? "" : `<span class="t-sec">${secText(sec)}</span>`;
        tip.innerHTML = `<span class="t-date">${date}</span><span class="t-val">${main} ${mainUnit}</span>${secRow}`;
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
  secondary = "precip",
}: {
  points: Point[];
  width: number;
  height: number;
  metric?: Metric;
  secondary?: Secondary;
}) {
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!ref.current) return;

    const xs = points.map((p) => Date.parse(p.date) / 1000);
    const sec = points.map((p) => secondaryValue(p, secondary));
    const main = points.map((p) => mainValue(p, metric));
    const isTemp = secondary === "temp";

    const secSeries: uPlot.Series = isTemp
      ? { scale: "sec", stroke: TEMP, width: 2, points: { show: false } }
      : {
          scale: "sec",
          paths: uPlot.paths.bars!({ size: [0.7, 18], align: 0 }),
          points: { show: false },
          fill: PRECIP,
          stroke: PRECIP,
          width: 0,
        };

    const opts: uPlot.Options = {
      width,
      height,
      legend: { show: false },
      cursor: { y: false, points: { size: 7 } },
      plugins: [cursorTooltip(UNIT[metric], secondary)],
      scales: {
        x: { time: true },
        y: {},
        sec: isTemp ? {} : { range: (_u, _min, max) => [0, Math.max(max ?? 1, 1)] },
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
          scale: "sec",
          side: 1,
          stroke: isTemp ? TEMP : "#4a7a96",
          grid: { show: false },
          ticks: { show: false },
          size: 40,
          font: "11px Inter, system-ui, sans-serif",
          values: (_u, vals) => vals.map((v) => `${v}`),
        },
      ],
      series: [
        {},
        secSeries,
        {
          scale: "y",
          stroke: theme.lake,
          width: 2,
          fill: "rgba(63, 143, 135, 0.10)",
          points: { show: false },
        },
      ],
    };

    const u = new uPlot(opts, [xs, sec, main], ref.current);
    return () => u.destroy();
  }, [points, width, height, metric, secondary]);

  return <div ref={ref} className="chart" />;
}
