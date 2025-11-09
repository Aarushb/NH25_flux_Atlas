import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface DataPoint {
  value: number;
  timestamp: number;
}

export function CustomD3Chart() {
  const svgRef = useRef<SVGSVGElement>(null);
  const [data, setData] = useState<DataPoint[]>(() =>
    Array.from({ length: 20 }, (_, i) => ({
      value: 200 + Math.random() * 100,
      timestamp: Date.now() - (19 - i) * 1000,
    }))
  );

  const WINDOW_SIZE = 20;
  const width = 800;
  const height = 300;
  const margin = { top: 20, right: 30, bottom: 30, left: 50 };

  useEffect(() => {
    const generateNext = (latest: number) => {
      const delta = (Math.random() - 0.5) * 30;
      return Math.max(50, Math.min(400, latest + delta));
    };

    const interval = setInterval(() => {
      setData((prevData) => {
        const newPoint: DataPoint = {
          value: generateNext(prevData[prevData.length - 1].value),
          timestamp: Date.now(),
        };
        return [...prevData.slice(-(WINDOW_SIZE - 1)), newPoint];
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    const g = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Scales
    const xScale = d3
      .scaleLinear()
      .domain([0, WINDOW_SIZE - 1])
      .range([0, chartWidth]);

    const yScale = d3
      .scaleLinear()
      .domain([0, 400]) // Fixed scale from 0 to 400
      .range([chartHeight, 0]);

    // Area generator
    const area = d3
      .area<DataPoint>()
      .x((_, i) => xScale(i))
      .y0(chartHeight)
      .y1((d) => yScale(d.value))
      .curve(d3.curveLinear);

    // Line generator
    const line = d3
      .line<DataPoint>()
      .x((_, i) => xScale(i))
      .y((d) => yScale(d.value))
      .curve(d3.curveLinear);

    // Draw area with gradient
    const gradient = svg
      .append("defs")
      .append("linearGradient")
      .attr("id", "area-gradient")
      .attr("x1", "0%")
      .attr("y1", "0%")
      .attr("x2", "0%")
      .attr("y2", "100%");

    gradient
      .append("stop")
      .attr("offset", "0%")
      .attr("stop-color", "#2563eb")
      .attr("stop-opacity", 0.6);

    gradient
      .append("stop")
      .attr("offset", "100%")
      .attr("stop-color", "#2563eb")
      .attr("stop-opacity", 0.1);

    // Render area with smooth transition
    const areaPath = g
      .append("path")
      .datum(data)
      .attr("fill", "url(#area-gradient)")
      .attr("d", area);

    // Render line with smooth transition
    const linePath = g
      .append("path")
      .datum(data)
      .attr("fill", "none")
      .attr("stroke", "#2563eb")
      .attr("stroke-width", 2)
      .attr("d", line);

    // Animate smoothly using D3 transitions
    areaPath.transition().duration(800).ease(d3.easeLinear).attr("d", area);

    linePath.transition().duration(800).ease(d3.easeLinear).attr("d", line);

    // Axes
    const xAxis = d3.axisBottom(xScale).ticks(5);
    const yAxis = d3.axisLeft(yScale).ticks(5);

    g.append("g")
      .attr("transform", `translate(0,${chartHeight})`)
      .call(xAxis)
      .attr("color", "#94a3b8");

    g.append("g").call(yAxis).attr("color", "#94a3b8");

    // Grid lines
    g.append("g")
      .attr("class", "grid")
      .attr("opacity", 0.1)
      .call(
        d3
          .axisLeft(yScale)
          .ticks(5)
          .tickSize(-chartWidth)
          .tickFormat(() => "")
      );
  }, [data, margin.top, margin.left, margin.right, margin.bottom, WINDOW_SIZE]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          Live Stock Chart - Current Value: $
          {data[data.length - 1].value.toFixed(2)}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <svg
          ref={svgRef}
          width={width}
          height={height}
          style={{ maxWidth: "100%", height: "auto" }}
        />
      </CardContent>
    </Card>
  );
}
