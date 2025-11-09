import { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface Event {
  id: number;
  title: string;
  description: string;
  location: string;
  timestamp: Date;
}

// Sample event data for simulation
const eventTemplates = [
  {
    title: "Earthquake Detected",
    description: "A magnitude 5.2 earthquake was detected",
    locations: ["Japan", "California", "Chile", "Indonesia", "Turkey"],
  },
  {
    title: "Major Storm Warning",
    description: "Severe weather conditions reported",
    locations: ["Florida", "Philippines", "Australia", "India", "Bangladesh"],
  },
  {
    title: "Political Summit",
    description: "International leaders meet for climate discussions",
    locations: ["Geneva", "New York", "Paris", "Berlin", "London"],
  },
  {
    title: "Economic Milestone",
    description: "Stock market reaches new record high",
    locations: ["Wall Street", "Tokyo", "London", "Hong Kong", "Frankfurt"],
  },
  {
    title: "Scientific Breakthrough",
    description: "Researchers announce major discovery",
    locations: ["MIT", "Oxford", "Stanford", "Cambridge", "ETH Zurich"],
  },
  {
    title: "Sports Championship",
    description: "National team wins international tournament",
    locations: ["Brazil", "Spain", "Germany", "Argentina", "France"],
  },
  {
    title: "Cultural Festival",
    description: "Annual celebration draws thousands",
    locations: ["Rio", "Mumbai", "Tokyo", "New Orleans", "Edinburgh"],
  },
  {
    title: "Tech Conference",
    description: "Industry leaders unveil new innovations",
    locations: ["San Francisco", "Seoul", "Shenzhen", "Austin", "Tel Aviv"],
  },
];

const generateRandomEvent = (id: number): Event => {
  const template =
    eventTemplates[Math.floor(Math.random() * eventTemplates.length)];
  const location =
    template.locations[Math.floor(Math.random() * template.locations.length)];

  return {
    id,
    title: template.title,
    description: `${template.description} in ${location}`,
    location,
    timestamp: new Date(),
  };
};

export function LatestEvents() {
  const [events, setEvents] = useState<Event[]>(() =>
    Array.from({ length: 10 }, (_, i) => generateRandomEvent(i))
  );
  const [nextId, setNextId] = useState(10);

  useEffect(() => {
    // Add a new event every 5 seconds
    const interval = setInterval(() => {
      setEvents((prevEvents) => {
        const newEvent = generateRandomEvent(nextId);
        setNextId((id) => id + 1);
        // Add new event at the start and keep only the latest 10
        return [newEvent, ...prevEvents.slice(0, 9)];
      });
    }, 5000);

    return () => clearInterval(interval);
  }, [nextId]);

  const formatTime = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.floor(diffHours / 24)}d ago`;
  };

  return (
    <Card className="card">
      <CardHeader>
        <CardTitle>Latest Global Events</CardTitle>
        <CardDescription>
          Real-time updates from around the world
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {events.map((event, index) => (
            <Card
              key={event.id}
              className="transition-all duration-500 ease-out glass"
              style={{
                animation: index === 0 ? "slideDown 0.5s ease-out" : undefined,
              }}
            >
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-sm">{event.title}</h3>
                      <Badge variant="secondary" className="text-xs">
                        {event.location}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {event.description}
                    </p>
                  </div>
                  <span className="text-xs text-muted-foreground whitespace-nowrap">
                    {formatTime(event.timestamp)}
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
