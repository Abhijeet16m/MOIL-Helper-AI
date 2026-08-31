import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Page Configuration (Enforces wide mode so the map isn't squeezed)
st.set_page_config(page_title="Desktop Map App", layout="wide")
st.title("🛰️ Streamlit Satellite Map View")

# 2. Add an interactive selector in case one server fails to load on your network
map_provider = st.sidebar.selectbox(
    "Select Satellite Provider",
    ["Esri World Imagery", "Google Satellite"]
)

# 3. Assign the mathematically exact tile URL string
if map_provider == "Esri World Imagery":
    tile_url = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
    attribution = "Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
else:
    tile_url = "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
    attribution = "Google"

# 4. Initialize the map object
start_lat, start_lon = 21.2514, 81.6296
base_map = folium.Map(
    location=[start_lat, start_lon], 
    zoom_start=12, 
    tiles=tile_url,
    attr=attribution
)

# 5. Render the Map (Forcing exact pixel allocations resolves CSS blank spaces)
st_folium(base_map, width=1100, height=600, returned_objects=[])
