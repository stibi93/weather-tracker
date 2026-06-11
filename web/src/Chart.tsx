import { useEffect, useRef } from "react";
import uPlot from "uplot";
import "uplot/dist/uPlot.min.css";
import { theme } from "./theme";

export type Point = { date: string; value_cm: number; resolution?: string };

const HU_DATE = new Intl.DateTimeFormat("hu-HU", { year: "numeric", month: "short", day: "numeric" });

// Kurzor-tooltip plugin: a hoverelt pont dátuma + pontos cm-értéke, a kurzorhoz igazítva.
function cursorTooltip(): uPlot.Plugin {
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
        const yv = idx != null ? u.data[1][idx] : null;
        if (idx == null || left < 0 || yv == null) {
          tip.style.display = "none";
          return;
        }
        const date = HU_DATE.format(new Date((u.data[0][idx] as number) * 1000));
        tip.innerHTML = `<span class="t-date">${date}</span><span class="t-val">${yv} cm</span>`;
        tip.style.display = "block";
        tip.style.left = `${left}px`;
        tip.style.top = `${top}px`;
      },
    },
  };
}

// Vékony React-wrapper az imperatív uPlot köré (canvas, sok pontra is gyors).
export function Chart({ points, width, height }: { points: Point[]; width: number; height: number }) {
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!ref.current) return;

    const xs = points.map((p) => Date.parse(p.date) / 1000);
    const ys = points.map((p) => p.value_cm);

    const opts: uPlot.Options = {
      width,
      height,
      legend: { show: false },
      cursor: { y: false, points: { size: 7 } },
      plugins: [cursorTooltip()],
      scales: { x: { time: true } },
      axes: [
        {
          stroke: theme.inkSoft,
          grid: { show: false },
          ticks: { stroke: theme.line, width: 1 },
          font: "11px Inter, system-ui, sans-serif",
        },
        {
          stroke: theme.inkSoft,
          grid: { stroke: theme.line, width: 1 },
          ticks: { show: false },
          size: 44,
          font: "11px Inter, system-ui, sans-serif",
          values: (_u, vals) => vals.map((v) => `${v}`),
        },
      ],
      series: [
        {},
        {
          stroke: theme.lake,
          width: 2,
          fill: "rgba(63, 143, 135, 0.12)",
          points: { show: false },
        },
      ],
    };

    const u = new uPlot(opts, [xs, ys], ref.current);
    return () => u.destroy();
  }, [points, width, height]);

  return <div ref={ref} className="chart" />;
}
