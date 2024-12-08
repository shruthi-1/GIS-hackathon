import pandas as pd
import folium
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
from folium import IFrame
file_path = 'C:/Users/shrut/PycharmProjects/hackathonrm/combined_data.csv'

df = pd.read_csv(file_path)

severe_pothole_df = df[df['Defects or Features'].str.contains('Severe Pothole', case=False, na=False)]

top_regions = severe_pothole_df['RoadName'].value_counts().head(3)

m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=10)

marker_cluster = MarkerCluster().add_to(m)

for index, row in severe_pothole_df.iterrows():
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=f"Road: {row['RoadName']}<br>Defects: {row['Defects or Features']}",
        icon=folium.Icon(color='red')
    ).add_to(marker_cluster)

map_output_path = "severe_potholes_map.html"
m.save(map_output_path)
print(f"Map saved to {map_output_path}")


plt.figure(figsize=(10, 6))
top_regions.plot(kind='bar')
plt.title("Top 3 Regions with Highest Number of Severe Potholes")
plt.xlabel("Region/Road Name")
plt.ylabel("Number of Severe Potholes")
plt.xticks(rotation=45)
plt.tight_layout()


chart_output_path = "top_severe_potholes_chart.png"
plt.savefig(chart_output_path)
print(f"Chart saved to {chart_output_path}")


image_fg = folium.FeatureGroup(name="Image Markers")

for index, row in severe_pothole_df.iterrows():
    raw_image_html = f'<img src="{row["RawImage"]}" width="300" height="200">'
    defect_image_html = f'<img src="{row["DetectedImage"]}" width="300" height="200">'

    iframe = IFrame(html=raw_image_html + defect_image_html, width=650, height=250)
    popup = folium.Popup(iframe, max_width=650)
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=popup,
        icon=folium.Icon(color='red')
    ).add_to(image_fg)

image_fg.add_to(m)
m