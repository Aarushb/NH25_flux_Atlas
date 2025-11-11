import { useEffect, useState } from "react";
import LoginPage from "./components/login-page";
import LandingHero from "./components/landing-hero";
import ZoomableWorldMap from "./components/zoomable-world-map";
import MarketHealthPanel from "./components/market-health-panel";
import { LatestEvents } from "./components/latest-events";
import { Separator } from "@/components/ui/separator";
import { DropdownMenuDemo } from "./components/dropdown-button";
import { DialogDemo } from "./components/dialog-demo";
import ResourceList from "./components/resource-list";
import ToastProvider from "./components/toast-provider";
import ActiveBids from "./components/active-bids";
import Ticker from "./components/ticker2";
import SellMarket from "./components/sell-market";

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

const ALL_RESOURCES = ["Aluminum", "Oil", "Natural Gas", "Uranium"];

function getResourcesForCountry(country: string) {
  const lower = (country || "").toLowerCase();
  if (lower.includes("united") || lower === "world" || lower.includes("china") || lower.includes("india")) {
    return ALL_RESOURCES;
  }
  if (lower.includes("brazil") || lower.includes("australia") || lower.includes("russia")) {
    return ["Aluminum", "Uranium"];
  }
  return ["Aluminum", "Natural Gas"];
}

function App() {
  const [currentPage, setCurrentPage] = useState<string>("dashboard");
  const [resource, setResource] = useState<string>("Aluminum");
  const [country, setCountry] = useState<string>("World");
    const [repName, setRepName] = useState<string | null>(null);
    const [repCountry, setRepCountry] = useState<string | null>(null); // country used at signup

  useEffect(() => {
    const handler = () => setCurrentPage("login");
    window.addEventListener("navigate:login", handler as EventListener);
    return () => window.removeEventListener("navigate:login", handler as EventListener);
  }, []);

  useEffect(() => {
      try {
        const n = localStorage.getItem("repName");
        const c = localStorage.getItem("repCountry");
        if (n) setRepName(n);
        if (c) {
          setRepCountry(c);
          setCountry(c);
        }
      } catch {
        void 0;
      }
    }, []);

  return (
    <ToastProvider>
      <>
        <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4 glass">
          <Separator orientation="vertical" className="mr-2 h-4" />
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-semibold">
              {currentPage === "dashboard" && "FluxAtlas"}
              {currentPage === "analytics" && "Analytics"}
              {currentPage === "sell" && "Sell Resources"}
              {currentPage === "buy" && "Buy Resources"}
              {currentPage === "login" && "Representative login"}
            </h1>
            {repName && currentPage === "dashboard" && (
              <div className="ml-4 text-sm text-muted-foreground">Welcome {repName} of {repCountry ?? country}</div>
            )}
          </div>
          <div className="ml-auto">
              {/* active bids icon */}
              <ActiveBids />
          </div>
        </header>
        <main id="main-content" className="flex flex-1 flex-col gap-4 p-4 overflow-y-auto">
          <LandingHero />

          {currentPage === "login" && (
            <LoginPage
              countries={countries}
                onLogin={(name, selectedCountry) => {
                  if (selectedCountry) {
                    setCountry(selectedCountry);
                    setRepCountry(selectedCountry);
                  }
                  setRepName(name);
                  setCurrentPage("dashboard");
                }}
            />
          )}
          {currentPage === "dashboard" && (
            <div className="space-y-4">
              <div className="flex flex-wrap items-center gap-3">
                <DropdownMenuDemo
                  value={resource}
                  setValue={setResource}
                  values={getResourcesForCountry(country)}
                />
                <DropdownMenuDemo
                  value={country}
                  setValue={setCountry}
                  values={countries}
                />
              </div>
              <MarketHealthPanel />
              <div className="mt-2">
                <SellMarket />
              </div>
              <div>
                <ResourceList />
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

          {currentPage === "sell" && (
            <div className="space-y-4">
              <SellMarket />
            </div>
          )}

          {currentPage === "buy" && <div className="space-y-4"><DialogDemo buttonText="Buy"/></div>}
        </main>
      </>
      <Ticker />
    </ToastProvider>
  );
}

export default App;
