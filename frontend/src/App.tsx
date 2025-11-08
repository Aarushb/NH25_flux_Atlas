import { useState } from "react";
import { AppSidebar } from "@/components/app-sidebar";
import { Component } from "@/components/example-chart";
import { ChartAreaLinear } from "./components/chart-area-linear";
import ZoomableWorldMap from "./components/zoomable-world-map";
import {
  SidebarProvider,
  SidebarInset,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";

function App() {
  const [currentPage, setCurrentPage] = useState<"home" | "charts" | "map">(
    "home"
  );

  return (
    <SidebarProvider>
      <AppSidebar onNavigate={setCurrentPage} currentPage={currentPage} />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-semibold">
              {currentPage === "home" && "Dashboard"}
              {currentPage === "charts" && "Live Charts"}
              {currentPage === "map" && "World Map"}
            </h1>
          </div>
        </header>
        <main className="flex flex-1 flex-col gap-4 p-4 overflow-y-auto">
          {currentPage === "home" && (
            <div className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <ChartAreaLinear />
                <ZoomableWorldMap />
              </div>
            </div>
          )}

          {currentPage === "charts" && <div className="space-y-4"></div>}

          {currentPage === "map" && <div className="space-y-4"></div>}
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
}

export default App;
