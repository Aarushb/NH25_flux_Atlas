import React, { useState } from "react";
import type { JSX } from "react";
import {
  ComposableMap,
  Geographies,
  Geography,
  ZoomableGroup,
} from "react-simple-maps";
import { geoCentroid } from "d3-geo";
import type { Feature, Geometry } from "geojson";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

// TopoJSON world data
const geoUrl = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";

// Type for the map zoom/center state
interface MapPosition {
  coordinates: [number, number];
  zoom: number;
}

// Type for a single country (extends GeoJSON Feature)
interface GeographyFeature extends Feature<Geometry, { name: string }> {
  rsmKey: string;
}

export default function ZoomableWorldMap(): JSX.Element {
  const [position, setPosition] = useState<MapPosition>({
    coordinates: [0, 20],
    zoom: 1,
  });

  const handleCountryClick = (geo: GeographyFeature): void => {
    const centroid = geoCentroid(geo) as [number, number];
    setPosition({
      coordinates: centroid,
      zoom: 4,
    });
  };

  const handleReset = (): void => {
    setPosition({
      coordinates: [0, 20],
      zoom: 1,
    });
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Interactive World Map</CardTitle>
          <Button onClick={handleReset} variant="outline" size="sm">
            Reset Zoom
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <ComposableMap projection="geoMercator">
          <ZoomableGroup
            center={position.coordinates}
            zoom={position.zoom}
            onMoveEnd={(pos: MapPosition) => setPosition(pos)}
          >
            <Geographies geography={geoUrl}>
              {({ geographies }: { geographies: GeographyFeature[] }) =>
                geographies.map((geo) => (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    onClick={() => handleCountryClick(geo)}
                    style={{
                      default: { fill: "#D6D6DA", outline: "none" },
                      hover: { fill: "#F53", outline: "none" },
                      pressed: { fill: "#E42", outline: "none" },
                    }}
                  />
                ))
              }
            </Geographies>
          </ZoomableGroup>
        </ComposableMap>
      </CardContent>
    </Card>
  );
}
