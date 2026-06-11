import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { basemapStyle } from "./basemap";
import { theme } from "./theme";

const DATA_URL = `${import.meta.env.BASE_URL}data/water-bodies.geojson`;
const SOURCE_ID = "water-bodies";
const LAYER_ID = "water-bodies-circles";

function tooltipHTML(p: Record<string, unknown>): string {
  const value = p.latest_value_cm == null ? "—" : `${p.latest_value_cm} cm`;
  const date = p.latest_date ?? "";
  return `<strong>${p.name}</strong><br/>
    <span style="color:${theme.inkSoft}">${p.station}</span><br/>
    <span style="font-size:15px;font-weight:600">${value}</span>
    <span style="color:${theme.inkSoft};font-size:11px"> · ${date}</span>`;
}

export function MapView() {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: basemapStyle(),
      center: [19.4, 47.05],
      zoom: 6.6,
      attributionControl: { compact: true },
    });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");

    const popup = new maplibregl.Popup({
      closeButton: false,
      closeOnClick: false,
      offset: 14,
      className: "wb-popup",
    });
    let hoveredId: string | null = null;

    map.on("load", async () => {
      const geo = await fetch(DATA_URL).then((r) => r.json());

      map.addSource(SOURCE_ID, {
        type: "geojson",
        data: geo,
        promoteId: "id", // properties.id -> feature id (feature-state-hez)
      });

      // Az összes víztestre illesztünk, hogy mind keretben legyen.
      const bounds = new maplibregl.LngLatBounds();
      for (const f of geo.features) {
        bounds.extend(f.geometry.coordinates as [number, number]);
      }
      if (!bounds.isEmpty()) {
        map.fitBounds(bounds, { padding: 90, maxZoom: 8, duration: 0 });
      }

      map.addLayer({
        id: LAYER_ID,
        type: "circle",
        source: SOURCE_ID,
        paint: {
          "circle-radius": [
            "case",
            ["boolean", ["feature-state", "hover"], false],
            13,
            8,
          ],
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
            ["boolean", ["feature-state", "hover"], false],
            4,
            2,
          ],
          "circle-stroke-color": [
            "case",
            ["boolean", ["feature-state", "hover"], false],
            theme.gold,
            "#ffffff",
          ],
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
    });

    return () => map.remove();
  }, []);

  return <div ref={containerRef} className="map-root" />;
}
