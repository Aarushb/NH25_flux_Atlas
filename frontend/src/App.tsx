import { useState, useEffect, useRef } from "react";
import LandingHero from "./components/landing-hero";
import ZoomableWorldMap from "./components/zoomable-world-map";
import MarketHealthPanel from "./components/market-health-panel";
import { LatestEvents } from "./components/latest-events";
import { Separator } from "@/components/ui/separator";
import { DropdownMenuDemo } from "./components/dropdown-button";
import { DialogDemo } from "./components/dialog-demo";
import AuctionForm from "./components/auction-form";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

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

const resources = [
  "Oil",
  "Natural Gas",
  "Coal",
  "Uranium",
  "Aluminum",
  "Iron Ore",
  "Copper",
  "Nickel",
  "Lithium",
  "Gold",
  "Diamonds",
  "Rare Earth",
  "Cobalt",
  "Platinum",
  "Palladium",
  "Tin",
  "Tungsten",
  "Graphite",
  "Niobium",
  "Hydropower",
];

// Map backend resource names to frontend names
const resourceNameMap: Record<string, string> = {
  PETROLEUM: "Oil",
  NATURAL_GAS: "Natural Gas",
  URANIUM: "Uranium",
  COAL: "Coal",
  BAUXITE: "Aluminum",
  IRON_ORE: "Iron Ore",
  COPPER: "Copper",
  NICKEL: "Nickel",
  LITHIUM: "Lithium",
  GOLD: "Gold",
  SILVER: "Silver",
  DIAMONDS: "Diamonds",
  RARE_EARTH_ELEMENTS: "Rare Earth",
  COBALT: "Cobalt",
  PLATINUM: "Platinum",
  PALLADIUM: "Palladium",
  TIN: "Tin",
  TUNGSTEN: "Tungsten",
  GRAPHITE: "Graphite",
  NIOBIUM: "Niobium",
  HYDROPOWER: "Hydropower",
};

// Reverse map for frontend to backend
const resourceNameReverseMap: Record<string, string> = Object.fromEntries(
  Object.entries(resourceNameMap).map(([k, v]) => [v, k])
);

interface SimulationMessage {
  type: string;
  data: Record<string, unknown>;
}

interface BatchAuction {
  auction_id: string;
  cluster_name: string;
  batch_num: number;
  seller: string;
  resource_name: string;
  quantity: number;
  base_price: number;
  resource_unit: string;
  turn_created: number;
  bids: Record<string, number>;
  winner: string | null;
  winning_price: number | null;
  is_finalized: boolean;
}

interface ActiveAuctionsData {
  turn: number;
  timestamp: number;
  active_cluster_auctions: unknown[];
  active_batch_auctions: BatchAuction[];
  total_active_batches: number;
  total_active_cluster_auctions: number;
  countries_currently_selling: string[];
}

