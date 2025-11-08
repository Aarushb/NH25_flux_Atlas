// ...existing code...
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { TrendingUp } from "lucide-react";
import { Area, AreaChart } from "recharts";
import type { ChartConfig } from "@/components/ui/chart";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

export const description = "A linear area chart";

//

const startingData = [
  { desktop: 186 },
  { desktop: 305 },
  { desktop: 237 },
  { desktop: 73 },
  { desktop: 209 },
  { desktop: 214 },
  { desktop: 180 },
  { desktop: 250 },
  { desktop: 195 },
  { desktop: 220 },
  { desktop: 170 },
  { desktop: 240 },
  { desktop: 230 },
  { desktop: 225 },
  { desktop: 235 },
  { desktop: 210 },
  { desktop: 205 },
  { desktop: 215 },
  { desktop: 230 },
  { desktop: 225 },
];

const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "var(--chart-1)",
  },
} satisfies ChartConfig;

export function ChartAreaLinear() {
  const WINDOW_SIZE = 20;
  const TICK_MS = 1000;
  const ANIM_MS = 600;

  const containerRef = useRef<HTMLDivElement | null>(null);
  const dataQueueRef = useRef<{ desktop: number; timestamp: number }[]>(
    startingData.map((item, i) => ({
      desktop: item.desktop,
      timestamp: Date.now() + i * 1000,
    }))
  );

  const [containerWidth, setContainerWidth] = useState(0);
  const [animating, setAnimating] = useState(false);
  const [translate, setTranslate] = useState(0);
  const [renderData, setRenderData] = useState(() =>
    dataQueueRef.current.slice(-WINDOW_SIZE)
  );

  // measure container width (responsive)
  useLayoutEffect(() => {
    const measure = () => {
      const w = containerRef.current?.clientWidth ?? 0;
      setContainerWidth(w);
    };
    measure();
    const ro = new ResizeObserver(measure);
    if (containerRef.current) ro.observe(containerRef.current);
    window.addEventListener("resize", measure);
    return () => {
      ro.disconnect();
      window.removeEventListener("resize", measure);
    };
  }, []);

  // helper to compute pixel step (one-slot width) for scroll animation
  const stepPx = containerWidth ? containerWidth / WINDOW_SIZE : 0;
  const innerWidth = containerWidth
    ? (containerWidth * (WINDOW_SIZE + 1)) / WINDOW_SIZE
    : undefined;

  useEffect(() => {
    if (!containerWidth) return;

    // Generate a new random data point based on the latest value
    const DELTA_MIN = -15;
    const DELTA_MAX = 15;

    const generateNext = (latest: number): number => {
      const delta = Math.random() * (DELTA_MAX - DELTA_MIN) + DELTA_MIN;
      const next = latest + delta;
      return Math.max(50, Math.min(400, next));
    };

    const id = setInterval(() => {
      const queue = dataQueueRef.current;
      const latest = queue[queue.length - 1];
      const newValue = generateNext(latest.desktop);
      const newPoint = { desktop: newValue, timestamp: Date.now() };

      console.log(
        "Tick - adding new value:",
        newValue,
        "translate will be:",
        -stepPx
      );

      // Add new point to queue
      dataQueueRef.current = [...queue, newPoint];

      // Prepare animation: show last WINDOW_SIZE + 1 items (current window + new point)
      const toRender = dataQueueRef.current.slice(-(WINDOW_SIZE + 1));
      setRenderData(toRender);

      // Trigger scroll animation
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          console.log(
            "Starting animation, animating:",
            true,
            "translate:",
            -stepPx
          );
          setAnimating(true);
          setTranslate(-stepPx);
        });
      });
    }, TICK_MS);

    return () => clearInterval(id);
  }, [containerWidth, stepPx]);

  // transition end handler: reset animation state
  const onTransitionEnd = () => {
    console.log("Transition ended, animating:", animating);
    if (!animating) return;

    // Trim queue to keep only latest WINDOW_SIZE items
    dataQueueRef.current = dataQueueRef.current.slice(-WINDOW_SIZE);

    // Reset animation and show the trimmed window
    console.log("Resetting animation");
    setAnimating(false);
    setTranslate(0);
    setRenderData(dataQueueRef.current.slice(-WINDOW_SIZE));
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Area Chart - Linear</CardTitle>
        <CardDescription>
          Live stock price simulation - 20 second window
        </CardDescription>
        <div className="text-xs text-muted-foreground mt-2">
          Debug: Container: {containerWidth}px | Step: {stepPx.toFixed(2)}px |
          Animating: {animating ? "YES" : "NO"} | Translate:{" "}
          {translate.toFixed(2)}px | Data points: {renderData.length}
        </div>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <div
            ref={containerRef}
            style={{
              width: "100%",
              height: "200px",
              overflow: "hidden",
              position: "relative",
            }}
          >
            <div
              onTransitionEnd={onTransitionEnd}
              style={{
                width: innerWidth ? `${innerWidth}px` : "100%",
                height: "200px",
                transform: `translateX(${translate}px)`,
                transition: animating
                  ? `transform ${ANIM_MS}ms linear`
                  : "none",
              }}
            >
              <AreaChart
                width={innerWidth || containerWidth || 600}
                height={200}
                data={renderData}
                margin={{
                  left: 12,
                  right: 12,
                  top: 12,
                  bottom: 12,
                }}
              >
                <ChartTooltip
                  cursor={false}
                  content={<ChartTooltipContent indicator="dot" hideLabel />}
                />
                <Area
                  dataKey="desktop"
                  type="linear"
                  fill="var(--color-desktop)"
                  fillOpacity={0.4}
                  stroke="var(--color-desktop)"
                  isAnimationActive={false}
                />
              </AreaChart>
            </div>
          </div>
        </ChartContainer>
      </CardContent>
      <CardFooter>
        <div className="flex w-full items-start gap-2 text-sm">
          <div className="grid gap-2">
            <div className="flex items-center gap-2 leading-none font-medium">
              Real-time updates <TrendingUp className="h-4 w-4" />
            </div>
            <div className="text-muted-foreground flex items-center gap-2 leading-none">
              New data point every second
            </div>
          </div>
        </div>
      </CardFooter>
    </Card>
  );
}
// ...existing code...
