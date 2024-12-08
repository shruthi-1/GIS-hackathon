import geopandas as gpd
import folium
import pandas as pd
from folium import FeatureGroup, LayerControl, Circle
from geopy.geocoders import Nominatim
import os
from folium.plugins import HeatMap
from IPython.display import IFrame

# Folder path containing CSV files
folder_path = "C:/Users/shrut/PycharmProjects/hackathonrm/dataset-hackathon"

# Combine CSV files
dataframes = []
for file_name in os.listdir(folder_path):
    if file_name.endswith('.csv'):
        file_path = os.path.join(folder_path, file_name)
        print(f"Processing file: {file_name}")
        df = pd.read_csv(file_path)
        dataframes.append(df)

combined_data = pd.concat(dataframes, ignore_index=True)

# Save the combined data to a CSV file
combined_data.to_csv("combined_data.csv", index=False)

# Ensure required columns exist
required_columns = {'Latitude', 'Longitude', 'RoadName', 'Defects or Features', 'RawImage', 'DetectedImage'}
missing_columns = required_columns - set(combined_data.columns)
if missing_columns:
    raise ValueError(f"Missing required columns in data: {missing_columns}")

# Filter severe potholes (example criteria; modify as needed)
severe_pothole_df = combined_data[combined_data['Defects or Features'].str.contains('Severe', na=False)]

# Initialize the folium map
if not combined_data.empty:
    map_center = [combined_data['Latitude'].mean(), combined_data['Longitude'].mean()]
else:
    map_center = [0, 0]  # Default center if data is empty

m = folium.Map(location=map_center, zoom_start=10)

# Severe Potholes Marker Cluster
marker_cluster = FeatureGroup(name="Severe Potholes")
for index, row in severe_pothole_df.iterrows():
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=f"Road: {row['RoadName']}<br>Defects: {row['Defects or Features']}",
        icon=folium.Icon(color='red', icon='exclamation-circle', prefix='fa')
    ).add_to(marker_cluster)
marker_cluster.add_to(m)

# Heatmap Layer
heatmap_layer = FeatureGroup(name="Pothole Heatmap", show=False)
heatmap_data = [[row['Latitude'], row['Longitude']] for index, row in combined_data.iterrows()]
HeatMap(heatmap_data, radius=10).add_to(heatmap_layer)
heatmap_layer.add_to(m)

# Image Layer
image_fg = FeatureGroup(name="Pothole Images")
for index, row in severe_pothole_df.iterrows():
    if pd.notna(row["RawImage"]) and pd.notna(row["DetectedImage"]):  # Ensure images are present
        # Combine raw and detected images into HTML
        html_content = f'''
        <div>
            <h4>Raw Image:</h4>
            <img src="{row["RawImage"]}" width="300" height="200"><br>
            <h4>Detected Image:</h4>
            <img src="{row["DetectedImage"]}" width="300" height="200">
        </div>
        '''

        # Create a folium.Popup directly from the HTML content
        popup = folium.Popup(html_content, max_width=650)

        # Add marker with the popup
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=popup,
            icon=folium.Icon(color='blue', icon='info-sign', prefix='glyphicon')
        ).add_to(image_fg)

image_fg.add_to(m)


# City Boundaries
city_boundaries_fg = FeatureGroup(name="City Boundaries", show=True)
geolocator = Nominatim(user_agent="top_cities")

# Example city list (replace with real data)
top_3_cities = ['New York', 'Los Angeles', 'Chicago']

for city in top_3_cities:
    try:
        location = geolocator.geocode(city)
        if location:
            latitude = location.latitude
            longitude = location.longitude
            Circle(
                location=[latitude, longitude],
                radius=5000,  # Adjust radius in meters
                color="pink",
                fill=True,
                fill_opacity=0.8,
                popup=f"{city} (Approximate Boundary)"
            ).add_to(city_boundaries_fg)
    except Exception as e:
        print(f"Error geocoding {city}: {e}")
city_boundaries_fg.add_to(m)

# Add LayerControl
LayerControl().add_to(m)

# Save the map
map_output_path = "enhanced_pothole_map.html"
m.save(map_output_path)
print(f"Enhanced map saved to {map_output_path}")
