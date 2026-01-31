import folium
import pandas as pd
import numpy as np
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster, HeatMap

st.set_page_config(page_title="F&B Location Intelligence", layout="wide")


@st.cache_data
def load_data():
    df = pd.read_csv('dummy.csv')
    return df


df = load_data()

# 2. Sidebar - Parameter Bobot
st.sidebar.header('Konfigurasi Bobot AI')
w_traffic = st.sidebar.slider('Bobot Traffic', 0.0, 1.0, 0.5)
w_income = st.sidebar.slider('Bobot Pendapatan', 0.0, 1.0, 0.5)
w_rent = st.sidebar.slider('Bobot Biaya Sewa (Negatif)', 0.0, 1.0, 0.5)
w_comp = st.sidebar.slider("Bobot Kompetisi (Negatif)", 0.0, 1.0, 0.5)

selected_grades = st.sidebar.multiselect("Filter Grade", options=df['Grade'].unique(), default=df['Grade'].unique())

# 3. Logika Model
scaler = MinMaxScaler()
cols_to_scale = ['Avg_Income', 'Traffic_Daily', 'Competitors', 'Rent_Per_Year']
df_scaled = pd.DataFrame(scaler.fit_transform(df[cols_to_scale]), columns=cols_to_scale)

# Menghitung AI Score (Normalisasi ke 0-100)
raw_score = (df_scaled['Traffic_Daily'] * w_traffic) + \
            (df_scaled['Avg_Income'] * w_income) - \
            (df_scaled['Rent_Per_Year'] * w_rent) - \
            (df_scaled['Competitors'] * w_comp)

df['AI_Score'] = ((raw_score - raw_score.min()) / (raw_score.max() - raw_score.min()) * 100).round(2)

# Filter Data Berdasarkan Sidebar
filtered_df = df[df['Grade'].isin(selected_grades)]

# 4. Layout Dashboard
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader('Visualisasi Geospasial')

    # Fokus peta ke rata-rata koordinat data
    m = folium.Map(location=[filtered_df['Latitude'].mean(), filtered_df['Longitude'].mean()], zoom_start=12)

    # PILIHAN: Marker Cluster untuk 2000 titik agar tidak lag
    marker_cluster = MarkerCluster().add_to(m)

    for i, row in filtered_df.iterrows():
        # Warna berdasarkan Verdict
        if 'Sangat Cocok' in row['Verdict']:
            color = 'green'
        elif 'Cocok' in row['Verdict']:
            color = 'blue'
        else:
            color = 'red'

        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(f"""
                <b>ID: {row['Location_ID']}</b><br>
                Score: {row['AI_Score']}<br>
                Grade: {row['Grade']}<br>
                Verdict: {row['Verdict']}
            """, max_width=200),
            icon=folium.Icon(color=color, icon='home')
        ).add_to(marker_cluster)

    st_folium(m, width=850, height=600, returned_objects=[])

with col2:
    st.subheader('Tabel Analisis Lokasi')
    # Tampilkan kolom yang relevan saja
    display_df = filtered_df[['Location_ID', 'Grade', 'AI_Score', 'Verdict']].sort_values(by='AI_Score',
                                                                                          ascending=False)
    st.dataframe(display_df, height=600, hide_index=True)