import React, { useState, useEffect } from "react";
import type { JSX } from "react";
import {
  ComposableMap,
  Geographies,
  Geography,
  ZoomableGroup,
} from "react-simple-maps";
import { geoCentroid, geoArea } from "d3-geo";
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

type MapProps = {
  value: string;
  setValue: React.Dispatch<React.SetStateAction<string>>;
};

export default function ZoomableWorldMap({
  value,
  setValue,
}: MapProps): JSX.Element {
  const [position, setPosition] = useState<MapPosition>({
    coordinates: [0, 20],
    zoom: 1.2,
  });
  const [geographiesData, setGeographiesData] = useState<GeographyFeature[]>(
    []
  );
  const [_isAnimating, setIsAnimating] = useState(false);

  const handleCountryClick = (geo: GeographyFeature): void => {
    const centroid = geoCentroid(geo) as [number, number];

    // Calculate zoom level based on country size
    // Using d3.geoPath to calculate the area of the country
    // Calculate zoom level based on country size
    // Using d3.geoArea to calculate the area of the country
    const area = geoArea(geo);
    // Smaller countries get higher zoom levels
    let zoomLevel = 4; // default
    if (area < 100) {
      zoomLevel = 8; // Very small countries (islands, city-states)
    } else if (area < 500) {
      zoomLevel = 6; // Small countries
    } else if (area < 2000) {
      zoomLevel = 5; // Medium countries
    } else {
      zoomLevel = 4; // Large countries
    }

    setIsAnimating(true);
    setPosition({
      coordinates: centroid,
      zoom: zoomLevel,
    });

    // Reset animation flag after transition
    setTimeout(() => setIsAnimating(false), 1000);
  };

  const handleReset = (): void => {
    setValue("World");
    setIsAnimating(true);
    setPosition({
      coordinates: [0, 20],
      zoom: 1.2,
    });
    setTimeout(() => setIsAnimating(false), 1000);
  };

  // Auto-zoom when value changes
  useEffect(() => {
    if (value === "World") handleReset();
    if (geographiesData.length === 0) return;

    const selectedGeo = geographiesData.find(
      (geo) => geo.properties.name === value
    );

    if (selectedGeo) {
      handleCountryClick(selectedGeo);
    }
  }, [value, geographiesData]);

  return (
    <Card className="p-0 overflow-hidden">
      <CardContent className="p-0">
        <div
          style={{
            position: "relative",
            width: "100%",
            height: "100%",
          }}
        >
          <style>{`
            .rsm-zoomable-group {
              transition: transform 1000ms ease-in-out !important;
            }
          `}</style>
          <ComposableMap projection="geoMercator">
            <ZoomableGroup
              center={position.coordinates}
              zoom={position.zoom}
              translateExtent={[
                [-1000, -500],
                [1000, 500],
              ]}
            >
              <Geographies geography={geoUrl}>
                {({ geographies }: { geographies: GeographyFeature[] }) => {
                  // Store geographies data once loaded
                  if (geographiesData.length === 0) {
                    setGeographiesData(geographies);
                  }

                  return geographies.map((geo) => (
                    <Geography
                      key={geo.rsmKey}
                      geography={geo}
                      style={{
                        default: {
                          // Change selected country color here (currently #6B7280 - gray-500)
                          fill:
                            geo.properties.name === value
                              ? "#6B7280"
                              : "#D6D6DA",
                          outline: "none",
                          cursor: "default",
                          pointerEvents: "none",
                        },
                        hover: {
                          fill:
                            geo.properties.name === value
                              ? "#6B7280"
                              : "#D6D6DA",
                          outline: "none",
                          pointerEvents: "none",
                        },
                        pressed: {
                          fill:
                            geo.properties.name === value
                              ? "#6B7280"
                              : "#D6D6DA",
                          outline: "none",
                          pointerEvents: "none",
                        },
                      }}
                    />
                  ));
                }}
              </Geographies>
            </ZoomableGroup>
          </ComposableMap>
        </div>
      </CardContent>
    </Card>
  );
}
