import pandas as pd
import numpy as np
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
import pydeck as pdk

st.set_page_config(
    page_title="F&B Location Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# DATA LOADING & PROCESSING
# ============================================================================

@st.cache_data
def load_data():
    """Load and prepare dataset"""
    df = pd.read_csv('malaysia_fnb_branches_2000.csv')
    return df

@st.cache_data
def calculate_scores(df, weights):
    """Calculate AI scores based on weights"""
    scaler = MinMaxScaler()
    cols = ['population_density', 'median_income_myr', 'mall_density_index', 
            'office_density_index', 'tourism_score', 'competitor_count']
    
    df_scaled = pd.DataFrame(scaler.fit_transform(df[cols]), columns=cols)
    
    raw_score = (
        df_scaled['population_density'] * weights['population'] +
        df_scaled['median_income_myr'] * weights['income'] +
        df_scaled['mall_density_index'] * weights['mall'] +
        df_scaled['office_density_index'] * weights['office'] +
        df_scaled['tourism_score'] * weights['tourism'] -
        df_scaled['competitor_count'] * weights['competitor']
    )
    
    return ((raw_score - raw_score.min()) / (raw_score.max() - raw_score.min()) * 100).round(2)

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

with st.sidebar:
    st.header("⚙️ Configuration")
    
    with st.expander("📊 Model Weights", expanded=True):
        weights = {
            'population': st.slider('Population Density', 0.0, 1.0, 0.3, step=0.05),
            'income': st.slider('Median Income', 0.0, 1.0, 0.25, step=0.05),
            'mall': st.slider('Mall Density', 0.0, 1.0, 0.2, step=0.05),
            'office': st.slider('Office Density', 0.0, 1.0, 0.15, step=0.05),
            'tourism': st.slider('Tourism Score', 0.0, 1.0, 0.1, step=0.05),
            'competitor': st.slider('Competitors (negative)', 0.0, 1.0, 0.2, step=0.05),
        }
    
    st.divider()
    st.header("🔍 Filters")
    
    # Load and process data
    df = load_data()
    df['AI_Score'] = calculate_scores(df, weights)
    df['Verdict'] = df['AI_Score'].apply(
        lambda x: 'Sangat Cocok' if x >= 70 else ('Cocok' if x >= 40 else 'Tidak Cocok')
    )
    
    # Filter controls
    verdict_filter = st.multiselect(
        "Verdict",
        options=sorted(df['Verdict'].unique()),
        default=sorted(df['Verdict'].unique())
    )
    
    city_filter = st.multiselect(
        "Cities",
        options=sorted(df['city'].unique()),
        default=sorted(df['city'].unique())[:5]
    )
    
    score_min, score_max = st.slider("AI Score Range", 0.0, 100.0, (0.0, 100.0), step=5.0)
    
    halal_only = st.checkbox("Halal Certified Only")

# ============================================================================
# APPLY FILTERS
# ============================================================================

filtered_df = df[
    (df['Verdict'].isin(verdict_filter)) &
    (df['city'].isin(city_filter)) &
    (df['AI_Score'] >= score_min) &
    (df['AI_Score'] <= score_max)
]

if halal_only:
    filtered_df = filtered_df[filtered_df['halal_certified_area'] == 1]

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.title("🗺️ F&B Location Intelligence")
st.markdown("Find the best locations for your food & beverage business across Malaysia")

if len(filtered_df) == 0:
    st.warning("⚠️ No locations match your filters. Try adjusting the criteria.")
else:
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📍 Locations", len(filtered_df))
    col2.metric("⭐ Avg Score", f"{filtered_df['AI_Score'].mean():.1f}")
    col3.metric("💰 Avg Income", f"RM {filtered_df['median_income_myr'].mean():.0f}")
    col4.metric("✅ Halal %", f"{(filtered_df['halal_certified_area'].sum() / len(filtered_df) * 100):.0f}%")
    
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["🗺️ Map", "📊 Table", "📈 Analytics"])
    
    # ========================================================================
    # MAP VIEW
    # ========================================================================
    with tab1:
        # Use Streamlit's native map (no Mapbox token required)
        map_data = filtered_df[['latitude', 'longitude']].copy()
        map_data.columns = ['lat', 'lon']
        
        st.map(map_data, zoom=7, use_container_width=True)
        
        st.info(f"📍 Showing {len(filtered_df)} locations across Malaysia")
    
    # ========================================================================
    # TABLE VIEW
    # ========================================================================
    with tab2:
        display_df = filtered_df[[
            'branch_id', 'city', 'median_income_myr', 'competitor_count',
            'tourism_score', 'halal_certified_area', 'AI_Score', 'Verdict'
        ]].sort_values('AI_Score', ascending=False).reset_index(drop=True)
        
        display_df.columns = ['Branch', 'City', 'Income (RM)', 'Competitors', 'Tourism', 'Halal', 'Score', 'Verdict']
        
        st.dataframe(display_df, use_container_width=True, height=500)
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="fnb_locations.csv",
            mime="text/csv"
        )
    
    # ========================================================================
    # ANALYTICS VIEW
    # ========================================================================
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Verdict Distribution")
            verdict_data = filtered_df['Verdict'].value_counts()
            st.bar_chart(verdict_data)
        
        with col2:
            st.subheader("Top 10 Cities")
            city_data = filtered_df['city'].value_counts().head(10)
            st.bar_chart(city_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Score Distribution")
            hist_data = pd.cut(filtered_df['AI_Score'], bins=10)
            hist_counts = hist_data.value_counts().sort_index()
            hist_df = pd.DataFrame({
                'Range': range(len(hist_counts)),
                'Count': hist_counts.values
            })
            st.bar_chart(hist_df.set_index('Range'))
        
        with col2:
            st.subheader("Income vs Score")
            scatter_data = filtered_df[['median_income_myr', 'AI_Score']].rename(
                columns={'median_income_myr': 'Income', 'AI_Score': 'Score'}
            )
            st.scatter_chart(scatter_data)
