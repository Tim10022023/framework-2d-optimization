import { useMemo } from "react";
import Plot from "react-plotly.js";
import type { Data, Layout } from "plotly.js";
import { createGrid, getBenchmarkDefinition } from "../lib/benchmarkFunctions";

type OverlayPoint = {
  x: number;
  y: number;
  z?: number;
};

type Props = {
  functionId: string;
  height?: number;
  points?: OverlayPoint[];
};

export default function FunctionSurfacePlot({
  functionId,
  height = 320,
  points = [],
}: Props) {
  const def = getBenchmarkDefinition(functionId);
  const grid = useMemo(() => createGrid(functionId, 90), [functionId]);

  const data = useMemo<Data[]>(() => {
    if (!def || !grid) return [];

    const traces: Data[] = [
      {
        type: "surface",
        x: grid.xs,
        y: grid.ys,
        z: grid.z,
        showscale: true,
        name: def.title,
      } as Data,
    ];

    if (points.length > 0) {
      traces.push({
        type: "scatter3d",
        mode: "lines+markers",
        x: points.map((p) => p.x),
        y: points.map((p) => p.y),
        z: points.map((p) => p.z ?? 0),
        marker: {
          size: 4,
          color: "black",
        },
        line: {
          width: 4,
          color: "black",
        },
        name: "Pfad",
      } as Data);
    }

    return traces;
  }, [def, grid, points]);

  const layout = useMemo<Partial<Layout>>(() => {
    if (!def) return {};

    return {
      title: {
        text: `${def.title} – 3D-Oberflächenplot`,
        font: { size: 14 },
      },
      height,
      margin: { l: 0, r: 0, t: 40, b: 0 },
      scene: {
        xaxis: { title: { text: "x" } },
        yaxis: { title: { text: "y" } },
        zaxis: { title: { text: def.logScale ? "log(f+1)" : "f(x,y)" } },
        camera: {
          eye: { x: 1.5, y: 1.4, z: 0.9 },
        },
      },
      showlegend: points.length > 0,
      uirevision: `surface-${functionId}`,
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
