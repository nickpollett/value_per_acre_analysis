import json
import csv
from typing import Dict, Any


def flatten_properties(feature: Dict[str, Any], geometry_type: str) -> Dict[str, Any]:
    """Flatten a GeoJSON feature's properties and add coordinates."""
    # Start with properties
    flat_feature = feature.get('properties', {}).copy()

    # Add geometry type
    flat_feature['geometry_type'] = geometry_type

    # Handle different geometry types
    geometry = feature.get('geometry', {})
    coordinates = geometry.get('coordinates', [])

    if geometry_type == 'Point':
        if coordinates:
            flat_feature['longitude'] = coordinates[0]
            flat_feature['latitude'] = coordinates[1]
    elif geometry_type in ['LineString', 'Polygon']:
        # Store first and last coordinates
        if coordinates and len(coordinates) > 0:
            flat_feature['start_lon'] = coordinates[0][0]
            flat_feature['start_lat'] = coordinates[0][1]
            flat_feature['end_lon'] = coordinates[-1][0]
            flat_feature['end_lat'] = coordinates[-1][1]

    return flat_feature


def geojson_to_csv(input_file: str, output_file: str) -> None:
    """Convert GeoJSON file to CSV format."""
    try:
        # Read GeoJSON file
        with open(input_file, 'r') as f:
            geojson_data = json.load(f)

        # Check if it's a feature collection
        if geojson_data.get('type') != 'FeatureCollection':
            raise ValueError("Input must be a GeoJSON FeatureCollection")

        features = geojson_data.get('features', [])
        if not features:
            raise ValueError("No features found in GeoJSON")

        # Process all features to get complete set of fields
        processed_features = []
        fieldnames = set()

        for feature in features:
            geometry_type = feature.get('geometry', {}).get('type', 'Unknown')
            flat_feature = flatten_properties(feature, geometry_type)
            processed_features.append(flat_feature)
            fieldnames.update(flat_feature.keys())

        # Write to CSV
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
            writer.writeheader()
            writer.writerows(processed_features)

        print(f"Successfully converted {len(processed_features)} features to {output_file}")

    except Exception as e:
        print(f"Error: {str(e)}")


# Example usage
input_file = "vs.geojson"
output_file = "final.csv"
geojson_to_csv(input_file, output_file)