import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
import os

os.makedirs('Output', exist_ok=True)

df = pd.read_csv('Data/restaurant_data.csv')

df['Aggregate rating'] = df['Aggregate rating'].fillna(0)
df['Average Cost for two'] = df['Average Cost for two'].fillna(df['Average Cost for two'].mean())
df['Cuisines'] = df['Cuisines'].fillna('Unknown')
df['City'] = df['City'].fillna('Unknown')
df['Locality'] = df['Locality'].fillna('Unknown')

plt.figure(figsize=(10,7))
plt.scatter(df['Longitude'], df['Latitude'], alpha=0.5, c='blue')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Restaurant Locations')
plt.tight_layout()
plt.savefig('Output/restaurant_locations.png')
plt.close()

map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
layered_map = folium.Map(location=map_center, zoom_start=12)

all_layer = folium.FeatureGroup(name='All Restaurants')
for _, row in df.iterrows():
    popup_text = f"""
    <b>{row['Restaurant Name']}</b><br>
    Cuisine: {row['Cuisines']}<br>
    Cost for Two: {row['Average Cost for two']:.2f}<br>
    Rating: {row['Aggregate rating']:.1f}
    """
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=3,
        popup=popup_text,
        color='blue',
        fill=True,
        fill_opacity=0.6
    ).add_to(all_layer)
layered_map.add_child(all_layer)

high_layer = folium.FeatureGroup(name='High-Rated (>=4.5)')
high_rated = df[df['Aggregate rating'] >= 4.5]
for _, row in high_rated.iterrows():
    popup_text = f"""
    <b>{row['Restaurant Name']}</b><br>
    Cuisine: {row['Cuisines']}<br>
    Cost for Two: {row['Average Cost for two']:.2f}<br>
    Rating: {row['Aggregate rating']:.1f}
    """
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=4,
        popup=popup_text,
        color='green',
        fill=True,
        fill_opacity=0.7
    ).add_to(high_layer)
layered_map.add_child(high_layer)

heat_layer = folium.FeatureGroup(name='Restaurant Density Heatmap')
heat_data = df[['Latitude', 'Longitude']].values.tolist()
HeatMap(heat_data, radius=15).add_to(heat_layer)
layered_map.add_child(heat_layer)

folium.LayerControl(collapsed=False).add_to(layered_map)

layered_map.save('Output/layered_restaurant_map.html')

group_col = 'City'
city_stats = df.groupby(group_col).agg({
    'Aggregate rating': 'mean',
    'Cuisines': lambda x: x.mode()[0] if not x.mode().empty else None,
    'Average Cost for two': 'mean',
    'Restaurant Name': 'count'
}).rename(columns={'Restaurant Name': 'restaurant_count'})

city_stats['Aggregate rating'] = city_stats['Aggregate rating'].round(2)
city_stats['Average Cost for two'] = city_stats['Average Cost for two'].round(2)

city_stats.to_csv('Output/city_stats.csv')

locality_stats = df.groupby('Locality').agg({
    'Aggregate rating': 'mean',
    'Restaurant Name': 'count'
}).rename(columns={'Restaurant Name': 'restaurant_count'})
locality_stats['Aggregate rating'] = locality_stats['Aggregate rating'].round(2)
locality_stats.to_csv('Output/locality_stats.csv')

def top_cuisines(x):
    return x.value_counts().head(3).index.tolist()

top_cuisine_stats = df.groupby('City')['Cuisines'].apply(top_cuisines)
top_cuisine_stats.to_csv('Output/top_cuisines_per_city.csv')

plt.figure(figsize=(12,6))
city_stats['restaurant_count'].sort_values(ascending=False).plot(kind='bar', color='skyblue')
plt.title('Number of Restaurants per City')
plt.ylabel('Restaurant Count')
plt.xlabel('City')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('Output/restaurants_per_city.png')
plt.close()

plt.figure(figsize=(8,8))
top_cuisines_overall = df['Cuisines'].value_counts().head(10)
top_cuisines_overall.plot(kind='pie', autopct='%1.1f%%', startangle=140, shadow=True)
plt.title('Top 10 Cuisines Distribution')
plt.ylabel('')
plt.tight_layout()
plt.savefig('Output/top_cuisines_pie.png')
plt.close()

plt.figure(figsize=(12,6))
city_stats['Aggregate rating'].sort_values(ascending=False).plot(kind='bar', color='orange')
plt.title('Average Restaurant Rating per City')
plt.ylabel('Average Rating')
plt.xlabel('City')
plt.xticks(rotation=45)
plt.ylim(0,5)
plt.tight_layout()
plt.savefig('Output/avg_rating_per_city.png')
plt.close()

plt.figure(figsize=(10,6))
plt.scatter(df['Average Cost for two'], df['Aggregate rating'], alpha=0.6, c='purple')
plt.xlabel('Average Cost for Two')
plt.ylabel('Aggregate Rating')
plt.title('Restaurant Cost vs Rating')
plt.tight_layout()
plt.savefig('Output/cost_vs_rating.png')
plt.close()

city_name = 'Makati City'
makati_df = df[df['City'] == city_name]
print(f"\nRestaurants in {city_name}:")
print(makati_df[['Restaurant Name','Cuisines','Aggregate rating','Average Cost for two']])

cuisine_name = 'Japanese'
japanese_df = df[df['Cuisines'].str.contains(cuisine_name)]
print(f"\n{cuisine_name} Restaurants:")
print(japanese_df[['Restaurant Name','City','Aggregate rating','Average Cost for two']])

print("\nEnhanced analysis complete! All plots saved in 'Output/' folder.")
print("Interactive map saved as 'layered_restaurant_map.html'.")
print("CSV summaries: city_stats.csv, locality_stats.csv, top_cuisines_per_city.csv")