function App() {
  const [currentPage, _setCurrentPage] = useState<string>("dashboard");
  const [resource, setResource] = useState<string>("Oil");
  const [country, setCountry] = useState<string>("World");

  // WebSocket state
  const [wsConnected, setWsConnected] = useState<boolean>(false);
  const [messages, setMessages] = useState<SimulationMessage[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Active auctions WebSocket state
  const [auctionWsConnected, setAuctionWsConnected] = useState<boolean>(false);
  const [auctionMessages, setAuctionMessages] = useState<SimulationMessage[]>(
    []
  );
  const [activeAuctionsData, setActiveAuctionsData] =
    useState<ActiveAuctionsData | null>(null);

  // Derived data from active auctions
  const materialsWithAuctions = new Set<string>();
  const countriesSellingMaterial = new Set<string>();

  if (activeAuctionsData) {
    activeAuctionsData.active_batch_auctions.forEach((auction) => {
      // Map backend resource name to frontend name
      const frontendResourceName =
        resourceNameMap[auction.resource_name] || auction.resource_name;
      materialsWithAuctions.add(frontendResourceName);

      // Check if this auction is for the currently selected material
      const selectedBackendResource =
        resourceNameReverseMap[resource] || resource;
      if (auction.resource_name === selectedBackendResource) {
        countriesSellingMaterial.add(auction.seller);
      }
    });
  }

  // Scroll to bottom of message container only when new messages arrive

  // WebSocket connection
  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/simulation");

    ws.onopen = () => {
      console.log("Connected to simulation WebSocket");
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      const message: SimulationMessage = JSON.parse(event.data);
      console.log("Received:", message.type, message.data);
      const thing: SimulationMessage[] = [];
      thing.push(message);
      setMessages(thing);
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");
      setWsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, []);

  // Active auctions WebSocket connection
  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/active-auctions");

    ws.onopen = () => {
      console.log("Connected to active auctions WebSocket");
      setAuctionWsConnected(true);
    };

    ws.onmessage = (event) => {
      const message: SimulationMessage = JSON.parse(event.data);
      console.log("Active Auctions:", message.type, message.data);
      setAuctionMessages([message]);

      // Update active auctions data
      if (
        message.type === "active_auctions_update" ||
        message.type === "active_auctions_snapshot"
      ) {
        setActiveAuctionsData(message.data as unknown as ActiveAuctionsData);
      }
    };

    ws.onerror = (error) => {
      console.error("Active auctions WebSocket error:", error);
    };

    ws.onclose = () => {
      console.log("Active auctions WebSocket disconnected");
      setAuctionWsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, []);

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
      <main
        id="main-content"
        className="flex flex-1 flex-col gap-4 p-4 overflow-y-auto"
      >
        <LandingHero />
        {currentPage === "dashboard" && (
          <div className="space-y-4">
            <div className="flex flex-wrap items-center gap-3">
              <DropdownMenuDemo
                value={resource}
                setValue={setResource}
                values={resources}
                itemsWithIndicator={materialsWithAuctions}
                indicatorColor="bg-amber-500"
                indicatorLabel="Active auctions available"
              />
              <DropdownMenuDemo
                value={country}
                setValue={setCountry}
                values={countries}
                itemsWithIndicator={countriesSellingMaterial}
                indicatorColor="bg-green-500"
                indicatorLabel="Selling selected material"
              />
            </div>
            <MarketHealthPanel />
            <div className="mt-2">
              <AuctionForm />
            </div>

            {/* Live Simulation Stream */}
            <Card className="mt-4">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  Live Simulation Stream
                  {wsConnected && (
                    <span className="flex h-3 w-3">
                      <span className="animate-ping absolute inline-flex h-3 w-3 rounded-full bg-green-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                    </span>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-black/90 text-green-400 font-mono text-sm p-4 rounded-lg h-96 overflow-y-auto">
                  {messages.length === 0 ? (
                    <div className="text-gray-500">
                      Connecting to simulation...
                    </div>
                  ) : (
                    messages.map((msg, idx) => (
                      <div
                        key={idx}
                        className="mb-2 border-b border-gray-800 pb-2"
                      >
                        <div className="text-yellow-400 font-bold">
                          [{msg.type}]
                        </div>
                        <pre className="text-xs mt-1 whitespace-pre-wrap wrap-break-word">
                          {JSON.stringify(msg.data, null, 2)}
                        </pre>
                      </div>
                    ))
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </CardContent>
            </Card>

            {/* Active Auctions Stream */}
            <Card className="mt-4">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  Active Auctions Stream
                  {auctionWsConnected && (
                    <span className="flex h-3 w-3">
                      <span className="animate-ping absolute inline-flex h-3 w-3 rounded-full bg-blue-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
                    </span>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-black/90 text-blue-400 font-mono text-sm p-4 rounded-lg h-96 overflow-y-auto">
                  {auctionMessages.length === 0 ? (
                    <div className="text-gray-500">
                      Connecting to active auctions stream...
                    </div>
                  ) : (
                    auctionMessages.map((msg, idx) => (
                      <div
                        key={idx}
                        className="mb-2 border-b border-gray-800 pb-2"
                      >
                        <div className="text-cyan-400 font-bold">
                          [{msg.type}]
                        </div>
                        <div className="text-xs mt-1 space-y-2">
                          <div>
                            <span className="text-gray-400">Turn:</span>{" "}
                            <span className="text-white">
                              {msg.data.turn as number}
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-400">
                              Active Batches:
                            </span>{" "}
                            <span className="text-white">
                              {msg.data.total_active_batches as number}
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-400">
                              Active Cluster Auctions:
                            </span>{" "}
                            <span className="text-white">
                              {msg.data.total_active_cluster_auctions as number}
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-400">
                              Countries Selling:
                            </span>{" "}
                            <span className="text-white">
                              {(
                                msg.data.countries_currently_selling as string[]
                              )?.join(", ") || "None"}
                            </span>
                          </div>
                          <details className="mt-2">
                            <summary className="cursor-pointer text-yellow-400 hover:text-yellow-300">
                              View Full Data
                            </summary>
                            <pre className="mt-2 whitespace-pre-wrap wrap-break-word text-xs">
                              {JSON.stringify(msg.data, null, 2)}
                            </pre>
                          </details>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>

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
  );
}

export default App;
