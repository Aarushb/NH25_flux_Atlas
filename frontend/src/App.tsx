import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import { Component } from "@/components/example-chart";
import { ChartAreaLinear } from "./components/chart-area-linear";
import ZoomableWorldMap from "./components/zoomable-world-map";

function App() {
  const [count, setCount] = useState(0);

  return (
    <div className="w-screen h-screen">
      <Component />
      <ChartAreaLinear />
      <ZoomableWorldMap />
    </div>
  );
}

export default App;
