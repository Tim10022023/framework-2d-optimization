import { useMemo } from "react";
import Plot from "react-plotly.js";
import type { Data, Layout } from "plotly.js";
import { createGrid, getBenchmarkDefinition } from "../lib/benchmarkFunctions";

type OverlayPoint = {
  x: number;
  y: number;
};

type Props = {
  functionId: string;
  height?: number;
  points?: OverlayPoint[];
};

export default function FunctionContourPlot({
  functionId,
  height = 300,
  points = [],
}: Props) {
  const def = getBenchmarkDefinition(functionId);
  const grid = useMemo(() => createGrid(functionId, 120), [functionId]);

  const data = useMemo<Data[]>(() => {
    if (!def || !grid) return [];

    const traces: Data[] = [
      {
        type: "contour",
        x: grid.xs,
        y: grid.ys,
        z: grid.z,
        contours: {
          coloring: "heatmap",
          showlabels: false,
        },
        colorbar: {
          title: {
            text: def.logScale ? "log(f+1)" : "f(x,y)",
          },
        },
        name: def.title,
      },
    ];

    if (points.length > 0) {
      traces.push({
        type: "scatter",
        mode: "lines+markers",
        x: points.map((p) => p.x),
        y: points.map((p) => p.y),
        marker: { size: 7, color: "black" },
        line: { width: 2, color: "black" },
        name: "Pfad",
      } as Data);
    }

    return traces;
  }, [def, grid, points]);

  const layout = useMemo<Partial<Layout>>(() => {
    if (!def) return {};

    return {
      title: {
        text: def.title,
        font: { size: 14 },
      },
      height,
      margin: { l: 50, r: 20, t: 40, b: 45 },
      xaxis: { title: { text: "x" } },
      yaxis: {
        title: { text: "y" },
        scaleanchor: "x",
        scaleratio: 1,
      },
      showlegend: points.length > 0,
      uirevision: `contour-${functionId}`,
    };
  }, [def, functionId, height, points.length]);

  if (!def || !grid) return null;

  return (
    <div style={{ marginTop: 0 }}>
      <Plot
        data={data}
        layout={layout}
        style={{ width: "100%" }}
        config={{ responsive: true, displayModeBar: false }}
      />
    </div>
  );
}
