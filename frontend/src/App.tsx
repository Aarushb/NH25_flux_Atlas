import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import { Component } from "@/components/example-chart";

function App() {
  const [count, setCount] = useState(0);

  return (
    <div className="w-screen h-screen">
      <Component />
    </div>
  );
}

export default App;
