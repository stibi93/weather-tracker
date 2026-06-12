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
  et0_mm: number | null;
  resolution?: string;
};

export type Metric = "level" | "discharge";
export type Secondary = "precip" | "temp" | "et0";

const HU_DATE = new Intl.DateTimeFormat("hu-HU", { year: "numeric", month: "short", day: "numeric" });
const UNIT: Record<Metric, string> = { level: "cm", discharge: "m³/s" };

type SecConfig = {
  value: (p: Point) => number | null;
  kind: "bars" | "line";
  color: string;
  zeroBased: boolean;
  text: (v: number) => string;
};

const SECONDARY: Record<Secondary, SecConfig> = {
  precip: {
    value: (p) => p.precip_mm,
    kind: "bars",
    color: "#4a7a96",
    zeroBased: true,
    text: (v) => `${v} mm csapadék`,
  },
  temp: {
    value: (p) => p.temp_c,
    kind: "line",
    color: theme.gold,
    zeroBased: false,
    text: (v) => `${v} °C`,
  },
  et0: {
    value: (p) => p.et0_mm,
    kind: "line",
    color: "#b5562e",
    zeroBased: true,
    text: (v) => `${v} mm párolgás`,
  },
};

// Kurzor-tooltip: dátum, fő metrika és aktív másodlagos érték.
function cursorTooltip(mainUnit: string, secText: (v: number) => string): uPlot.Plugin {
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
    const cfg = SECONDARY[secondary];

    const xs = points.map((p) => Date.parse(p.date) / 1000);
    const sec = points.map((p) => cfg.value(p));
    const main = points.map((p) => (metric === "discharge" ? p.discharge_m3s : p.value_cm));

    const secSeries: uPlot.Series =
      cfg.kind === "line"
        ? { scale: "sec", stroke: cfg.color, width: 2, points: { show: false } }
        : {
            scale: "sec",
            paths: uPlot.paths.bars!({ size: [0.7, 18], align: 0 }),
            points: { show: false },
            fill: "rgba(74, 122, 150, 0.38)",
            stroke: "rgba(74, 122, 150, 0.38)",
            width: 0,
          };

    const opts: uPlot.Options = {
      width,
      height,
      legend: { show: false },
      cursor: { y: false, points: { size: 7 } },
      plugins: [cursorTooltip(UNIT[metric], cfg.text)],
      scales: {
        x: { time: true },
        y: {},
        sec: cfg.zeroBased ? { range: (_u, _min, max) => [0, Math.max(max ?? 1, 1)] } : {},
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
          stroke: cfg.color,
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
