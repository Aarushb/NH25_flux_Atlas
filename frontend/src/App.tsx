import { useEffect, useState } from "react";
import LoginPage from "./components/login-page";
import LandingHero from "./components/landing-hero";
import ZoomableWorldMap from "./components/zoomable-world-map";
import MarketHealthPanel from "./components/market-health-panel";
import { LatestEvents } from "./components/latest-events";
import { Separator } from "@/components/ui/separator";
import { DropdownMenuDemo } from "./components/dropdown-button";
import { DialogDemo } from "./components/dialog-demo";
import AuctionForm from "./components/auction-form";
import ResourceList from "./components/resource-list";
import ToastProvider from "./components/toast-provider";
import ActiveBids from "./components/active-bids";


interface Country {
  id: string;
  cname: string;
}

interface Resource {
  id: string;
  name: string;
}

// Type for common HTTP methods
type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

async function apiFetch<T>(
    endpoint: string,
    method: HttpMethod = "GET",
    body?: unknown // Use 'unknown' for type safety
): Promise<T> {
  const res = await fetch(endpoint, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

type Page = "dashboard" | "analytics" | "sell" | "buy" | "login";

function App() {
  const [currentPage, setCurrentPage] = useState<Page>("dashboard");
  const [resource, setResource] = useState<string | null>(null);
  const [country, setCountry] = useState<string | null>(null);
  const [repName, setRepName] = useState<string | null>(null);
  const [repCountry, setRepCountry] = useState<string | null>(null);

  const [countries, setCountries] = useState<Country[]>([]);

  const [countryResources, setCountryResources] = useState<Resource[]>([]);

  // Load stored representative info
  useEffect(() => {
    try {
      const n = localStorage.getItem("repName");
      const c = localStorage.getItem("repCountry");
      if (n) setRepName(n);
      if (c) {
        setRepCountry(c);
        setCountry(c);
      }
    } catch (err) {
      console.warn("Could not access localStorage:", err);
    }
  }, []);

  // Listen for navigate:login event
  useEffect(() => {

    const handler = () => {
      setCurrentPage("login");
    };

    window.addEventListener("navigate:login", handler);
    return () => window.removeEventListener("navigate:login", handler);
  }, []);

  // Fetch countries on mount
  async function fetchData() {
    try {
      const res = await fetch("http://localhost:8000/countries/");
      const json = await res.json();
      setCountries(json);

    } catch (e) {
      console.error("Failed to fetch countries", e);
    }
  }

  useEffect(() => {
    fetchData()
  }, []);

  console.log(countries)

  // Fetch resources for selected country
  useEffect(() => {
    // FIX: Explicitly handle the 'null' case for country
    if (!country) {
      setCountryResources([]);
      setResource(null);
      return;
    }

    async function fetchCountryResources() {
      try {
        const countryObj = countries.find((c) => c.cname === country);
        if (!countryObj) {
          // Handle case where country name is valid but not in the list yet
          setCountryResources([]);
          setResource(null);
          return;
        }

        const data = await apiFetch<Resource[]>(
            `http://localhost:8000/countries/${countryObj.id}/resources/`
        );
        setCountryResources(data);
        // Set default resource to the first in the list, or null if empty
        setResource(data[0]?.name || null);
      } catch (err) {
        console.error("Error fetching country resources:", err);
        setCountryResources([]);
        setResource(null);
      }
    }

    fetchCountryResources();
  }, [country, countries]); // Dependency array is correct

const names:string[] = []  
  
countries.map(c => {
  names.push(c.cname)
})
  
  console.log(names)
  
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
                  <div className="ml-4 text-sm text-muted-foreground">
                    Welcome {repName} of {repCountry ?? country ?? "Unknown"}
                  </div>
              )}
            </div>
            <div className="ml-auto">
              <ActiveBids />
            </div>
          </header>

          <main
              id="main-content"
              className="flex flex-1 flex-col gap-4 p-4 overflow-y-auto"
          >
            <LandingHero />

            {currentPage === "login" && (
                <LoginPage
                    countries={countries.map((c) => c.cname)}
                    onLogin={(name: string, selectedCountry: string) => {

                      if (selectedCountry) {
                        setCountry(selectedCountry);
                        setRepCountry(selectedCountry);
                        localStorage.setItem("repCountry", selectedCountry);
                      }
                      setRepName(name);
                      localStorage.setItem("repName", name);
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
                        values={countryResources.map((r) => r.name)}
                        placeholder="Select Resource"
                    />
                    <DropdownMenuDemo
                        value={country}
                        setValue={setCountry}
                        values={countries.map((c) => c.cname)}
                        placeholder="Select Country"
                    />
                  </div>

                  <MarketHealthPanel

                  />

                  <div className="mt-2">
                    <AuctionForm
                        sellerCountry={repCountry}
                        currentCountry={country}
                        availableResources={countryResources.map((r) => r.name)}
                    />
                  </div>

                  <ResourceList />

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
                  <DialogDemo buttonText="Sell" />
                </div>
            )}
            {currentPage === "buy" && (
                <div className="space-y-4">
                  <DialogDemo buttonText="Buy" />
                </div>
            )}
          </main>
        </>
      </ToastProvider>
  );
}

export default App;