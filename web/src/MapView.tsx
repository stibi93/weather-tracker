import { useEffect, useRef } from "react";
import maplibregl, { type ExpressionSpecification } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { basemapStyle } from "./basemap";
import { theme } from "./theme";

const DATA_URL = `${import.meta.env.BASE_URL}data/water-bodies.geojson`;
const SOURCE_ID = "water-bodies";
const LAYER_ID = "water-bodies-circles";

function tooltipHTML(p: Record<string, unknown>): string {
  const value = p.latest_value_cm == null ? "—" : `${p.latest_value_cm} cm`;
  return `<strong>${p.name}</strong><br/>
    <span style="color:${theme.inkSoft}">${p.station}</span><br/>
    <span style="font-size:15px;font-weight:600">${value}</span>
    <span style="color:${theme.inkSoft};font-size:11px"> · ${p.latest_date ?? ""}</span>`;
}

const hoverOrSelected: ExpressionSpecification = [
  "any",
  ["boolean", ["feature-state", "hover"], false],
  ["boolean", ["feature-state", "selected"], false],
];

export function MapView({
  onSelect,
  selectedId,
}: {
  onSelect: (id: string) => void;
  selectedId: string | null;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const prevSelected = useRef<string | null>(null);
  const onSelectRef = useRef(onSelect);
  onSelectRef.current = onSelect;

  useEffect(() => {
    if (!containerRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: basemapStyle(),
      center: [19.4, 47.05],
      zoom: 6.6,
      attributionControl: { compact: true },
    });
    mapRef.current = map;
    if (new URLSearchParams(location.search).has("debug")) {
      (window as Window & { __map?: maplibregl.Map }).__map = map;
    }
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "bottom-right");

    const popup = new maplibregl.Popup({
      closeButton: false,
      closeOnClick: false,
      offset: 14,
      className: "wb-popup",
    });
    let hoveredId: string | null = null;

    map.on("load", async () => {
      const geo = await fetch(DATA_URL).then((r) => r.json());
      map.addSource(SOURCE_ID, { type: "geojson", data: geo, promoteId: "id" });

      const bounds = new maplibregl.LngLatBounds();
      for (const f of geo.features) bounds.extend(f.geometry.coordinates as [number, number]);
      if (!bounds.isEmpty()) map.fitBounds(bounds, { padding: 90, maxZoom: 8, duration: 0 });

      map.addLayer({
        id: LAYER_ID,
        type: "circle",
        source: SOURCE_ID,
        paint: {
          "circle-radius": ["case", hoverOrSelected, 13, 8],
          "circle-color": [
            "match",
            ["get", "kind"],
            "lake",
            theme.lake,
            "river",
            theme.river,
            theme.gold,
          ],
          "circle-stroke-width": [
            "case",
            ["boolean", ["feature-state", "selected"], false],
            5,
            ["case", ["boolean", ["feature-state", "hover"], false], 4, 2],
          ],
          "circle-stroke-color": ["case", hoverOrSelected, theme.gold, "#ffffff"],
          "circle-opacity": 0.95,
        },
      });

      const setHover = (id: string | null) => {
        if (hoveredId) map.setFeatureState({ source: SOURCE_ID, id: hoveredId }, { hover: false });
        hoveredId = id;
        if (hoveredId) map.setFeatureState({ source: SOURCE_ID, id: hoveredId }, { hover: true });
      };

      map.on("mousemove", LAYER_ID, (e) => {
        const f = e.features?.[0];
        if (!f) return;
        map.getCanvas().style.cursor = "pointer";
        setHover(String(f.id));
        popup.setLngLat(e.lngLat).setHTML(tooltipHTML(f.properties as Record<string, unknown>)).addTo(map);
      });

      map.on("mouseleave", LAYER_ID, () => {
        map.getCanvas().style.cursor = "";
        setHover(null);
        popup.remove();
      });

      map.on("click", LAYER_ID, (e) => {
        const f = e.features?.[0];
        if (f) onSelectRef.current(String(f.id));
      });
    });

    return () => map.remove();
  }, []);

  // Kiválasztott víztest kiemelése feature-state-tel.
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.getSource(SOURCE_ID)) return;
    if (prevSelected.current) {
      map.setFeatureState({ source: SOURCE_ID, id: prevSelected.current }, { selected: false });
    }
    if (selectedId) {
      map.setFeatureState({ source: SOURCE_ID, id: selectedId }, { selected: true });
    }
    prevSelected.current = selectedId;
  }, [selectedId]);

  return <div ref={containerRef} className="map-root" />;
}
