// ...existing code...
import { useEffect, useState } from "react";
import { Bar, BarChart } from "recharts";

import type { ChartConfig } from "@/components/ui/chart";
import { ChartContainer } from "@/components/ui/chart";

const chartData = [
  { month: "January", desktop: 186, mobile: 80 },
  { month: "February", desktop: 305, mobile: 200 },
  { month: "March", desktop: 237, mobile: 120 },
  { month: "April", desktop: 73, mobile: 190 },
  { month: "May", desktop: 209, mobile: 130 },
  { month: "June", desktop: 214, mobile: 140 },
  { month: "July", desktop: 180, mobile: 95 },
  { month: "August", desktop: 250, mobile: 160 },
  { month: "September", desktop: 195, mobile: 110 },
  { month: "October", desktop: 220, mobile: 150 },
  { month: "November", desktop: 170, mobile: 90 },
  { month: "December", desktop: 240, mobile: 170 },
];

const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "#2563eb",
  },
  mobile: {
    label: "Mobile",
    color: "#60a5fa",
  },
} satisfies ChartConfig;

export function Component() {
  const SLICE_LENGTH = 6;
  const [start, setStart] = useState(0);

  // Advance the window every second
  useEffect(() => {
    const id = setInterval(() => {
      setStart((s) => (s + 1) % chartData.length);
    }, 1000);
    return () => clearInterval(id);
  }, []);

  // Build a length-6 sliding window that wraps around the 12-month array
  const visibleData = Array.from({ length: SLICE_LENGTH }, (_, i) => {
    return chartData[(start + i) % chartData.length];
  });

  return (
    <ChartContainer config={chartConfig} className="min-h-[200px] w-full">
      <BarChart accessibilityLayer data={visibleData}>
        <Bar dataKey="desktop" fill="var(--color-desktop)" radius={4} />
        <Bar dataKey="mobile" fill="var(--color-mobile)" radius={4} />
      </BarChart>
    </ChartContainer>
  );
}
// ...existing code...
