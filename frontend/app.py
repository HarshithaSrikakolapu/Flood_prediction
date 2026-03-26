import streamlit as st
import numpy as np
import requests
import pandas as pd
import plotly.graph_objects as go
import time

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="PFEWS - Flood Prediction Dashboard",
    page_icon="🌊",
    layout="wide"
)

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1a1c24; border-radius: 10px; padding: 10px; border: 1px solid #30363d; }
    .risk-high { color: #ff4b4b; font-weight: bold; font-size: 24px; }
    .risk-medium { color: #ffa500; font-weight: bold; font-size: 24px; }
    .risk-low { color: #00ff00; font-weight: bold; font-size: 24px; }
    .weather-card { background-color: #1a1c24; border-radius: 10px; padding: 15px; border-left: 5px solid #4facfe; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("🌊 Predictive Flood Early Warning System")
st.markdown("### Multi-Source Sensor Fusion & Flow Simulation")

# Sidebar for Inputs
with st.sidebar:
    st.header("🛰️ Terrain & Weather Controls")
    rainfall = st.slider("Rainfall", 0.0, 1.0, 0.45, help="Normalized rainfall (0-1)")
    river_level = st.slider("River Level", 0.0, 1.0, 0.3, help="Normalized river level (0-1)")
    soil_moisture = st.slider("Soil Moisture", 0.0, 1.0, 0.6, help="Normalized soil moisture (0-1)")
    elevation = st.slider("Elevation", 0.1, 50.0, 10.0, help="Terrain elevation (m)")
    
    st.divider()
    if st.button("🚀 Predict Risk (Manual)", use_container_width=True):
        payload = {
            "rainfall": float(rainfall),
            "river_level": float(river_level),
            "soil_moisture": float(soil_moisture),
            "elevation": float(elevation)
        }
        try:
            res = requests.post(f"{BACKEND_URL}/predict", json=payload)
            if res.status_code == 200:
                st.session_state.risk_data = res.json()
                st.session_state.source = "Manual Slider"
                if 'weather_info' in st.session_state:
                    del st.session_state.weather_info
            else:
                st.error("Backend Error")
        except Exception as e:
            st.error(f"Connection Failed: {e}")

    st.divider()
    st.header("📍 Location Risk")
    loc_mode = st.radio("Mode", ["City", "Lat/Lon"], horizontal=True)
    
    loc_payload = {"elevation": float(elevation)}
    if loc_mode == "City":
        city_val = st.text_input("Enter City", "London")
        loc_payload["city"] = city_val
    else:
        clat, clon = st.columns(2)
        lat_val = clat.number_input("Lat", value=51.5074, format="%.4f")
        lon_val = clon.number_input("Lon", value=-0.1278, format="%.4f")
        loc_payload["lat"] = lat_val
        loc_payload["lon"] = lon_val

    if st.button("🔍 Get Location Risk", use_container_width=True):
        try:
            with st.spinner("Fetching weather data..."):
                res = requests.post(f"{BACKEND_URL}/predict/location", json=loc_payload)
                if res.status_code == 200:
                    api_data = res.json()
                    st.session_state.risk_data = {
                        "risk_score": api_data["risk_score"],
                        "risk_level": api_data["risk_level"]
                    }
                    st.session_state.weather_info = api_data["weather_data"]
                    st.session_state.source = f"Real-time: {api_data['weather_data']['city']}"
                    st.success(f"Weather fetched for {api_data['weather_data']['city']}")
                else:
                    st.error(f"Error: {res.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"Connection Failed: {e}")

# Main Dashboard
if 'risk_data' in st.session_state:
    risk = st.session_state.risk_data
    
    # Alert for HIGH risk
    if risk['risk_level'] == "HIGH":
        st.warning("⚠️ CRITICAL ALERT: High Flood Risk Detected! Immediate action may be required.", icon="🚨")
    
    # Data Source Header
    source_text = st.session_state.get('source', 'Default')
    st.markdown(f"#### Data Source: {source_text}")
    
    # Weather Info Card (if available)
    if 'weather_info' in st.session_state:
        w = st.session_state.weather_info
        
        st.markdown(f"""
            <div class="weather-card">
                <b>🌍 Location:</b> {w['city']} | 
                <b>🌡️ Temp:</b> {w['temp']}°C | 
                <b>💧 Humidity:</b> {w['humidity']}% | 
                <b>🌧️ Rainfall (1h):</b> {w['rainfall_1h']}mm
            </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Risk Score", f"{risk['risk_score']:.2f}")
    with col2:
        color = "red" if risk['risk_level'] == "HIGH" else "orange" if risk['risk_level'] == "MEDIUM" else "green"
        st.markdown(f"**Risk Level:** <span style='color:{color}; font-size:24px; font-weight:bold;'>{risk['risk_level']}</span>", unsafe_allow_html=True)

st.divider()

# 4. Grid Visualization (Heatmap)
st.subheader("🗺️ Flood Simulation Heatmap")
grid_size = 20

@st.cache_data
def get_mock_elevation(size):
    # Create simple depression in the center
    x = np.linspace(-2, 2, size)
    y = np.linspace(-2, 2, size)
    X, Y = np.meshgrid(x, y)
    Z = (X**2 + Y**2) * 5
    return Z.tolist()

elevation_grid = get_mock_elevation(grid_size)

if st.button("🌊 Run Simulation"):
    sim_payload = {
        "grid_size": grid_size,
        "elevation_grid": elevation_grid,
        "initial_water_level": 5.0 if 'risk_data' in st.session_state and st.session_state.risk_data['risk_level'] != "LOW" else 1.0,
        "rainfall_intensity": 10.0
    }
    
    history = None
    with st.spinner("Calculating water flow..."):
        try:
            res = requests.post(f"{BACKEND_URL}/simulate", json=sim_payload, timeout=10)
            if res.status_code == 200:
                history = res.json()['steps']
            else:
                st.error(f"Simulation failed: {res.text}")
        except Exception as e:
            st.error(f"Connection Failed: {e}")
            
    if history:
        st.success(f"✅ Simulation Data Loaded: {len(history)} frames.")
        
        # Diagnostic check
        total_water = np.sum(history[-1])
        st.write(f"### 🌊 System Check: {total_water:.2f} Units of Water")
        
        frame_idx = st.slider("🎞️ Manual Frame Scrub", 0, len(history)-1, 0)
        
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        
        z_elev = np.array(elevation_grid)
        z_water = np.array(history[frame_idx])
        
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')
        
        rows, cols = z_elev.shape
        X, Y = np.meshgrid(range(cols), range(rows))
        
        # Plot Terrain
        ax.plot_surface(X, Y, z_elev, cmap='terrain', alpha=0.6, label='Terrain')
        # Plot Water
        ax.plot_surface(X, Y, z_elev + z_water, cmap='winter', alpha=0.8, label='Water')
        
        ax.set_title(f"Flood Forecast - Step {frame_idx}")
        ax.set_zlabel("Height")
        plt.tight_layout()
        
        st.pyplot(fig)
        
        if st.button("▶️ Run Full Animation Trace"):
            placeholder = st.empty()
            for i, water_step in enumerate(history):
                z_w = np.array(water_step)
                f_anim = plt.figure(figsize=(8, 5))
                a_anim = f_anim.add_subplot(111, projection='3d')
                a_anim.plot_surface(X, Y, z_elev, cmap='terrain', alpha=0.5)
                a_anim.plot_surface(X, Y, z_elev + z_w, cmap='winter', alpha=0.7)
                a_anim.set_title(f"Animating: Step {i}")
                placeholder.pyplot(f_anim)
                plt.close(f_anim)
                time.sleep(0.01)
            st.balloons()
else:
    # Initial Elevation Heatmap
    fig = go.Figure(data=go.Heatmap(
        z=np.array(elevation_grid),
        colorscale='Viridis',
        colorbar=dict(title="Elevation")
    ))
    fig.update_layout(title="Terrain Elevation Map", template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("PFEWS - Analytics & Monitoring System | Multi-Source Sensor Fusion")
