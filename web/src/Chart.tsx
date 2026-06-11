import { useEffect, useRef } from "react";
import uPlot from "uplot";
import "uplot/dist/uPlot.min.css";
import { theme } from "./theme";

export type Point = { date: string; value_cm: number; resolution?: string };

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
      cursor: { y: false, points: { size: 6 } },
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
          size: 42,
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
          value: (_u, v) => (v == null ? "—" : `${v} cm`),
        },
      ],
    };

    const u = new uPlot(opts, [xs, ys], ref.current);
    return () => u.destroy();
  }, [points, width, height]);

  return <div ref={ref} className="chart" />;
}
