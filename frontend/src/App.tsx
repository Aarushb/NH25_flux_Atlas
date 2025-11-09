import { useState } from "react";
import { AppSidebar } from "@/components/app-sidebar";
import { Component } from "@/components/example-chart";
import { CustomD3Chart } from "./components/chart-area-linear";
import ZoomableWorldMap from "./components/zoomable-world-map";
import { LatestEvents } from "./components/latest-events";
import {
  SidebarProvider,
  SidebarInset,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { DropdownMenuDemo } from "./components/dropdown-button";
import { DialogDemo } from "./components/dialog-demo";

const countries: string[] = [
  "World",
  "Somalia",
  "Mozambique",
  "Chad",
  "Haiti",
  "Pakistan",
  "Nigeria",
  "Kenya",
  "Bangladesh",
  "India",
  "South Africa",
  "Sri Lanka",
  "Indonesia",
  "Vietnam",
  "Iran",
  "Brazil",
  "China",
  "Azerbaijan",
  "Chile",
  "Oman",
  "Latvia",
  "Slovakia",
  "Russia",
  "Kuwait",
  "Japan",
  "France",
  "Saudi Arabia",
  "Germany",
  "United States",
  "Switzerland",
  "Australia",
];

const resources = ["Aluminum", "Oil", "Natural Gas", "Uranium"];

function App() {
  const [currentPage, setCurrentPage] = useState<string>("home");
  const [resource, setResource] = useState<string>("Aluminum");
  const [country, setCountry] = useState<string>("World");

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
              <DropdownMenuDemo
                value={resource}
                setValue={setResource}
                values={resources}
              />
              <DropdownMenuDemo
                value={country}
                setValue={setCountry}
                values={countries}
              />
              <div className="grid gap-4 md:grid-cols-2">
                <CustomD3Chart />
                <ZoomableWorldMap value={country} setValue={setCountry} />
              </div>
              <DialogDemo buttonText="Place Bid" />
              <DialogDemo buttonText="Some Bullshit" />
              <LatestEvents />
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
