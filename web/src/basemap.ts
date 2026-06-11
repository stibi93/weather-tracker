import type { StyleSpecification } from "maplibre-gl";

// Saját, kézzel hangolt "földes/topográfiai" vektoros stílus (C irány).
// Kulcs nélküli OpenFreeMap (OpenMapTiles séma) vektor csempékre épül, és minden
// réteget mi színezünk — ettől egyedi, "designer" a megjelenés a stock térképek helyett.
// Ha VITE_MAPTILER_KEY meg van adva, helyette a MapTiler "outdoor" stílus is használható.

const OFM = "https://tiles.openfreemap.org";

const c = {
  parchment: "#efe6d3",
  wood: "#c7d1ad",
  grass: "#d8dcbb",
  park: "#cfdcb4",
  residential: "#e9dec8",
  waterDeep: "#3f8f87",
  road: "#e6d7b4",
  roadMinor: "#e4dac4",
  boundary: "#b59a6d",
  ink: "#5a4f3c",
  halo: "#f6efde",
} as const;

export function customEarthyStyle(): StyleSpecification {
  return {
    version: 8,
    glyphs: `${OFM}/fonts/{fontstack}/{range}.pbf`,
    sources: {
      openmaptiles: {
        type: "vector",
        url: `${OFM}/planet`,
        attribution:
          '© OpenMapTiles · © OpenStreetMap közreműködők · csempék: OpenFreeMap',
      },
    },
    layers: [
      { id: "bg", type: "background", paint: { "background-color": c.parchment } },

      // Tájhasználat / növényzet — lágy, alacsony kontraszt
      {
        id: "landuse-residential",
        type: "fill",
        source: "openmaptiles",
        "source-layer": "landuse",
        filter: ["==", ["get", "class"], "residential"],
        paint: { "fill-color": c.residential, "fill-opacity": 0.5 },
      },
      {
        id: "landcover-wood",
        type: "fill",
        source: "openmaptiles",
        "source-layer": "landcover",
        filter: ["in", ["get", "class"], ["literal", ["wood", "forest"]]],
        paint: { "fill-color": c.wood, "fill-opacity": 0.55 },
      },
      {
        id: "landcover-grass",
        type: "fill",
        source: "openmaptiles",
        "source-layer": "landcover",
        filter: ["in", ["get", "class"], ["literal", ["grass", "meadow", "scrub", "heath"]]],
        paint: { "fill-color": c.grass, "fill-opacity": 0.5 },
      },
      {
        id: "park",
        type: "fill",
        source: "openmaptiles",
        "source-layer": "park",
        paint: { "fill-color": c.park, "fill-opacity": 0.45 },
      },

      // Víz — a hős elem, telített teal
      {
        id: "water",
        type: "fill",
        source: "openmaptiles",
        "source-layer": "water",
        filter: ["!=", ["get", "intermittent"], 1],
        paint: { "fill-color": c.waterDeep },
      },
      {
        id: "waterway",
        type: "line",
        source: "openmaptiles",
        "source-layer": "waterway",
        paint: {
          "line-color": c.waterDeep,
          "line-width": ["interpolate", ["linear"], ["zoom"], 6, 0.6, 12, 2.2],
          "line-opacity": 0.85,
        },
      },

      // Utak — visszafogott, hierarchikus, homokszín
      {
        id: "road-minor",
        type: "line",
        source: "openmaptiles",
        "source-layer": "transportation",
        minzoom: 10,
        filter: ["in", ["get", "class"], ["literal", ["minor", "service", "track"]]],
        paint: { "line-color": c.roadMinor, "line-width": ["interpolate", ["linear"], ["zoom"], 11, 0.4, 16, 2] },
      },
      {
        id: "road-secondary",
        type: "line",
        source: "openmaptiles",
        "source-layer": "transportation",
        filter: ["in", ["get", "class"], ["literal", ["secondary", "tertiary"]]],
        paint: { "line-color": c.road, "line-width": ["interpolate", ["linear"], ["zoom"], 8, 0.4, 14, 2.5] },
      },
      {
        id: "road-primary",
        type: "line",
        source: "openmaptiles",
        "source-layer": "transportation",
        filter: ["in", ["get", "class"], ["literal", ["primary", "trunk", "motorway"]]],
        paint: {
          "line-color": c.road,
          "line-width": ["interpolate", ["linear"], ["zoom"], 6, 0.6, 10, 2, 14, 4.5],
        },
      },

      // Határok — finom szaggatott okker
      {
        id: "boundary-country",
        type: "line",
        source: "openmaptiles",
        "source-layer": "boundary",
        filter: ["==", ["get", "admin_level"], 2],
        paint: {
          "line-color": c.boundary,
          "line-width": ["interpolate", ["linear"], ["zoom"], 4, 0.8, 10, 2],
          "line-dasharray": [3, 1.5],
          "line-opacity": 0.7,
        },
      },

      // Címkék
      {
        id: "place-city",
        type: "symbol",
        source: "openmaptiles",
        "source-layer": "place",
        filter: ["in", ["get", "class"], ["literal", ["city", "town"]]],
        layout: {
          "text-field": ["get", "name"],
          "text-font": ["Noto Sans Bold"],
          "text-size": ["interpolate", ["linear"], ["zoom"], 6, 11, 10, 15],
          "text-letter-spacing": 0.04,
        },
        paint: { "text-color": c.ink, "text-halo-color": c.halo, "text-halo-width": 1.6 },
      },
      {
        id: "water-name",
        type: "symbol",
        source: "openmaptiles",
        "source-layer": "water_name",
        layout: {
          "text-field": ["get", "name"],
          "text-font": ["Noto Sans Italic"],
          "text-size": 12,
        },
        paint: { "text-color": c.waterDeep, "text-halo-color": c.halo, "text-halo-width": 1.4 },
      },
    ],
  };
}

export function basemapStyle(): string | StyleSpecification {
  const key = import.meta.env.VITE_MAPTILER_KEY;
  if (key) return `https://api.maptiler.com/maps/outdoor-v2/style.json?key=${key}`;
  return customEarthyStyle();
}
