import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import os
import base64
from PIL import Image
import io
import plotly.io as pio
import json
import urllib.parse
from scipy import stats as scipy_stats


def fetch_additional_data(lat, lon, start_date, end_date):
    """Fetch additional data from GES DISC OPeNDAP"""
    try:
        # GES DISC API endpoint
        ges_disc_url = f"https://disc.gsfc.nasa.gov/api/search?lat={lat}&lon={lon}&startTime={start_date}&endTime={end_date}"
        response = requests.get(ges_disc_url)
        return response.json()
    except:
        return None

# Page config - MUST be first
st.set_page_config(
    page_title="🛡 Parade Guards: Weather Intelligence",
    layout="wide",
    page_icon="🛡",
    initial_sidebar_state="collapsed"
)

# NASA Space Theme CSS
st.markdown("""
<style>
    /* Mobile-First Base Styles */
    .stApp {
        max-width: 100vw;
        overflow-x: hidden;
    }

    /* Super Responsive Grid System */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        width: 100%;
    }

    /* Responsive Cards */
    .metric-card {
        width: 100%;
        min-height: 100px;
        padding: clamp(0.5rem, 2vw, 1rem);
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease;
        font-size: clamp(0.8rem, 2vw, 1rem);
    }

    /* Super Responsive Typography */
    .main-title {
        font-size: clamp(1.2rem, 5vw, 4rem);
        line-height: 1.1;
    }
    
    .subtitle {
        font-size: clamp(0.8rem, 2.5vw, 1.3rem);
        line-height: 1.3;
    }
    
    /* Responsive Panels */
    .mission-panel {
        width: 100%;
        max-width: 100vw;
        margin: clamp(0.5rem, 2vw, 1rem) 0;
        padding: clamp(0.8rem, 3vw, 2rem);
    }

    .panel-title {
        font-size: clamp(1rem, 3.5vw, 1.4rem);
        line-height: 1.2;
    }

    /* Super Responsive Buttons */
    .stButton > button {
        width: 100%;
        height: auto;
        min-height: clamp(40px, 8vw, 60px);
        padding: clamp(0.3rem, 1.5vw, 0.8rem);
        font-size: clamp(0.7rem, 2.5vw, 1rem);
        line-height: 1.2;
    }

    /* Responsive Charts */
    .js-plotly-plot {
        width: 100% !important;
        height: auto !important;
        min-height: clamp(200px, 40vw, 400px);
    }

    /* Responsive Inputs */
    .stSelectbox, .stNumberInput, .stDateInput {
        width: 100%;
        font-size: clamp(0.8rem, 2vw, 1rem);
    }

    /* Super Responsive Columns */
    [data-testid="column"] {
        padding: clamp(0.2rem, 1vw, 0.5rem);
    }

    /* Mobile Navigation - Enhanced */
    @media screen and (max-width: 480px) {
        .status-bar {
            flex-direction: column;
            text-align: center;
            gap: 0.5rem;
        }
        
        .header-content {
            padding: 0.5rem;
            flex-direction: column;
            gap: 1rem;
        }
        
        .logo-container {
            width: 60px;
            height: 60px;
        }
        
        .logo-image {
            width: 50px;
            height: 50px;
        }

        /* Stack all columns on very small screens */
        [data-testid="stHorizontalBlock"] > div {
            width: 100% !important;
            margin: 0.3rem 0;
        }
        
        /* Adjust chart heights for mobile */
        .js-plotly-plot {
            height: 200px !important;
        }
        
        /* Make metrics stack */
        [data-testid="metric-container"] {
            width: 100%;
            margin: 0.3rem 0;
        }

        /* Mobile sharing buttons */
        .stButton > button {
            min-height: 50px;
            font-size: 0.8rem;
        }
    }

    /* Small Mobile (320px and below) */
    @media screen and (max-width: 320px) {
        .main-title {
            font-size: 1.2rem;
        }
        
        .subtitle {
            font-size: 0.8rem;
        }
        
        .metric-card {
            min-height: 80px;
            padding: 0.5rem;
        }
        
        .stButton > button {
            min-height: 45px;
            font-size: 0.7rem;
        }
    }

    /* Mobile Navigation */
    @media screen and (max-width: 768px) {
        .status-bar {
            flex-direction: column;
            text-align: center;
        }
        
        .header-content {
            padding: 1rem;
        }
        
        .logo-container {
            width: 80px;
            height: 80px;
        }
        
        .logo-image {
            width: 60px;
            height: 60px;
        }

        /* Stack columns on mobile */
        [data-testid="stHorizontalBlock"] > div {
            width: 100%;
            margin: 0.5rem 0;
        }
        
        /* Adjust chart heights */
        .js-plotly-plot {
            height: 250px !important;
        }
        
        /* Make metrics stack */
        [data-testid="metric-container"] {
            width: 100%;
            margin: 0.5rem 0;
        }
    }

    /* Tablet Adjustments */
    @media screen and (min-width: 769px) and (max-width: 1024px) {
        .grid-container {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .mission-panel {
            padding: 1.5rem;
        }
    }

    /* Large Desktop */
    @media screen and (min-width: 1200px) {
        .grid-container {
            grid-template-columns: repeat(4, 1fr);
        }
        
        .mission-panel {
            padding: 2rem;
        }
    }

    /* Animation for Loading States */
    .stSpinner {
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
    }
    
    .main .block-container {
        padding-top: 2rem;
        max-width: 100%;
    }
    
    /* Animated Starfield */
    body::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(2px 2px at 20px 30px, #eee, transparent),
            radial-gradient(2px 2px at 40px 70px, rgba(255,255,255,0.8), transparent),
            radial-gradient(1px 1px at 90px 40px, #fff, transparent);
        background-repeat: repeat;
        background-size: 200px 100px;
        animation: sparkle 20s linear infinite;
        pointer-events: none;
        z-index: -1;
    }
    
    @keyframes sparkle {
        from { transform: translateY(0px); }
        to { transform: translateY(-100px); }
    }
    
    @keyframes blink {
        0%, 50%, 100% { opacity: 1; }
        25%, 75% { opacity: 0.3; }
    }
    
    /* Mission Control Panels */
    .mission-panel {
        background: rgba(0, 0, 0, 0.7);
        border: 1px solid #00d4ff;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.2);
    }
    
    .panel-title {
        font-family: 'Orbitron', monospace;
        font-size: 1.4rem;
        color: #00d4ff;
        margin-bottom: 1rem;
        text-align: center;
        text-shadow: 0 0 10px #00d4ff;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border: 2px solid #00d4ff;
        border-radius: 8px;
        height: 60px;
        font-family: 'Orbitron', monospace;
        font-size: 16px;
        font-weight: 600;
        color: #ffffff;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
    }
    
    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.6);
        transform: translateY(-2px);
    }
    
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #ff0080 0%, #ff4081 100%);
        border: 2px solid #ff0080;
        animation: primaryPulse 2s ease-in-out infinite;
    }
    
    @keyframes primaryPulse {
        0%, 100% { box-shadow: 0 0 15px rgba(255, 0, 128, 0.4); }
        50% { box-shadow: 0 0 25px rgba(255, 0, 128, 0.8); }
    }
    
    /* Input Styling */
    .stSelectbox>div>div, .stNumberInput>div>div>input, .stDateInput>div>div>input {
        background: rgba(0, 0, 0, 0.8);
        border: 1px solid #00d4ff;
        border-radius: 5px;
        color: #ffffff;
    }
    
    /* Metric Cards */
    .metric-card {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid #00d4ff;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: #ff0080;
        box-shadow: 0 0 15px rgba(255, 0, 128, 0.3);
        transform: translateY(-2px);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Global Cities Database (Same as before)
# -----------------------------
# Replace the existing LOCATIONS dictionary with this expanded version

LOCATIONS = {
    "🇨🇦 Canada": {
        "Ontario": {
            "Toronto": (43.6532, -79.3832),
            "Ottawa": (45.4215, -75.6972),
            "Mississauga": (43.5890, -79.6441),
            "Brampton": (43.7315, -79.7624),
            "Hamilton": (43.2557, -79.8711),
            "London": (42.9849, -81.2453),
            "Windsor": (42.3149, -83.0364),
            "Vaughan": (43.8563, -79.5085),
            "Kitchener": (43.4516, -80.4925),
            "Markham": (43.8561, -79.3370)
        },
        "Quebec": {
            "Montreal": (45.5017, -73.5673),
            "Quebec City": (46.8139, -71.2080),
            "Laval": (45.6066, -73.7124),
            "Gatineau": (45.4765, -75.7013),
            "Longueuil": (45.5308, -73.5177),
            "Sherbrooke": (45.4040, -71.8929),
            "Saguenay": (48.4279, -71.0485),
            "Levis": (46.7382, -71.2465),
            "Trois-Rivieres": (46.3432, -72.5429),
            "Terrebonne": (45.6929, -73.6331)
        },
        "British Columbia": {
            "Vancouver": (49.2827, -123.1207),
            "Victoria": (48.4284, -123.3656),
            "Surrey": (49.1913, -122.8490),
            "Burnaby": (49.2488, -122.9805),
            "Richmond": (49.1666, -123.1336),
            "Abbotsford": (49.0504, -122.3045),
            "Coquitlam": (49.2838, -122.7932),
            "Kelowna": (49.8880, -119.4960),
            "Delta": (49.0847, -123.0587),
            "Nanaimo": (49.1659, -123.9401)
        }
    },
    "🇺🇸 United States": {
        "California": {
            "Los Angeles": (34.0522, -118.2437),
            "San Francisco": (37.7749, -122.4194),
            "San Diego": (32.7157, -117.1611),
            "San Jose": (37.3382, -121.8863),
            "Sacramento": (38.5816, -121.4944),
            "Oakland": (37.8044, -122.2712),
            "Long Beach": (33.7701, -118.1937),
            "Anaheim": (33.8366, -117.9143),
            "Santa Ana": (33.7455, -117.8677),
            "Riverside": (33.9534, -117.3962)
        },
        "New York": {
            "New York City": (40.7128, -74.0060),
            "Buffalo": (42.8864, -78.8784),
            "Rochester": (43.1566, -77.6088),
            "Syracuse": (43.0481, -76.1474),
            "Albany": (42.6526, -73.7562),
            "Yonkers": (40.9312, -73.8987),
            "Utica": (43.1009, -75.2327),
            "White Plains": (41.0340, -73.7629),
            "Binghamton": (42.0987, -75.9180),
            "Poughkeepsie": (41.7004, -73.9210)
        }
    },
    "🇬🇧 United Kingdom": {
        "England": {
            "London": (51.5074, -0.1278),
            "Manchester": (53.4808, -2.2426),
            "Birmingham": (52.4862, -1.8904),
            "Liverpool": (53.4084, -2.9916),
            "Leeds": (53.8008, -1.5491),
            "Sheffield": (53.3811, -1.4701),
            "Newcastle": (54.9783, -1.6178),
            "Nottingham": (52.9548, -1.1581),
            "Bristol": (51.4545, -2.5879),
            "Leicester": (52.6369, -1.1398)
        },
        "Scotland": {
            "Edinburgh": (55.9533, -3.1883),
            "Glasgow": (55.8642, -4.2518),
            "Aberdeen": (57.1497, -2.0943),
            "Dundee": (56.4620, -2.9707),
            "Inverness": (57.4778, -4.2247),
            "Perth": (56.3950, -3.4308),
            "Stirling": (56.1165, -3.9369),
            "St Andrews": (56.3398, -2.7967),
            "Falkirk": (56.0019, -3.7839),
            "Ayr": (55.4589, -4.6292)
        }
    },
    "🇮🇳 India": {
        "Maharashtra": {
            "Mumbai": (19.0760, 72.8777),
            "Pune": (18.5204, 73.8567),
            "Nagpur": (21.1458, 79.0882),
            "Nashik": (19.9975, 73.7898),
            "Aurangabad": (19.8762, 75.3433)
        },
        "Delhi": {
            "New Delhi": (28.6139, 77.2090),
            "North Delhi": (28.7041, 77.1025),
            "South Delhi": (28.5244, 77.1855),
            "East Delhi": (28.6280, 77.2789),
            "West Delhi": (28.6663, 77.0665)
        },
        "Tamil Nadu": {
            "Chennai": (13.0827, 80.2707),
            "Coimbatore": (11.0168, 76.9558),
            "Madurai": (9.9252, 78.1198),
            "Salem": (11.6643, 78.1460),
            "Tiruchirappalli": (10.7905, 78.7047)
        }
    },
    "🇯🇵 Japan": {
        "Kanto": {
            "Tokyo": (35.6762, 139.6503),
            "Yokohama": (35.4437, 139.6380),
            "Saitama": (35.8616, 139.6455),
            "Chiba": (35.6074, 140.1065),
            "Kawasaki": (35.5308, 139.7029)
        },
        "Kansai": {
            "Osaka": (34.6937, 135.5023),
            "Kyoto": (35.0116, 135.7681),
            "Kobe": (34.6901, 135.1955),
            "Nara": (34.6851, 135.8048),
            "Wakayama": (34.2305, 135.1708)
        }
    }
}
if 'share_image' not in st.session_state:
    st.session_state.share_image = None
if 'location_name' not in st.session_state:
    st.session_state.location_name = None
if 'latitude' not in st.session_state:
    st.session_state.latitude = None
if 'longitude' not in st.session_state:
    st.session_state.longitude = None
if 'target_date' not in st.session_state:
    st.session_state.target_date = None
if 'selected_activity' not in st.session_state:
    st.session_state.selected_activity = None
# Initialize session state for persistent data
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'df_filtered' not in st.session_state:
    st.session_state.df_filtered = None
if 'risks' not in st.session_state:
    st.session_state.risks = None
if 'overall_risk' not in st.session_state:
    st.session_state.overall_risk = None
if 'stats' not in st.session_state:
    st.session_state.stats = None
# You can continue adding more countries following the same pattern:
# "🇦🇺 Australia", "🇩🇪 Germany", "🇫🇷 France", "🇮🇹 Italy", etc.

# -----------------------------
# Activity Profiles
# -----------------------------
ACTIVITY_PROFILES = {
    "Beach Day 🏖": {
        "icon": "🏖",
        "thresholds": {"temp_min": 22, "temp_max": 38, "rain": 2, "wind": 10},
        "description": "Sunshine, warm temps, light winds"
    },
    "Hiking/Trail 🥾": {
        "icon": "🥾",
        "thresholds": {"temp_min": 5, "temp_max": 32, "rain": 5, "wind": 15},
        "description": "Moderate temps, dry conditions"
    },
    "Picnic/BBQ 🧺": {
        "icon": "🧺",
        "thresholds": {"temp_min": 15, "temp_max": 35, "rain": 1, "wind": 12},
        "description": "Pleasant weather, no rain"
    },
    "Parade/Festival 🎉": {
        "icon": "🎉",
        "thresholds": {"temp_min": 0, "temp_max": 35, "rain": 3, "wind": 15},
        "description": "Comfortable for crowds"
    },
    "General Outdoor 🌳": {
        "icon": "🌳",
        "thresholds": {"temp_min": 10, "temp_max": 32, "rain": 3, "wind": 12},
        "description": "Comfortable conditions"
    }
}

# -----------------------------
# Core Functions (Same as working version)
# -----------------------------
@st.cache_data(ttl=7200, show_spinner=False)
def fetch_enhanced_weather_data(lat, lon, target_month, target_day, years_back=15):
    """Fetch comprehensive weather data including humidity, snow, and air quality proxies"""
    all_data = []
    current_year = datetime.now().year
    start_year = max(1981, current_year - years_back)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    successful_years = 0
    
    for idx, year in enumerate(range(start_year, current_year)):
        try:
            status_text.text(f"📡 Fetching enhanced data: {year} ({idx+1}/{current_year-start_year})")
            
            try:
                center_date = datetime(year, target_month, target_day)
            except ValueError:
                if target_month == 2 and target_day == 29:
                    center_date = datetime(year, 2, 28)
                else:
                    continue
            
            start_date = center_date - timedelta(days=5)
            end_date = center_date + timedelta(days=5)
            
            # Enhanced parameters including humidity, cloud cover, and more
            url = (f"https://power.larc.nasa.gov/api/temporal/daily/point?"
                   f"parameters=T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,WS2M,RH2M,CLOUD_AMT,QV2M,PS&"
                   f"community=RE&longitude={lon}&latitude={lat}&"
                   f"start={start_date.strftime('%Y%m%d')}&end={end_date.strftime('%Y%m%d')}&format=JSON")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if 'properties' not in data or 'parameter' not in data['properties']:
                continue
            
            parameters = data['properties']['parameter']
            
            for date_str in parameters['T2M'].keys():
                date_obj = datetime.strptime(date_str, "%Y%m%d")
                
                # Extract all available parameters
                temp = parameters.get('T2M', {}).get(date_str)
                temp_max = parameters.get('T2M_MAX', {}).get(date_str)
                temp_min = parameters.get('T2M_MIN', {}).get(date_str)
                precip = parameters.get('PRECTOTCORR', {}).get(date_str)
                wind = parameters.get('WS2M', {}).get(date_str)
                humidity = parameters.get('RH2M', {}).get(date_str)
                cloud_cover = parameters.get('CLOUD_AMT', {}).get(date_str)
                specific_humidity = parameters.get('QV2M', {}).get(date_str)
                pressure = parameters.get('PS', {}).get(date_str)
                
                # Calculate heat index (feels-like temperature)
                heat_index = None
                if temp and humidity:
                    if temp >= 27:  # Heat index only relevant at higher temps
                        heat_index = calculate_heat_index(temp, humidity)
                
                if all(v not in [None, -999, -999.0] for v in [temp, temp_max, temp_min, precip, wind]):
                    all_data.append({
                        'year': year, 'date': date_obj, 'month': date_obj.month, 'day': date_obj.day,
                        'temperature': float(temp), 'temp_max': float(temp_max), 'temp_min': float(temp_min),
                        'precipitation': float(precip), 'wind_speed': float(wind),
                        'humidity': float(humidity) if humidity not in [None, -999, -999.0] else None,
                        'cloud_cover': float(cloud_cover) if cloud_cover not in [None, -999, -999.0] else None,
                        'heat_index': heat_index,
                        'pressure': float(pressure) if pressure not in [None, -999, -999.0] else None
                    })
            
            successful_years += 1
            progress_bar.progress((idx + 1) / (current_year - start_year))
        except:
            pass
    
    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(all_data)

def calculate_heat_index(temp_c, humidity):
    """Calculate heat index (feels-like temperature)"""
    try:
        # Convert to Fahrenheit for calculation
        temp_f = temp_c * 9/5 + 32
        
        # Simplified heat index formula
        hi = -42.379 + 2.04901523*temp_f + 10.14333127*humidity \
             - 0.22475541*temp_f*humidity - 0.00683783*temp_f*temp_f \
             - 0.05481717*humidity*humidity + 0.00122874*temp_f*temp_f*humidity \
             + 0.00085282*temp_f*humidity*humidity - 0.00000199*temp_f*temp_f*humidity*humidity
        
        # Convert back to Celsius
        hi_c = (hi - 32) * 5/9
        return hi_c
    except:
        return None
def create_interactive_map(lat, lon, location_name):
    """Create an interactive map with location marker"""
    import plotly.express as px
    
    df_map = pd.DataFrame({
        'lat': [lat],
        'lon': [lon],
        'location': [location_name]
    })
    
    fig = px.scatter_mapbox(
        df_map, 
        lat='lat', 
        lon='lon',
        hover_name='location',
        zoom=8,
        height=400,
        color_discrete_sequence=['#00d4ff']
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#ffffff"}
    )
    
    return fig

def calculate_enhanced_weather_risks(df, target_month, target_day, thresholds):
    """Enhanced risk calculation including humidity and heat index"""
    df_filtered = df[(df['month'] == target_month) & (abs(df['day'] - target_day) <= 3)].copy()
    
    if len(df_filtered) < 10:
        return None
    
    total_days = len(df_filtered)
    
    risks = {
        'too_cold': (df_filtered['temp_min'] < thresholds['temp_min']).sum() / total_days * 100,
        'too_hot': (df_filtered['temp_max'] > thresholds['temp_max']).sum() / total_days * 100,
        'rainy': (df_filtered['precipitation'] >= thresholds['rain']).sum() / total_days * 100,
        'windy': (df_filtered['wind_speed'] >= thresholds['wind']).sum() / total_days * 100
    }
    
    # Add humidity risk if available
    if 'humidity' in df_filtered.columns and df_filtered['humidity'].notna().sum() > 10:
        risks['high_humidity'] = (df_filtered['humidity'] > 80).sum() / total_days * 100
    
    # Add uncomfortable heat index risk
    if 'heat_index' in df_filtered.columns and df_filtered['heat_index'].notna().sum() > 10:
        risks['uncomfortable_heat'] = (df_filtered['heat_index'] > 35).sum() / total_days * 100
    
    bad_weather_days = (
        (df_filtered['temp_min'] < thresholds['temp_min']) |
        (df_filtered['temp_max'] > thresholds['temp_max']) |
        (df_filtered['precipitation'] >= thresholds['rain']) |
        (df_filtered['wind_speed'] >= thresholds['wind'])
    ).sum()
    
    overall_risk = (bad_weather_days / total_days) * 100
    
    stats = {
        'avg_temp': df_filtered['temperature'].mean(),
        'typical_high': df_filtered['temp_max'].median(),
        'typical_low': df_filtered['temp_min'].median(),
        'max_temp_ever': df_filtered['temp_max'].max(),
        'min_temp_ever': df_filtered['temp_min'].min(),
        'avg_precip': df_filtered['precipitation'].mean(),
        'max_precip_ever': df_filtered['precipitation'].max(),
        'avg_wind': df_filtered['wind_speed'].mean(),
        'max_wind_ever': df_filtered['wind_speed'].max(),
        'rainy_days': (df_filtered['precipitation'] >= 1.0).sum(),
        'total_days': total_days,
        'years_analyzed': df_filtered['year'].nunique(),
        'avg_humidity': df_filtered['humidity'].mean() if 'humidity' in df_filtered.columns else None,
        'avg_cloud_cover': df_filtered['cloud_cover'].mean() if 'cloud_cover' in df_filtered.columns else None
    }
    
    return risks, overall_risk, stats, df_filtered

def create_risk_gauge(overall_risk):
    if overall_risk < 20:
        color, status = "#00ff64", "MISSION GO 🚀"
    elif overall_risk < 40:
        color, status = "#00d4ff", "NOMINAL ✅"
    elif overall_risk < 60:
        color, status = "#ffa500", "CAUTION ⚠"
    else:
        color, status = "#ff0080", "HIGH RISK ❌"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_risk,
        title={'text': f"🛰 {status}", 'font': {'size': 24, 'color': color, 'family': "Orbitron"}},
        number={'suffix': "%", 'font': {'size': 48, 'color': color}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': "#00d4ff"},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 20], 'color': 'rgba(0, 255, 100, 0.3)'},
                {'range': [20, 40], 'color': 'rgba(0, 212, 255, 0.3)'},
                {'range': [40, 60], 'color': 'rgba(255, 165, 0, 0.3)'},
                {'range': [60, 100], 'color': 'rgba(255, 0, 128, 0.3)'}
            ]
        }
    ))
    
    fig.update_layout(
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#ffffff"},
        margin=dict(t=50, b=50, l=50, r=50),  # Responsive margins
        autosize=True  # Make plot responsive
    )
    return fig

def create_risk_breakdown(risks):
    labels = ['❄ COLD', '🔥 HEAT', '🌧 RAIN', '💨 WIND']
    values = [risks['too_cold'], risks['too_hot'], risks['rainy'], risks['windy']]
    
    fig = go.Figure(go.Bar(
        x=labels, y=values,
        text=[f'{v:.1f}%' for v in values],
        textposition='outside',
        marker_color=['#00d4ff', '#ff0080', '#00ff64', '#ffa500']
    ))
    
    fig.update_layout(
        title={'text': '🛰 THREAT ASSESSMENT', 'font': {'color': '#00d4ff', 'family': "Orbitron"}},
        yaxis={'gridcolor': 'rgba(0, 212, 255, 0.2)'},
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "#ffffff"}
    )
    return fig
def create_weather_trend_analysis(df_filtered, variable='temperature'):
    """Create comprehensive trend analysis with regression"""
    fig = go.Figure()
    
    # Group by year and calculate mean
    yearly_data = df_filtered.groupby('year')[variable].mean().reset_index()
    
    # Add scatter plot
    fig.add_trace(go.Scatter(
        x=yearly_data['year'],
        y=yearly_data[variable],
        mode='markers',
        name='Yearly Average',
        marker=dict(size=10, color='#00d4ff')
    ))
    
    # Add trend line
    if len(yearly_data) > 2:
        z = np.polyfit(yearly_data['year'], yearly_data[variable], 1)
        p = np.poly1d(z)
        
        fig.add_trace(go.Scatter(
            x=yearly_data['year'],
            y=p(yearly_data['year']),
            mode='lines',
            name=f'Trend (slope: {z[0]:.3f}°C/year)',
            line=dict(color='#ff0080', width=3, dash='dash')
        ))
    
    # Add moving average
    if len(yearly_data) >= 3:
        yearly_data['ma'] = yearly_data[variable].rolling(window=3, center=True).mean()
        fig.add_trace(go.Scatter(
            x=yearly_data['year'],
            y=yearly_data['ma'],
            mode='lines',
            name='3-Year Moving Average',
            line=dict(color='#00ff64', width=2)
        ))
    
    fig.update_layout(
        title=f'🔮 Long-term {variable.replace("_", " ").title()} Trend',
        xaxis_title='Year',
        yaxis_title=f'{variable.replace("_", " ").title()}',
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "#ffffff"},
        hovermode='x unified',
        height=450
    )
    
    return fig
def create_probability_curve(df_filtered, variable, thresholds):
    """Create probability distribution with bell curve"""
    data = df_filtered[variable].dropna()
    
    if len(data) < 10:
        return None
    
    fig = go.Figure()
    
    # Histogram
    fig.add_trace(go.Histogram(
        x=data,
        nbinsx=30,
        name="Observed Frequency",
        marker_color='#00d4ff',
        opacity=0.7,
        histnorm='probability density'
    ))
    
    # Fit normal distribution
    mu = data.mean()
    sigma = data.std()
    x_range = np.linspace(data.min(), data.max(), 100)
    y_fit = scipy_stats.norm.pdf(x_range, mu, sigma)
    
    fig.add_trace(go.Scatter(
        x=x_range,
        y=y_fit,
        mode='lines',
        name='Normal Distribution Fit',
        line=dict(color='#ff0080', width=3)
    ))
    
    # Add threshold markers
    if variable == 'temperature' and 'temp_max' in thresholds:
        fig.add_vline(
            x=thresholds['temp_max'],
            line_dash="dash",
            line_color="#ff0080",
            annotation_text=f"Too Hot: {thresholds['temp_max']}°C"
        )
    elif variable == 'precipitation' and 'rain' in thresholds:
        fig.add_vline(
            x=thresholds['rain'],
            line_dash="dash",
            line_color="#00ff64",
            annotation_text=f"Rain Threshold: {thresholds['rain']}mm"
        )
    
    fig.update_layout(
        title=f'📊 Probability Distribution - {variable.replace("_", " ").title()}',
        xaxis_title=variable.replace("_", " ").title(),
        yaxis_title='Probability Density',
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "#ffffff"},
        height=400,
        showlegend=True
    )
    
    return fig
def calculate_confidence_score(stats):
    years = stats['years_analyzed']
    days = stats['total_days']
    
    if years >= 10 and days >= 50:
        return "HIGH ✅", "#00ff64"
    elif years >= 5 and days >= 25:
        return "MEDIUM ⚠", "#ffa500"
    else:
        return "LOW ❌", "#ff0080"
    
def prepare_data_with_metadata(df, location, date):
    """Add metadata to downloaded data"""
    metadata = {
        "data_source": "NASA POWER API",
        "location": location,
        "coordinates": f"Lat: {latitude}, Lon: {longitude}",
        "date_generated": datetime.now().strftime("%Y-%m-%d"),
        "units": {
            "temperature": "Celsius",
            "precipitation": "mm",
            "wind_speed": "m/s"
        },
        "data_variables": list(df.columns),
        "analysis_date": date.strftime("%Y-%m-%d")
    }
    
    if format_choice == "JSON":
        data = {
            "metadata": metadata,
            "data": json.loads(df.to_json(orient="records"))
        }
        return json.dumps(data)
    else:
        metadata_str = "\n".join([f"# {k}: {v}" for k, v in metadata.items()])
        return f"{metadata_str}\n\n{df.to_csv(index=False)}"

def create_shareable_image(location_name, target_date, selected_activity, overall_risk, stats, risks):
    """Create a shareable image with analysis results"""
    try:
        # Create combined figure for sharing with better formatting
        share_fig = go.Figure()
        
        # Add a simple background
        share_fig.add_trace(go.Scatter(
            x=[0, 1], y=[0, 1],
            mode='markers',
            marker=dict(size=1, color='rgba(0,0,0,0)'),
            showlegend=False
        ))
        
        # Layout with improved styling and proper margins
        share_fig.update_layout(
            title={
                'text': "🛡 PARADE GUARDS: Weather Intelligence Report",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 28, 'color': '#00d4ff', 'family': "Orbitron"}
            },
            paper_bgcolor="rgba(0,0,0,0.95)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={'color': "#ffffff", 'family': "Arial"},
            height=900,
            width=1200,
            showlegend=False,
            margin=dict(l=50, r=50, t=100, b=50),  # Proper margins
            annotations=[
                # Header with better spacing
                dict(
                    text=f"📍 LOCATION: {location_name}",
                    x=0.5, y=0.88,
                    showarrow=False,
                    font={'size': 20, 'color': '#00d4ff', 'family': "Arial"},
                    xanchor='center'
                ),
                dict(
                    text=f"📅 DATE: {target_date.strftime('%B %d, %Y')}",
                    x=0.5, y=0.84,
                    showarrow=False,
                    font={'size': 18, 'color': '#ffffff', 'family': "Arial"},
                    xanchor='center'
                ),
                # Activity with better formatting
                dict(
                    text=f"🎯 ACTIVITY: {selected_activity}",
                    x=0.5, y=0.78,
                    showarrow=False,
                    font={'size': 18, 'color': '#00ff64', 'family': "Arial"},
                    xanchor='center'
                ),
                # Risk Score with emphasis
                dict(
                    text=f"⚠ RISK ASSESSMENT: {overall_risk:.1f}%",
                    x=0.5, y=0.70,
                    showarrow=False,
                    font={'size': 24, 'color': '#ff0080', 'family': "Arial", 'weight': 'bold'},
                    xanchor='center'
                ),
                # Weather Stats with better layout
                dict(
                    text=f"🌡 TEMPERATURE: {stats['typical_low']:.1f}°C to {stats['typical_high']:.1f}°C",
                    x=0.5, y=0.62,
                    showarrow=False,
                    font={'size': 16, 'color': '#00d4ff', 'family': "Arial"},
                    xanchor='center'
                ),
                dict(
                    text=f"🌧 RAIN RISK: {risks['rainy']:.1f}%",
                    x=0.5, y=0.58,
                    showarrow=False,
                    font={'size': 16, 'color': '#00d4ff', 'family': "Arial"},
                    xanchor='center'
                ),
                dict(
                    text=f"💨 WIND RISK: {risks['windy']:.1f}%",
                    x=0.5, y=0.54,
                    showarrow=False,
                    font={'size': 16, 'color': '#00d4ff', 'family': "Arial"},
                    xanchor='center'
                ),
                # Additional stats
                dict(
                    text=f"📊 DATA: {stats['years_analyzed']} years analyzed ({stats['total_days']} days)",
                    x=0.5, y=0.46,
                    showarrow=False,
                    font={'size': 14, 'color': '#ffffff', 'family': "Arial"},
                    xanchor='center'
                ),
                # Footer with proper spacing
                dict(
                    text="Generated by Parade Guards Weather Intelligence System",
                    x=0.5, y=0.15,
                    showarrow=False,
                    font={'size': 14, 'color': '#ffffff', 'family': "Arial"},
                    xanchor='center'
                ),
                dict(
                    text="Data Source: NASA POWER API | 🛡 Weather Protection Active",
                    x=0.5, y=0.10,
                    showarrow=False,
                    font={'size': 12, 'color': '#00d4ff', 'family': "Arial"},
                    xanchor='center'
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        # # Convert to image with high quality
        # img_bytes = pio.to_image(share_fig, format="png", width=1200, height=900, scale=2)
        # return img_bytes
        st.plotly_chart(share_fig)

    except Exception as e:
        st.error(f"Error creating shareable image: {str(e)}")
        return None

# Add this after your analysis section, before the footer:
def create_temperature_distribution(df_filtered):
    """Create temperature distribution plot"""
    try:
        data = df_filtered['temperature'].dropna()
        
        fig = go.Figure()
        
        # Add histogram
        fig.add_trace(go.Histogram(
            x=data,
            nbinsx=30,
            name="Temperature Distribution",
            marker_color="#ff0080",
            opacity=0.7
        ))

        # Add mean line
        mean_value = data.mean()
        fig.add_vline(
            x=mean_value,
            line_dash="dash",
            line_color="white",
            annotation_text=f"Mean: {mean_value:.1f}°C",
            annotation_position="top"
        )

        # Update layout
        fig.update_layout(
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "#ffffff"},
        margin=dict(t=50, b=50, l=50, r=50),
        autosize=True,
        xaxis={'automargin': True},
        yaxis={'automargin': True}
    )
        return fig

    except Exception as e:
        st.error(f"Error creating temperature plot: {str(e)}")
        return None

# -----------------------------
# Load logo as base64
# -----------------------------
try:
    with open("2.png", "rb") as f:
        logo_bytes = f.read()
    logo_data_uri = f"data:image/png;base64,{base64.b64encode(logo_bytes).decode()}"
except FileNotFoundError:
    logo_data_uri = "2.png"
# -----------------------------
# Responsive Header
# -----------------------------
st.markdown(f"""
<style>
    /* Responsive Container */
    .header-container {{
        background: linear-gradient(135deg, #0c1445 0%, #1a237e 50%, #0c1445 100%);
        border: 2px solid #00d4ff;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem auto;
        text-align: center;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
        max-width: 1400px;
        width: 100%;
    }}

    /* Flex Layout */
    .header-content {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 2rem;
        flex-wrap: wrap;
    }}

    /* Logo Container */
    .logo-container {{
        flex: 0 0 auto;
        width: 120px;
        height: 120px;
        background: linear-gradient(135deg, #00d4ff 0%, #2196f3 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
        padding: 10px;
        transition: transform 0.3s ease;
    }}

    .logo-container:hover {{
        transform: scale(1.05);
    }}

    /* Logo Image */
    .logo-image {{
        width: 100px;
        height: 100px;
        object-fit: contain;
    }}

    /* Title Container */
    .title-container {{
        flex: 1;
        min-width: 300px;
        padding: 1rem;
    }}

    /* Responsive Typography */
    .main-title {{
        font-family: 'Orbitron', monospace;
        font-size: clamp(2rem, 5vw, 4rem);
        font-weight: 900;
        color: #00d4ff;
        text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff;
        margin: 0;
        line-height: 1.2;
    }}

    .subtitle {{
        font-family: 'Exo 2', sans-serif;
        font-size: clamp(1rem, 2vw, 1.3rem);
        color: #ffffff;
        margin-top: 0.5rem;
        opacity: 0.9;
    }}

    /* Status Bar */
    .status-bar {{
        margin-top: 1.5rem;
        font-family: 'Orbitron', monospace;
        font-size: clamp(0.8rem, 1.5vw, 1rem);
        display: flex;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }}

    /* Status Indicator */
    .status-indicator {{
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #00ff64;
        margin-right: 8px;
        animation: blink 1s infinite;
    }}

    @media (max-width: 768px) {{
        .header-content {{
            flex-direction: column;
            text-align: center;
        }}
        
        .logo-container {{
            margin: 0 auto;
        }}
        
        .status-bar {{
            flex-direction: column;
            gap: 0.5rem;
        }}
    }}
</style>

<div class="header-container">
    <div class="header-content">
        <div class="logo-container">
            <img src="{logo_data_uri}" class="logo-image" alt="Parade Guards Logo">
        </div>
        <div class="title-container">
            <div class="main-title">PARADE GUARDS</div>
            <div class="subtitle">WEATHER INTELLIGENCE SYSTEM</div>
        </div>
    </div>
    <div class="status-bar">
        <div>
            <span class="status-indicator"></span>
            <span style="color: #00ff64;">SYSTEMS ONLINE</span>
        </div>
        <span style="color: #ffa500;">|</span>
        <span style="color: #00d4ff;">NASA POWER API: CONNECTED</span>
        <span style="color: #ffa500;">|</span>
        <span style="color: #00d4ff;">WEATHER PROTECTION: ACTIVE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Mission Status
col1, col2, col3, col4 = st.columns(4)

# Replace the metrics section with this grid layout
st.markdown("""
<div class="grid-container">
    <div class="metric-card">
        <div style="font-family: 'Orbitron', monospace; color: #00d4ff;">📡 DATA SOURCE</div>
        <div style="font-size: clamp(1rem, 2vw, 1.5rem); font-weight: bold; color: #00ff64;">NASA POWER</div>
    </div>
    <div class="metric-card">
        <div style="font-family: 'Orbitron', monospace; color: #00d4ff;">🌍 COVERAGE</div>
        <div style="font-size: clamp(1rem, 2vw, 1.5rem); font-weight: bold; color: #00ff64;">GLOBAL</div>
    </div>
    <div class="metric-card">
        <div style="font-family: 'Orbitron', monospace; color: #00d4ff;">📅 ARCHIVE</div>
        <div style="font-size: clamp(1rem, 2vw, 1.5rem); font-weight: bold; color: #00ff64;">1981-2024</div>
    </div>
    <div class="metric-card">
        <div style="font-family: 'Orbitron', monospace; color: #00d4ff;">🛰 SATELLITES</div>
        <div style="font-size: clamp(1rem, 2vw, 1.5rem); font-weight: bold; color: #00ff64;">MULTI</div>
    </div>
</div>
""", unsafe_allow_html=True)
if 'selected_variable' not in st.session_state:
    st.session_state.selected_variable = "temperature"

# Initialize session state
if 'activity' not in st.session_state:
    st.session_state.activity = "General Outdoor 🌳"

# Location Selection
st.markdown('<div class="mission-panel"><div class="panel-title">🛡 LOCATION PROTECTION ZONE</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    selected_country = st.selectbox("🌍 COUNTRY", list(LOCATIONS.keys()))

with col2:
    provinces = list(LOCATIONS[selected_country].keys())
    selected_province = st.selectbox("🗺 REGION", provinces)

with col3:
    cities = list(LOCATIONS[selected_country][selected_province].keys())
    selected_city = st.selectbox("🏙 CITY", cities + ["🛰 Custom"])

if selected_city == "🛰 Custom":
    col_lat, col_lon = st.columns(2)
    with col_lat:
        latitude = st.number_input("Latitude", value=40.7128, format="%.4f")
    with col_lon:
        longitude = st.number_input("Longitude", value=-74.0060, format="%.4f")
    location_name = f"{latitude:.3f}°, {longitude:.3f}°"
else:
    latitude, longitude = LOCATIONS[selected_country][selected_province][selected_city]
    location_name = f"{selected_city}, {selected_province}"

st.info(f"📍 SECURED:** {location_name} | LAT: {latitude:.4f}° LON: {longitude:.4f}°")
# Show location on map
with st.expander("🗺 View Location on Map"):
   st.plotly_chart(create_interactive_map(latitude, longitude, location_name), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Date Selection
st.markdown('<div class="mission-panel"><div class="panel-title">📅 EVENT TIMELINE</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    target_date = st.date_input(
        "🗓 EVENT DATE",
        value=datetime.now() + timedelta(days=30),
        min_value=datetime.now(),
        max_value=datetime.now() + timedelta(days=365)
    )

with col2:
    st.info(f"{target_date.strftime('%B %d, %Y')}\n{target_date.strftime('%A')}")

st.markdown('</div>', unsafe_allow_html=True)

# Activity Selection
st.markdown('<div class="mission-panel"><div class="panel-title">🛡 ACTIVITY PROFILE</div>', unsafe_allow_html=True)

cols = st.columns(len(ACTIVITY_PROFILES))
for idx, (activity, profile) in enumerate(ACTIVITY_PROFILES.items()):
    with cols[idx]:
        if st.button(f"{profile['icon']}\n{activity.split()[0]}", key=f"act_{idx}", use_container_width=True):
            st.session_state.activity = activity

selected_activity = st.session_state.activity
st.success(f"ACTIVE: {selected_activity} - {ACTIVITY_PROFILES[selected_activity]['description']}")
st.markdown('</div>', unsafe_allow_html=True)

# Launch Button
# Launch Button
if st.button("🛡 LAUNCH PROTECTION ANALYSIS", type="primary", use_container_width=True):
    
    with st.spinner(f"🛰 Analyzing 15 years of enhanced data for {location_name}..."):
        df = fetch_enhanced_weather_data(latitude, longitude, target_date.month, target_date.day)
    
    if df.empty:
        st.error("❌ DATA UNAVAILABLE")
        st.session_state.analysis_complete = False
    else:
        result = calculate_enhanced_weather_risks(df, target_date.month, target_date.day, ACTIVITY_PROFILES[selected_activity]['thresholds'])
        
        if result is None:
            st.error("❌ INSUFFICIENT DATA")
            st.session_state.analysis_complete = False
        else:
            risks, overall_risk, stats, df_filtered = result
            
            # ONLY store in session state - NO display here!
            st.session_state.analysis_complete = True
            st.session_state.df_filtered = df_filtered
            st.session_state.risks = risks
            st.session_state.overall_risk = overall_risk
            st.session_state.stats = stats
            st.session_state.location_name = location_name
            st.session_state.latitude = latitude
            st.session_state.longitude = longitude
            st.session_state.target_date = target_date
            st.session_state.selected_activity = selected_activity

# NOW display results OUTSIDE the button
if st.session_state.analysis_complete:
    # Retrieve from session state
    risks = st.session_state.risks
    overall_risk = st.session_state.overall_risk
    stats = st.session_state.stats
    df_filtered = st.session_state.df_filtered
    location_name = st.session_state.location_name
    latitude = st.session_state.latitude
    longitude = st.session_state.longitude
    target_date = st.session_state.target_date
    selected_activity = st.session_state.selected_activity
    
    st.success(f"✅ ANALYSIS COMPLETE: {stats['years_analyzed']} years ({stats['total_days']} days)")
    
    # Add Interactive Map
    st.markdown('<div class="mission-panel"><div class="panel-title">🗺 TARGET LOCATION</div>', unsafe_allow_html=True)
    st.plotly_chart(create_interactive_map(latitude, longitude, location_name), use_container_width=True, key="analysis_map")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Intelligence Assessment
    st.markdown('<div class="mission-panel"><div class="panel-title">📊 INTELLIGENCE ASSESSMENT</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.plotly_chart(create_risk_gauge(overall_risk), use_container_width=True, key="risk_gauge_main")
    
    with col2:
        st.plotly_chart(create_risk_breakdown(risks), use_container_width=True, key="risk_breakdown_main")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced Stats
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🌡 High", f"{stats['typical_high']:.1f}°C", f"{stats['max_temp_ever']:.1f}°C max")
    with col2:
        st.metric("❄ Low", f"{stats['typical_low']:.1f}°C", f"{stats['min_temp_ever']:.1f}°C min")
    with col3:
        st.metric("🌧 Rain", f"{(stats['rainy_days']/stats['total_days'])*100:.0f}%", f"{stats['rainy_days']} days")
    with col4:
        st.metric("💨 Wind", f"{stats['avg_wind']:.1f} m/s", f"{stats['max_wind_ever']:.1f} max")
    with col5:
        if stats['avg_humidity']:
            st.metric("💧 Humidity", f"{stats['avg_humidity']:.0f}%", "Average")
        else:
            st.metric("☁️ Cloud", f"{stats['avg_cloud_cover']:.0f}%" if stats['avg_cloud_cover'] else "N/A", "Cover")
    
    # TREND ANALYSIS - Now this won't reset!
    st.markdown("---")
    st.markdown('<div class="mission-panel"><div class="panel-title">📈 CLIMATE TREND ANALYSIS</div>', unsafe_allow_html=True)
    
    trend_variable = st.selectbox(
        "Select Variable for Trend Analysis:",
        ["temperature", "precipitation", "wind_speed", "humidity"],
        help="See if conditions are changing over time",
        key="trend_selector"
    )
    
    if trend_variable in df_filtered.columns and df_filtered[trend_variable].notna().sum() > 10:
        st.plotly_chart(create_weather_trend_analysis(df_filtered, trend_variable), use_container_width=True, key=f"trend_{trend_variable}")
        
        # Calculate trend significance
        yearly_data = df_filtered.groupby('year')[trend_variable].mean().reset_index()
        if len(yearly_data) > 2:
            slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(yearly_data['year'], yearly_data[trend_variable])
            
            if p_value < 0.05:
                trend_direction = "increasing" if slope > 0 else "decreasing"
                st.warning(f"⚠️ **Significant Trend Detected**: {trend_variable.replace('_', ' ').title()} is {trend_direction} by {abs(slope):.3f} units/year (p={p_value:.4f})")
            else:
                st.info(f"📊 No significant trend detected for {trend_variable.replace('_', ' ').title()} (p={p_value:.4f})")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # PROBABILITY DISTRIBUTIONS
    st.markdown("---")
    st.markdown('<div class="mission-panel"><div class="panel-title">📊 PROBABILITY DISTRIBUTIONS</div>', unsafe_allow_html=True)
    
    prob_variable = st.selectbox(
        "Select Variable for Probability Analysis:",
        ["temperature", "precipitation", "wind_speed"],
        help="See the full probability distribution",
        key="prob_selector"
    )
    
    prob_fig = create_probability_curve(df_filtered, prob_variable, ACTIVITY_PROFILES[selected_activity]['thresholds'])
    if prob_fig:
        st.plotly_chart(prob_fig, use_container_width=True, key=f"prob_{prob_variable}")
        
        # Calculate probabilities
        data = df_filtered[prob_variable].dropna()
        percentiles = [10, 25, 50, 75, 90]
        values = np.percentile(data, percentiles)
        
        st.markdown("### 📊 Percentile Analysis")
        cols = st.columns(len(percentiles))
        for i, (p, v) in enumerate(zip(percentiles, values)):
            with cols[i]:
                st.metric(f"{p}th %ile", f"{v:.1f}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Temperature Distribution
    st.markdown("---")
    st.markdown('<div class="mission-panel"><div class="panel-title">🌡 TEMPERATURE DISTRIBUTION</div>', unsafe_allow_html=True)
    
    temp_fig = create_temperature_distribution(df_filtered)
    if temp_fig:
        st.plotly_chart(temp_fig, use_container_width=True, key="temp_dist_main")
    
    col1, col2, col3 = st.columns(3)
    temp_data = df_filtered['temperature'].dropna()
    
    with col1:
        st.metric("Average Temperature", f"{temp_data.mean():.1f}°C")
    with col2:
        st.metric("Temperature Range", f"{temp_data.min():.1f}°C to {temp_data.max():.1f}°C")
    with col3:
        st.metric("Standard Deviation", f"±{temp_data.std():.1f}°C")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Downloads and Sharing (keep your existing code)
    # ... rest of your download and sharing code ...
            
            # Continue with existing download and sharing sections...
            
    # Downloads
    st.markdown("---")
    st.markdown('<div class="mission-panel"><div class="panel-title">📥 DOWNLOAD OPTIONS</div>', unsafe_allow_html=True)
    
    format_choice = st.radio(
        "Select Format:",
        ["CSV", "JSON"],
        horizontal=True
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        summary = pd.DataFrame({
            'Location': [location_name],
            'Date': [target_date.strftime('%Y-%m-%d')],
            'Activity': [selected_activity],
            'Risk_Percent': [round(overall_risk, 2)],
            'High_C': [round(stats['typical_high'], 1)],
            'Low_C': [round(stats['typical_low'], 1)]
        })
        
        if format_choice == "CSV":
            download_data = prepare_data_with_metadata(summary, location_name, target_date)
            file_extension = "csv"
        else:
            download_data = summary.to_json(orient="records")
            file_extension = "json"
            
        st.download_button(
            "📊 DOWNLOAD SUMMARY", 
            download_data,
            f"summary_{target_date.strftime('%Y%m%d')}.{file_extension}",
            help="Download analysis summary",
            use_container_width=True
        )
    
    with col2:
        if format_choice == "CSV":
            full_data = prepare_data_with_metadata(df_filtered, location_name, target_date)
            file_extension = "csv"
        else:
            full_data = df_filtered.to_json(orient="records")
            file_extension = "json"
            
        st.download_button(
            "📁 DOWNLOAD FULL DATA",
            full_data,
            f"weather_data_{target_date.strftime('%Y%m%d')}.{file_extension}",
            help="Download complete dataset",
            use_container_width=True
        )
    st.markdown("---")
    st.markdown('<div class="mission-panel"><div class="panel-title">🌅 SHARE ANALYSIS</div>', unsafe_allow_html=True)
    
    # Create shareable image
    share_image = create_shareable_image(
        location_name, 
        target_date, 
        selected_activity, 
        overall_risk, 
        stats, 
        risks
    )
    st.session_state.share_image = share_image
    
    if share_image:
        # Display the shareable image
        st.image(share_image, caption="Your Weather Analysis Report", use_container_width=True)
        
        # Create WhatsApp text
        whatsapp_text = f"🌤 Weather Analysis Report 🛡\n\n"
        whatsapp_text += f"📍 Location: {location_name}\n"
        whatsapp_text += f"📅 Date: {target_date.strftime('%B %d, %Y')}\n"
        whatsapp_text += f"🎯 Activity: {selected_activity}\n\n"
        whatsapp_text += f"⚠ Risk Assessment: {overall_risk:.1f}%\n"
        whatsapp_text += f"🌡 Temperature: {stats['typical_low']:.1f}°C to {stats['typical_high']:.1f}°C\n"
        whatsapp_text += f"🌧 Rain Risk: {risks['rainy']:.1f}%\n"
        whatsapp_text += f"💨 Wind Risk: {risks['windy']:.1f}%\n\n"
        whatsapp_text += f"📊 Data: {stats['years_analyzed']} years analyzed ({stats['total_days']} days)\n\n"
        whatsapp_text += "🛡 Generated by Parade Guards Weather Intelligence System\n"
        whatsapp_text += "📡 Data Source: NASA POWER API"
        
        # Create WhatsApp URL
        import urllib.parse
        whatsapp_url = f"https://wa.me/?text={urllib.parse.quote(whatsapp_text)}"
        
        # Simple working solution with proper buttons
        col1, col2 = st.columns(2)
        
        with col1:
            # HTML download link - NO PAGE REFRESH
            st.markdown(f"""
            <a href="data:image/png;base64,{base64.b64encode(share_image).decode()}" download="weather_analysis_{target_date.strftime('%Y%m%d')}.png" style="
                display: block;
                background: linear-gradient(135deg, #00d4ff 0%, #2196f3 100%);
                border: 2px solid #00d4ff;
                border-radius: 8px;
                height: 60px;
                width: 100%;
                font-family: 'Orbitron', monospace;
                font-size: 18px;
                font-weight: 600;
                color: #ffffff;
                text-decoration: none;
                text-align: center;
                line-height: 60px;
                box-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
                cursor: pointer;
                margin: 0;
            ">
                📷 DOWNLOAD IMAGE
            </a>
            """, unsafe_allow_html=True)
        
        with col2:
            # WhatsApp sharing button
            st.markdown(f"""
            <a href="{whatsapp_url}" target="_blank" style="
                display: block;
                background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
                border: 2px solid #25D366;
                border-radius: 8px;
                height: 60px;
                width: 100%;
                font-family: 'Orbitron', monospace;
                font-size: 18px;
                font-weight: 600;
                color: #ffffff;
                text-decoration: none;
                text-align: center;
                line-height: 60px;
                box-shadow: 0 0 15px rgba(37, 211, 102, 0.4);
                cursor: pointer;
                margin: 0;
            ">
                📱 SHARE ON WHATSAPP
            </a>
            """, unsafe_allow_html=True)
        
        # Additional sharing options
        st.markdown("### 🌐 Other Sharing Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Email sharing
            email_subject = f"Weather Analysis for {location_name}"
            email_body = whatsapp_text
            email_url = f"mailto:?subject={urllib.parse.quote(email_subject)}&body={urllib.parse.quote(email_body)}"
            st.markdown(f"""
            <a href="{email_url}" target="_blank" style="
                display: block;
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
                border: 2px solid #ff6b6b;
                border-radius: 8px;
                height: 50px;
                width: 100%;
                font-family: 'Orbitron', monospace;
                font-size: 16px;
                font-weight: 600;
                color: #ffffff;
                text-decoration: none;
                text-align: center;
                line-height: 50px;
                box-shadow: 0 0 10px rgba(255, 107, 107, 0.4);
                cursor: pointer;
            ">
                📧 EMAIL
            </a>
            """, unsafe_allow_html=True)
        
        # with col2:
        #     # Twitter sharing
        #     twitter_text = f"🌤 Weather Analysis: {location_name} - Risk: {overall_risk:.1f}% - Generated by Parade Guards 🛡"
        #     twitter_url = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(twitter_text)}"
        #     st.markdown(f"""
        #     <a href="{twitter_url}" target="_blank" style="
        #         display: block;
        #         background: linear-gradient(135deg, #1DA1F2 0%, #0d8bd9 100%);
        #         border: 2px solid #1DA1F2;
        #         border-radius: 8px;
        #         height: 50px;
        #         width: 100%;
        #         font-family: 'Orbitron', monospace;
        #         font-size: 16px;
        #         font-weight: 600;
        #         color: #ffffff;
        #         text-decoration: none;
        #         text-align: center;
        #         line-height: 50px;
        #         box-shadow: 0 0 10px rgba(29, 161, 242, 0.4);
        #         cursor: pointer;
        #     ">
        #         🐦 TWITTER
        #     </a>
        #     """, unsafe_allow_html=True)
        
        with col3:
            # Copy text button
            if st.button("📋 COPY TEXT", use_container_width=True):
                st.code(whatsapp_text)
                st.success("Text copied! You can now paste it anywhere.")
        
        st.markdown("""
        <div style="text-align: center; color: #00d4ff; margin-top: 15px; font-size: 0.9rem;">
            💡 Download the image first, then use WhatsApp/Email/Twitter to share it with the text
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    # Replace the existing distribution analysis section with:
    # Replace the distribution analysis section with:
    st.markdown("---")
    # st.markdown('<div class="mission-panel"><div class="panel-title">🌡 TEMPERATURE DISTRIBUTION</div>', unsafe_allow_html=True)
    
    # try:
    #     temp_fig = create_temperature_distribution(df_filtered)
    #     if temp_fig:
    #         st.plotly_chart(temp_fig, use_container_width=True)
        
    #     # Temperature statistics
    #     col1, col2, col3 = st.columns(3)
    #     temp_data = df_filtered['temperature'].dropna()
        
    #     with col1:
    #         st.metric(
    #             "Average Temperature", 
    #             f"{temp_data.mean():.1f}°C"
    #         )
    #     with col2:
    #         st.metric(
    #             "Temperature Range", 
    #             f"{temp_data.min():.1f}°C to {temp_data.max():.1f}°C"
    #         )
    #     with col3:
    #         st.metric(
    #             "Standard Deviation", 
    #             f"±{temp_data.std():.1f}°C"
    #         )
        
    # except Exception as e:
    #     st.error("Unable to create temperature analysis")
    
    # st.markdown('</div>', unsafe_allow_html=True)



# Add in the analysis section
# st.markdown("### 📊 Data Distribution")
# variable = st.selectbox(
#     "Select Variable to Analyze:",
#     ["temperature", "precipitation", "wind_speed"]
# )
# st.plotly_chart(
#     create_probability_distribution(df_filtered, variable),
#     use_container_width=True
# )
# Footer
st.markdown("""
<div style="background: rgba(0, 0, 0, 0.7); border: 1px solid #00d4ff; border-radius: 15px; 
            padding: 2rem; margin: 3rem 0; text-align: center;">
    <div style="font-family: 'Orbitron', monospace; color: #00d4ff; font-size: 1.5rem; margin-bottom: 1rem;">
        🚀 NASA SPACE APPS CHALLENGE 2025
    </div>
    <div style="color: #ffffff;">
        Challenge: "Will It Rain On My Parade?"<br>
        Data: NASA POWER API | Built with Streamlit
    </div>
</div>
""", unsafe_allow_html=True)
