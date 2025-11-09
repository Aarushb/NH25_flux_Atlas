import { useState } from "react";
import LandingHero from "./components/landing-hero";
import ZoomableWorldMap from "./components/zoomable-world-map";
import MarketHealthPanel from "./components/market-health-panel";
import { LatestEvents } from "./components/latest-events";
import { Separator } from "@/components/ui/separator";
import { DropdownMenuDemo } from "./components/dropdown-button";
import { DialogDemo } from "./components/dialog-demo";
import AuctionForm from "./components/auction-form";

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
  const [currentPage, _setCurrentPage] = useState<string>("dashboard");
  const [resource, setResource] = useState<string>("Aluminum");
  const [country, setCountry] = useState<string>("World");

  return (
    <>
      <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4 glass">
          <Separator orientation="vertical" className="mr-2 h-4" />
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-semibold">
              {currentPage === "dashboard" && "Dashboard"}
              {currentPage === "analytics" && "Analytics"}
              {currentPage === "sell" && "Sell Resources"}
              {currentPage === "buy" && "Buy Resources"}
            </h1>
          </div>
        </header>
        <main id="main-content" className="flex flex-1 flex-col gap-4 p-4 overflow-y-auto">
          <LandingHero />
          {currentPage === "dashboard" && (
            <div className="space-y-4">
              <div className="flex flex-wrap items-center gap-3">
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
              </div>
              <MarketHealthPanel />
              <div className="mt-2">
                <AuctionForm />
              </div>
              <div className="grid gap-4 md:grid-cols-1">
                <div className="h-[480px] md:h-[820px]">
                  <ZoomableWorldMap value={country} setValue={setCountry} />
                </div>
              </div>
              <DialogDemo buttonText="Place Bid" />
              <DialogDemo buttonText="More Info" />
              <LatestEvents />
            </div>
          )}

          {currentPage === "analytics" && <div className="space-y-4"></div>}

          {currentPage === "sell" && <div className="space-y-4"><DialogDemo buttonText="Sell"/></div>}

          {currentPage === "buy" && <div className="space-y-4"><DialogDemo buttonText="Buy"/></div>}
        </main>
    </>
  );
}

export default App;
