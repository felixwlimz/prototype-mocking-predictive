import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Malaysian cities with accurate land-based coordinates
cities_data = {
    'Kuala Lumpur': {'lat': 3.1390, 'lon': 101.6869, 'count': 400},
    'George Town': {'lat': 5.4164, 'lon': 100.3327, 'count': 250},
    'Johor Bahru': {'lat': 1.4854, 'lon': 103.7618, 'count': 300},
    'Kota Kinabalu': {'lat': 5.9788, 'lon': 118.0894, 'count': 200},
    'Kuching': {'lat': 1.5533, 'lon': 110.3592, 'count': 200},
    'Ipoh': {'lat': 4.5921, 'lon': 101.0901, 'count': 220},
    'Shah Alam': {'lat': 3.0673, 'lon': 101.5186, 'count': 280},
    'Petaling Jaya': {'lat': 3.1731, 'lon': 101.5897, 'count': 320},
    'Subang Jaya': {'lat': 3.0456, 'lon': 101.5758, 'count': 250},
    'Klang': {'lat': 3.0333, 'lon': 101.5500, 'count': 200},
    'Seremban': {'lat': 2.7258, 'lon': 101.9424, 'count': 180},
    'Melaka': {'lat': 2.1896, 'lon': 102.2501, 'count': 200},
    'Alor Setar': {'lat': 6.1184, 'lon': 100.3688, 'count': 150},
    'Kota Bharu': {'lat': 6.1756, 'lon': 102.2381, 'count': 170},
    'Kuantan': {'lat': 3.8067, 'lon': 103.3256, 'count': 180},
    'Putrajaya': {'lat': 2.7258, 'lon': 101.6964, 'count': 220},
    'Cyberjaya': {'lat': 2.9264, 'lon': 101.6964, 'count': 200},
    'Ampang': {'lat': 3.1520, 'lon': 101.5901, 'count': 250},
    'Kajang': {'lat': 2.8386, 'lon': 101.7884, 'count': 200},
    'Sungai Petani': {'lat': 5.6411, 'lon': 100.5036, 'count': 180},
    'Sandakan': {'lat': 5.8250, 'lon': 118.1063, 'count': 120},
    'Tawau': {'lat': 4.2571, 'lon': 117.8860, 'count': 120},
    'Miri': {'lat': 4.3973, 'lon': 113.9849, 'count': 130},
    'Sibu': {'lat': 2.3053, 'lon': 111.8252, 'count': 140},
    'Bintulu': {'lat': 3.1883, 'lon': 113.0313, 'count': 120},
    'Kangar': {'lat': 6.4349, 'lon': 100.2048, 'count': 100},
    'Taiping': {'lat': 4.7433, 'lon': 100.7400, 'count': 130},
    'Bukit Mertajam': {'lat': 5.3667, 'lon': 100.4667, 'count': 140},
    'Butterworth': {'lat': 5.2833, 'lon': 100.3500, 'count': 150},
    'Bandar Seri Begawan': {'lat': 4.8830, 'lon': 114.9430, 'count': 150},
}

# Generate 5000 random locations clustered around cities
data = []
record_id = 1

for city, city_info in cities_data.items():
    city_lat = city_info['lat']
    city_lon = city_info['lon']
    count = city_info['count']
    
    for _ in range(count):
        # Create tight clusters around city centers (±0.02 degrees ≈ 2-3 km)
        # This keeps points on land and within city boundaries
        latitude = city_lat + np.random.normal(0, 0.015)
        longitude = city_lon + np.random.normal(0, 0.015)
        
        # Random metrics
        population_density = np.random.randint(5000, 15000)
        median_income_myr = np.random.randint(4000, 9000)
        competitor_count = np.random.randint(5, 80)
        mall_density_index = np.random.uniform(0.5, 4.0)
        office_density_index = np.random.uniform(0.5, 5.0)
        tourism_score = np.random.uniform(20, 85)
        halal_certified_area = np.random.choice([0, 1], p=[0.3, 0.7])
        location_score = np.random.uniform(20, 85)
        
        data.append({
            'branch_id': f'MY-{record_id:05d}',
            'country': 'Malaysia',
            'state': 'Various',
            'city': city,
            'latitude': latitude,
            'longitude': longitude,
            'population_density': population_density,
            'median_income_myr': median_income_myr,
            'competitor_count': competitor_count,
            'mall_density_index': mall_density_index,
            'office_density_index': office_density_index,
            'tourism_score': tourism_score,
            'halal_certified_area': halal_certified_area,
            'location_score': location_score
        })
        record_id += 1

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('malaysia_fnb_branches_2000.csv', index=False)

print(f"✅ Dataset generated successfully!")
print(f"📊 Total records: {len(df)}")
print(f"\n📍 Records per city:")
print(df['city'].value_counts().to_string())
print(f"\n📈 Dataset Statistics:")
print(f"   - Latitude range: {df['latitude'].min():.4f} to {df['latitude'].max():.4f}")
print(f"   - Longitude range: {df['longitude'].min():.4f} to {df['longitude'].max():.4f}")
print(f"   - Saved to: malaysia_fnb_branches_2000.csv")
