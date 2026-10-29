"""
Environmental Spatial Data Processing & Heatmap Visualizer
Integrates GeoJSON/Shapefiles, computes pollution/air quality indices, and renders interactive maps.
"""
import json

def process_environmental_data(input_geojson: dict) -> dict:
    features = input_geojson.get("features", [])
    processed = []
    
    for feat in features:
        props = feat.get("properties", {})
        geometry = feat.get("geometry", {})
        
        pm25 = props.get("pm25", 0.0)
        aqi_category = "Good"
        if pm25 > 35.4: aqi_category = "Moderate"
        if pm25 > 55.4: aqi_category = "Unhealthy for Sensitive Groups"
        if pm25 > 150.4: aqi_category = "Hazardous"
        
        props["computed_aqi_category"] = aqi_category
        props["render_color"] = "#22c55e" if aqi_category == "Good" else "#ef4444"
        
        processed.append({
            "type": "Feature",
            "geometry": geometry,
            "properties": props
        })
        
    return {
        "type": "FeatureCollection",
        "metadata": {
            "total_points": len(processed),
            "engine": "ARIA Environmental Spatial Engine"
        },
        "features": processed
    }

if __name__ == "__main__":
    sample = {
        "features": [
            {"geometry": {"type": "Point", "coordinates": [-73.98, 40.75]}, "properties": {"pm25": 14.2}},
            {"geometry": {"type": "Point", "coordinates": [-73.99, 40.76]}, "properties": {"pm25": 62.1}}
        ]
    }
    print(json.dumps(process_environmental_data(sample), indent=2))
