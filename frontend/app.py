import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(
    page_title="PFEWS - Flood Prediction Dashboard",
    page_icon="🌊",
    layout="wide"
)

# -------------------------------
# Simple Risk Model (Replace later with ML model)
# -------------------------------
def predict_risk(rainfall, river_level, soil_moisture, elevation):
    score = (
        0.4 * rainfall +
        0.3 * river_level +
        0.2 * soil_moisture -
        0.1 * (elevation / 50)
    )
    score = max(0, min(score, 1))

    if score > 0.7:
        level = "HIGH"
    elif score > 0.4:
        level = "MEDIUM"
    else:
        level = "LOW"

    return score, level


# -------------------------------
# UI
# -------------------------------
st.title("🌊 Predictive Flood Early Warning System")
st.markdown("### AI Risk Prediction ")

# Sidebar
with st.sidebar:
    st.header("🛰️ Controls")

    rainfall = st.slider("Rainfall", 0.0, 1.0, 0.5)
    river_level = st.slider("River Level", 0.0, 1.0, 0.4)
    soil_moisture = st.slider("Soil Moisture", 0.0, 1.0, 0.6)
    elevation = st.slider("Elevation (m)", 1.0, 50.0, 10.0)

    if st.button("🚀 Predict Risk"):
        score, level = predict_risk(
            rainfall, river_level, soil_moisture, elevation
        )

        st.session_state.risk = {
            "score": score,
            "level": level
        }

# -------------------------------
# Display Results
# -------------------------------
if "risk" in st.session_state:
    risk = st.session_state.risk

    if risk["level"] == "HIGH":
        st.warning("⚠️ HIGH FLOOD RISK!", icon="🚨")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Risk Score", f"{risk['score']:.2f}")

    with col2:
        color = {
            "HIGH": "red",
            "MEDIUM": "orange",
            "LOW": "green"
        }[risk["level"]]

        st.markdown(
            f"<h2 style='color:{color}'>{risk['level']}</h2>",
            unsafe_allow_html=True
        )

# -------------------------------
# Simulation (NO BACKEND)
# -------------------------------
st.subheader("🗺️ Flood Simulation")

grid_size = 20

def generate_terrain(size):
    x = np.linspace(-2, 2, size)
    y = np.linspace(-2, 2, size)
    X, Y = np.meshgrid(x, y)
    Z = (X**2 + Y**2) * 5
    return Z

terrain = generate_terrain(grid_size)

if st.button("🌊 Run Simulation"):

    water = np.zeros((grid_size, grid_size))

    # initialize water in center
    water[grid_size//2][grid_size//2] = 5

    frames = []

    for _ in range(30):
        new_water = water.copy()

        for i in range(1, grid_size-1):
            for j in range(1, grid_size-1):
                flow = water[i][j] * 0.2

                new_water[i][j] -= flow
                new_water[i+1][j] += flow/4
                new_water[i-1][j] += flow/4
                new_water[i][j+1] += flow/4
                new_water[i][j-1] += flow/4

        water = new_water
        frames.append(water.copy())

    st.success("Simulation complete")

    frame_idx = st.slider("Frame", 0, len(frames)-1, 0)

    z_water = frames[frame_idx]

    fig = go.Figure()

    fig.add_trace(go.Surface(z=terrain, colorscale='Greens', opacity=0.6))
    fig.add_trace(go.Surface(z=terrain + z_water, colorscale='Blues', opacity=0.8))

    fig.update_layout(
        title="Flood Simulation",
        scene=dict(zaxis_title="Height"),
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Initial Heatmap
# -------------------------------
else:
    fig = go.Figure(data=go.Heatmap(
        z=terrain,
        colorscale='Viridis'
    ))

    fig.update_layout(
        title="Terrain Elevation",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("Developed by Team Hack Forge")

