import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import json
import random
import base64
from io import BytesIO
from PIL import Image

# Page config - MUST be first
st.set_page_config(
    page_title="🛡️ Parade Guards: Weather Intelligence",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed"
)

# NASA Space Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600&display=swap');
    
    /* Global Dark Theme */
    .stApp {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    
    /* Animated Starfield Background */
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
            radial-gradient(1px 1px at 90px 40px, #fff, transparent),
            radial-gradient(1px 1px at 130px 80px, rgba(255,255,255,0.6), transparent),
            radial-gradient(2px 2px at 160px 30px, #ddd, transparent);
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
    
    /* NASA Header with Glowing Effect */
    .nasa-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #1e3c72 100%);
        border: 2px solid #00d4ff;
        border-radius: 15px;
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: 
            0 0 20px rgba(0, 212, 255, 0.3),
            inset 0 0 20px rgba(0, 212, 255, 0.1);
    }
    
    .nasa-header::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #00d4ff, #ff0080, #00d4ff, #ff0080);
        border-radius: 15px;
        z-index: -1;
        animation: borderGlow 3s linear infinite;
    }
    
    @keyframes borderGlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .nasa-title {
        font-family: 'Orbitron', monospace;
        font-size: 3.5rem;
        font-weight: 900;
        color: #00d4ff;
        text-shadow: 
            0 0 10px #00d4ff,
            0 0 20px #00d4ff,
            0 0 30px #00d4ff;
        margin: 0;
        letter-spacing: 2px;
        animation: titleGlow 2s ease-in-out infinite alternate;
    }
    
    @keyframes titleGlow {
        from { text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff, 0 0 30px #00d4ff; }
        to { text-shadow: 0 0 20px #00d4ff, 0 0 30px #00d4ff, 0 0 40px #00d4ff; }
    }
    
    .nasa-subtitle {
        font-family: 'Exo 2', sans-serif;
        font-size: 1.3rem;
        color: #ffffff;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        letter-spacing: 1px;
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
    
    /* Space-themed Buttons */
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
        background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%);
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.6);
        transform: translateY(-2px);
    }
    
    /* Primary Button Special Styling */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #ff0080 0%, #ff4081 100%);
        border: 2px solid #ff0080;
        box-shadow: 0 0 15px rgba(255, 0, 128, 0.4);
        animation: primaryPulse 2s ease-in-out infinite;
    }
    
    @keyframes primaryPulse {
        0%, 100% { box-shadow: 0 0 15px rgba(255, 0, 128, 0.4); }
        50% { box-shadow: 0 0 25px rgba(255, 0, 128, 0.8); }
    }
    
    /* Select Box Styling */
    .stSelectbox>div>div {
        background: rgba(0, 0, 0, 0.8);
        border: 1px solid #00d4ff;
        border-radius: 5px;
        color: #ffffff;
    }
    
    /* Number Input Styling */
    .stNumberInput>div>div>input {
        background: rgba(0, 0, 0, 0.8);
        border: 1px solid #00d4ff;
        border-radius: 5px;
        color: #ffffff;
    }
    
    /* Date Input Styling */
    .stDateInput>div>div>input {
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
        margin: 0.5rem 0;
        backdrop-filter: blur(5px);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: #ff0080;
        box-shadow: 0 0 15px rgba(255, 0, 128, 0.3);
        transform: translateY(-2px);
    }
    
    /* Info Box Styling */
    .stInfo {
        background: rgba(0, 100, 255, 0.1);
        border: 1px solid #00d4ff;
        border-radius: 8px;
    }
    
    .stSuccess {
        background: rgba(0, 255, 100, 0.1);
        border: 1px solid #00ff64;
        border-radius: 8px;
    }
    
    .stWarning {
        background: rgba(255, 165, 0, 0.1);
        border: 1px solid #ffa500;
        border-radius: 8px;
    }
    
    .stError {
        background: rgba(255, 0, 0, 0.1);
        border: 1px solid #ff0000;
        border-radius: 8px;
    }
    
    /* Progress Bar Styling */
    .stProgress>div>div>div>div {
        background: linear-gradient(90deg, #00d4ff, #ff0080);
    }
    
    /* Spinner Styling */
    .stSpinner>div {
        border-color: #00d4ff transparent transparent transparent;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 100%);
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.3);
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #00d4ff, #ff0080);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #ff0080, #00d4ff);
    }
    
    /* Floating Elements Animation */
    .floating {
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Glitch Effect for Special Text */
    .glitch {
        position: relative;
        color: #00d4ff;
        font-size: 2rem;
        font-weight: bold;
        animation: glitch 2s linear infinite;
    }
    
    .glitch::before,
    .glitch::after {
        content: attr(data-text);
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }
    
    .glitch::before {
        animation: glitch-1 0.5s linear infinite reverse;
        color: #ff0080;
        z-index: -1;
    }
    
    .glitch::after {
        animation: glitch-2 0.5s linear infinite reverse;
        color: #00ff64;
        z-index: -2;
    }
    
    @keyframes glitch {
        0%, 100% { transform: translate(0); }
        20% { transform: translate(-2px, 2px); }
        40% { transform: translate(-2px, -2px); }
        60% { transform: translate(2px, 2px); }
        80% { transform: translate(2px, -2px); }
    }
    
    @keyframes glitch-1 {
        0%, 100% { transform: translate(0); }
        20% { transform: translate(2px, -2px); }
        40% { transform: translate(-2px, 2px); }
        60% { transform: translate(-2px, -2px); }
        80% { transform: translate(2px, 2px); }
    }
    
    @keyframes glitch-2 {
        0%, 100% { transform: translate(0); }
        20% { transform: translate(-2px, 2px); }
        40% { transform: translate(2px, 2px); }
        60% { transform: translate(2px, -2px); }
        80% { transform: translate(-2px, -2px); }
    }
    
    /* Mission Status Indicator */
    .mission-status {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        animation: statusBlink 1s infinite;
    }
    
    .status-online { background: #00ff64; }
    .status-warning { background: #ffa500; }
    .status-offline { background: #ff0000; }
    
    @keyframes statusBlink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    
    /* Space Station Tracker */
    .iss-tracker {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(255, 0, 128, 0.1) 100%);
        border: 2px solid #00d4ff;
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    /* Satellite Visualization */
    .satellite-viz {
        position: relative;
        height: 200px;
        background: radial-gradient(circle at center, rgba(0, 212, 255, 0.1) 0%, transparent 70%);
        border: 1px solid #00d4ff;
        border-radius: 10px;
        overflow: hidden;
    }
    
    .satellite {
        position: absolute;
        width: 8px;
        height: 8px;
        background: #00d4ff;
        border-radius: 50%;
        box-shadow: 0 0 10px #00d4ff;
        animation: orbit 10s linear infinite;
    }
    
    @keyframes orbit {
        from { transform: rotate(0deg) translateX(80px) rotate(0deg); }
        to { transform: rotate(360deg) translateX(80px) rotate(-360deg); }
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Global Cities Database
# -----------------------------
LOCATIONS = {
    "🇨🇦 Canada": {
        "Alberta": {
            "Calgary": (51.0447, -114.0719),
            "Edmonton": (53.5461, -113.4938),
            "Red Deer": (52.2681, -113.8111),
            "Lethbridge": (49.6942, -112.8328),
            "Fort McMurray": (56.7267, -111.3790)
        },
        "British Columbia": {
            "Vancouver": (49.2827, -123.1207),
            "Victoria": (48.4284, -123.3656),
            "Kelowna": (49.8880, -119.4960),
            "Kamloops": (50.6745, -120.3273),
            "Prince George": (53.9171, -122.7497)
        },
        "Manitoba": {
            "Winnipeg": (49.8951, -97.1384),
            "Brandon": (49.8483, -99.9501),
            "Steinbach": (49.5258, -96.6839),
            "Thompson": (55.7433, -97.8553)
        },
        "New Brunswick": {
            "Fredericton": (45.9636, -66.6431),
            "Saint John": (45.2733, -66.0633),
            "Moncton": (46.0878, -64.7782),
            "Bathurst": (47.6186, -65.6506)
        },
        "Newfoundland and Labrador": {
            "St. John's": (47.5615, -52.7126),
            "Corner Brook": (48.9500, -57.9522),
            "Gander": (48.9560, -54.6089),
            "Labrador City": (52.9462, -66.9118)
        },
        "Nova Scotia": {
            "Halifax": (44.6488, -63.5752),
            "Sydney": (46.1368, -60.1942),
            "Truro": (45.3669, -63.2755),
            "New Glasgow": (45.5939, -62.6358)
        },
        "Ontario": {
            "Toronto": (43.6532, -79.3832),
            "Ottawa": (45.4215, -75.6972),
            "Mississauga": (43.5890, -79.6441),
            "Hamilton": (43.2557, -79.8711),
            "London": (42.9849, -81.2453),
            "Windsor": (42.3149, -83.0364),
            "Kitchener": (43.4516, -80.4925),
            "Thunder Bay": (48.3809, -89.2477)
        },
        "Prince Edward Island": {
            "Charlottetown": (46.2382, -63.1311),
            "Summerside": (46.3950, -63.7890),
            "Stratford": (46.2169, -63.0886)
        },
        "Quebec": {
            "Montreal": (45.5017, -73.5673),
            "Quebec City": (46.8139, -71.2080),
            "Laval": (45.6066, -73.7124),
            "Gatineau": (45.4765, -75.7013),
            "Sherbrooke": (45.4042, -71.8929),
            "Trois-Rivières": (46.3432, -72.5477)
        },
        "Saskatchewan": {
            "Regina": (50.4452, -104.6189),
            "Saskatoon": (52.1332, -106.6700),
            "Prince Albert": (53.2033, -105.7531),
            "Moose Jaw": (50.3933, -105.5519)
        }
    },
    "🇺🇸 United States": {
        "California": {
            "Los Angeles": (34.0522, -118.2437),
            "San Francisco": (37.7749, -122.4194),
            "San Diego": (32.7157, -117.1611),
            "Sacramento": (38.5816, -121.4944),
            "San Jose": (37.3382, -121.8863),
            "Fresno": (36.7378, -119.7871)
        },
        "Texas": {
            "Houston": (29.7604, -95.3698),
            "Dallas": (32.7767, -96.7970),
            "Austin": (30.2672, -97.7431),
            "San Antonio": (29.4241, -98.4936),
            "Fort Worth": (32.7555, -97.3308)
        },
        "Florida": {
            "Miami": (25.7617, -80.1918),
            "Orlando": (28.5383, -81.3792),
            "Tampa": (27.9506, -82.4572),
            "Jacksonville": (30.3322, -81.6557),
            "Tallahassee": (30.4383, -84.2807)
        },
        "New York": {
            "New York City": (40.7128, -74.0060),
            "Buffalo": (42.8864, -78.8784),
            "Rochester": (43.1566, -77.6088),
            "Syracuse": (43.0481, -76.1474),
            "Albany": (42.6526, -73.7562)
        },
        "Illinois": {
            "Chicago": (41.8781, -87.6298),
            "Springfield": (39.7817, -89.6501),
            "Peoria": (40.6936, -89.5890),
            "Rockford": (42.2711, -89.0940)
        },
        "Washington": {
            "Seattle": (47.6062, -122.3321),
            "Spokane": (47.6588, -117.4260),
            "Tacoma": (47.2529, -122.4443),
            "Vancouver": (45.6387, -122.6615)
        },
        "Colorado": {
            "Denver": (39.7392, -104.9903),
            "Colorado Springs": (38.8339, -104.8214),
            "Aurora": (39.7294, -104.8319),
            "Boulder": (40.0150, -105.2705)
        },
        "Michigan": {
            "Detroit": (42.3314, -83.0458),
            "Grand Rapids": (42.9634, -85.6681),
            "Lansing": (42.7325, -84.5555),
            "Ann Arbor": (42.2808, -83.7430)
        }
    },
    "🇬🇧 United Kingdom": {
        "England": {
            "London": (51.5074, -0.1278),
            "Manchester": (53.4808, -2.2426),
            "Birmingham": (52.4862, -1.8904),
            "Liverpool": (53.4084, -2.9916),
            "Leeds": (53.8008, -1.5491),
            "Bristol": (51.4545, -2.5879)
        },
        "Scotland": {
            "Edinburgh": (55.9533, -3.1883),
            "Glasgow": (55.8642, -4.2518),
            "Aberdeen": (57.1497, -2.0943),
            "Dundee": (56.4620, -2.9707)
        },
        "Wales": {
            "Cardiff": (51.4816, -3.1791),
            "Swansea": (51.6214, -3.9436),
            "Newport": (51.5842, -2.9977)
        },
        "Northern Ireland": {
            "Belfast": (54.5973, -5.9301),
            "Londonderry": (54.9966, -7.3086)
        }
    },
    "🇦🇺 Australia": {
        "New South Wales": {
            "Sydney": (-33.8688, 151.2093),
            "Newcastle": (-32.9283, 151.7817),
            "Wollongong": (-34.4278, 150.8931),
            "Canberra": (-35.2809, 149.1300)
        },
        "Victoria": {
            "Melbourne": (-37.8136, 144.9631),
            "Geelong": (-38.1499, 144.3617),
            "Ballarat": (-37.5622, 143.8503)
        },
        "Queensland": {
            "Brisbane": (-27.4698, 153.0251),
            "Gold Coast": (-28.0167, 153.4000),
            "Cairns": (-16.9186, 145.7781),
            "Townsville": (-19.2590, 146.8169)
        },
        "Western Australia": {
            "Perth": (-31.9505, 115.8605),
            "Fremantle": (-32.0569, 115.7439),
            "Bunbury": (-33.3267, 115.6397)
        },
        "South Australia": {
            "Adelaide": (-34.9285, 138.6007),
            "Mount Gambier": (-37.8296, 140.7823)
        }
    },
    "🇮🇳 India": {
        "Maharashtra": {
            "Mumbai": (19.0760, 72.8777),
            "Pune": (18.5204, 73.8567),
            "Nagpur": (21.1458, 79.0882)
        },
        "Delhi": {
            "New Delhi": (28.6139, 77.2090),
            "Delhi": (28.7041, 77.1025)
        },
        "Karnataka": {
            "Bangalore": (12.9716, 77.5946),
            "Mysore": (12.2958, 76.6394),
            "Mangalore": (12.9141, 74.8560)
        },
        "Tamil Nadu": {
            "Chennai": (13.0827, 80.2707),
            "Coimbatore": (11.0168, 76.9558),
            "Madurai": (9.9252, 78.1198)
        },
        "West Bengal": {
            "Kolkata": (22.5726, 88.3639),
            "Darjeeling": (27.0410, 88.2663)
        }
    },
    "🇩🇪 Germany": {
        "Bavaria": {
            "Munich": (48.1351, 11.5820),
            "Nuremberg": (49.4521, 11.0767),
            "Augsburg": (48.3705, 10.8978)
        },
        "Berlin": {
            "Berlin": (52.5200, 13.4050)
        },
        "Hamburg": {
            "Hamburg": (53.5511, 9.9937)
        },
        "Hesse": {
            "Frankfurt": (50.1109, 8.6821),
            "Wiesbaden": (50.0825, 8.2400)
        }
    },
    "🇫🇷 France": {
        "Île-de-France": {
            "Paris": (48.8566, 2.3522),
            "Versailles": (48.8014, 2.1301)
        },
        "Provence": {
            "Marseille": (43.2965, 5.3698),
            "Nice": (43.7102, 7.2620),
            "Cannes": (43.5528, 7.0174)
        },
        "Auvergne-Rhône-Alpes": {
            "Lyon": (45.7640, 4.8357),
            "Grenoble": (45.1885, 5.7245)
        }
    },
    "🇯🇵 Japan": {
        "Tokyo": {
            "Tokyo": (35.6762, 139.6503),
            "Yokohama": (35.4437, 139.6380)
        },
        "Osaka": {
            "Osaka": (34.6937, 135.5023),
            "Kyoto": (35.0116, 135.7681)
        },
        "Hokkaido": {
            "Sapporo": (43.0642, 141.3469),
            "Hakodate": (41.7688, 140.7288)
        }
    },
    "🇲🇽 Mexico": {
        "Mexico City": {
            "Mexico City": (19.4326, -99.1332)
        },
        "Jalisco": {
            "Guadalajara": (20.6597, -103.3496),
            "Puerto Vallarta": (20.6534, -105.2253)
        },
        "Quintana Roo": {
            "Cancún": (21.1619, -86.8515),
            "Playa del Carmen": (20.6296, -87.0739)
        }
    }
}

# -----------------------------
# Activity Profiles
# -----------------------------
ACTIVITY_PROFILES = {
    "Beach Day 🏖️": {
        "icon": "🏖️",
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
    "Fishing/Boating 🎣": {
        "icon": "🎣",
        "thresholds": {"temp_min": 10, "temp_max": 38, "rain": 8, "wind": 8},
        "description": "Calm waters, low wind"
    },
    "Camping ⛺": {
        "icon": "⛺",
        "thresholds": {"temp_min": 5, "temp_max": 35, "rain": 5, "wind": 15},
        "description": "Dry, mild conditions"
    },
    "Sports/Running 🏃": {
        "icon": "🏃",
        "thresholds": {"temp_min": 8, "temp_max": 28, "rain": 2, "wind": 12},
        "description": "Cool, dry weather ideal"
    },
    "General Outdoor 🌳": {
        "icon": "🌳",
        "thresholds": {"temp_min": 10, "temp_max": 32, "rain": 3, "wind": 12},
        "description": "Comfortable conditions"
    }
}

# -----------------------------
# Core Functions
# -----------------------------
@st.cache_data(ttl=7200, show_spinner=False)
def fetch_historical_weather(lat, lon, target_month, target_day, years_back=15):
    """Fetch historical weather data"""
    all_data = []
    current_year = datetime.now().year
    start_year = max(1981, current_year - years_back)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    successful_years = 0
    
    for idx, year in enumerate(range(start_year, current_year)):
        try:
            status_text.text(f"📡 Fetching data: {year} ({idx+1}/{current_year-start_year})")
            
            try:
                center_date = datetime(year, target_month, target_day)
            except ValueError:
                if target_month == 2 and target_day == 29:
                    center_date = datetime(year, 2, 28)
                else:
                    continue
            
            start_date = center_date - timedelta(days=5)
            end_date = center_date + timedelta(days=5)
            
            start_str = start_date.strftime("%Y%m%d")
            end_str = end_date.strftime("%Y%m%d")
            
            url = (f"https://power.larc.nasa.gov/api/temporal/daily/point?"
                   f"parameters=T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,WS2M&"
                   f"community=RE&longitude={lon}&latitude={lat}&"
                   f"start={start_str}&end={end_str}&format=JSON")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if 'properties' not in data or 'parameter' not in data['properties']:
                continue
            
            parameters = data['properties']['parameter']
            
            for date_str in parameters['T2M'].keys():
                date_obj = datetime.strptime(date_str, "%Y%m%d")
                
                temp = parameters['T2M'][date_str]
                temp_max = parameters['T2M_MAX'][date_str]
                temp_min = parameters['T2M_MIN'][date_str]
                precip = parameters['PRECTOTCORR'][date_str]
                wind = parameters['WS2M'][date_str]
                
                if all(v not in [None, -999, -999.0] for v in [temp, temp_max, temp_min, precip, wind]):
                    all_data.append({
                        'year': year,
                        'date': date_obj,
                        'month': date_obj.month,
                        'day': date_obj.day,
                        'temperature': float(temp),
                        'temp_max': float(temp_max),
                        'temp_min': float(temp_min),
                        'precipitation': float(precip),
                        'wind_speed': float(wind)
                    })
            
            successful_years += 1
            progress_bar.progress((idx + 1) / (current_year - start_year))
            
        except:
            pass
    
    progress_bar.empty()
    status_text.empty()
    
    if successful_years < 5:
        st.warning(f"⚠️ Only {successful_years} years of data retrieved. Results may be less reliable.")
    
    return pd.DataFrame(all_data)

def calculate_weather_risks(df, target_month, target_day, thresholds):
    """Calculate weather risk probabilities"""
    df_filtered = df[
        (df['month'] == target_month) & 
        (abs(df['day'] - target_day) <= 3)
    ].copy()
    
    if len(df_filtered) < 10:
        return None
    
    total_days = len(df_filtered)
    
    risks = {
        'too_cold': (df_filtered['temp_min'] < thresholds['temp_min']).sum() / total_days * 100,
        'too_hot': (df_filtered['temp_max'] > thresholds['temp_max']).sum() / total_days * 100,
        'rainy': (df_filtered['precipitation'] >= thresholds['rain']).sum() / total_days * 100,
        'windy': (df_filtered['wind_speed'] >= thresholds['wind']).sum() / total_days * 100
    }
    
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
        'years_analyzed': df_filtered['year'].nunique()
    }
    
    return risks, overall_risk, stats, df_filtered

def create_risk_gauge(overall_risk):
    """Create NASA-style mission risk gauge"""
    if overall_risk < 20:
        color, status, emoji = "#00ff64", "MISSION GO", "🚀"
    elif overall_risk < 40:
        color, status, emoji = "#00d4ff", "CONDITIONS NOMINAL", "✅"
    elif overall_risk < 60:
        color, status, emoji = "#ffa500", "CAUTION ADVISED", "⚠️"
    else:
        color, status, emoji = "#ff0080", "MISSION RISK", "❌"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=overall_risk,
        delta={'reference': 50, 'increasing': {'color': "#ff0080"}, 'decreasing': {'color': "#00ff64"}},
        title={'text': f"🛰️ {status}", 'font': {'size': 24, 'color': color, 'family': "Orbitron, monospace"}},
        number={'suffix': "%", 'font': {'size': 48, 'color': color, 'family': "Orbitron, monospace"}},
        gauge={
            'axis': {
                'range': [0, 100], 
                'tickwidth': 2, 
                'tickcolor': "#00d4ff",
                'tickfont': {'color': "#ffffff", 'family': "Orbitron, monospace"}
            },
            'bar': {'color': color, 'thickness': 0.8},
            'bgcolor': "rgba(0,0,0,0.3)",
            'borderwidth': 3,
            'bordercolor': "#00d4ff",
            'steps': [
                {'range': [0, 20], 'color': 'rgba(0, 255, 100, 0.3)'},
                {'range': [20, 40], 'color': 'rgba(0, 212, 255, 0.3)'},
                {'range': [40, 60], 'color': 'rgba(255, 165, 0, 0.3)'},
                {'range': [60, 100], 'color': 'rgba(255, 0, 128, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "#ff0080", 'width': 4},
                'thickness': 0.8,
                'value': 80
            }
        }
    ))
    
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=100, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'family': "Orbitron, monospace", 'color': "#ffffff"}
    )
    
    return fig

def create_risk_breakdown(risks):
    labels = ['❄️ COLD THREAT', '🔥 HEAT THREAT', '🌧️ PRECIP THREAT', '💨 WIND THREAT']
    values = [risks['too_cold'], risks['too_hot'], risks['rainy'], risks['windy']]
    colors = ['#00d4ff', '#ff0080', '#00ff64', '#ffa500']

    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        text=[f'{v:.1f}%' for v in values],
        textposition='outside',
        marker_color=colors,
        marker_line_color='#00d4ff',
        marker_line_width=2,
        opacity=0.9
    ))

    fig.update_layout(
        title={
            'text': '🛰️ MISSION THREAT ASSESSMENT', 
            'x': 0.5, 
            'xanchor': 'center', 
            'font': {'size': 24, 'color': '#00d4ff', 'family': "Orbitron, monospace"}
        },
        yaxis=dict(
            title='THREAT LEVEL (%)',
            tickfont={'color': '#ffffff', 'family': "Orbitron, monospace"},
            gridcolor='rgba(0, 212, 255, 0.3)',
            linecolor='#00d4ff',
            range=[0, max(max(values) * 1.3, 10)]
        ),
        xaxis=dict(
            tickfont={'color': '#ffffff', 'family': "Orbitron, monospace"},
            linecolor='#00d4ff'
        ),
        height=450,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': "Orbitron, monospace", 'color': "#ffffff"},
        margin=dict(t=80, b=60, l=60, r=20)
    )

    return fig
# -----------------------------
# Load logo as base64
# -----------------------------
with open("2.png", "rb") as f:
    logo_bytes = f.read()
logo_data_uri = f"data:image/png;base64,{base64.b64encode(logo_bytes).decode()}"

# -----------------------------
# Parade Guards Header (UI)
# -----------------------------
st.markdown(f"""
<style>
@keyframes blink {{
    0%, 50%, 100% {{ opacity: 1; }}
    25%, 75% {{ opacity: 0; }}
}}
</style>

<div style="background: linear-gradient(135deg, #0c1445 0%, #1a237e 50%, #0c1445 100%);
            border: 2px solid #00d4ff; border-radius: 15px; padding: 2rem;
            margin-bottom: 2rem; text-align: center; position: relative; overflow: hidden;
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);">

    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">

        <div style="width: 80px; height: 80px; margin-right: 20px;
                    background: linear-gradient(135deg, #00d4ff 0%, #2196f3 100%);
                    border-radius: 50%; display: flex; align-items: center;
                    justify-content: center; box-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
                    overflow: hidden;">
            <img src="{logo_data_uri}" style="width:70px; height:70px; object-fit:contain;">
        </div>

        <div>
            <div style="font-family: 'Orbitron', monospace; font-size: 3.5rem; font-weight: 900;
                        color: #00d4ff; text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff, 0 0 30px #00d4ff;
                        margin: 0; letter-spacing: 2px;">PARADE GUARDS</div>
            <div style="font-family: 'Exo 2', sans-serif; font-size: 1.3rem; color: #ffffff;
                        margin: 0.5rem 0 0 0; opacity: 0.9; letter-spacing: 1px;">
                WEATHER INTELLIGENCE SYSTEM
            </div>
        </div>
    </div>

    <div style="margin-top: 1rem; font-family: 'Orbitron', monospace; font-size: 1rem;">
        <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%;
                    margin-right: 8px; background: #00ff64; animation: blink 1s infinite;"></span>
        <span style="color: #00ff64;">SYSTEMS ONLINE</span>
        <span style="margin: 0 1rem; color: #ffa500;">|</span>
        <span style="color: #00d4ff;">NASA POWER API: CONNECTED</span>
        <span style="margin: 0 1rem; color: #ffa500;">|</span>
        <span style="color: #00d4ff;">WEATHER PROTECTION: ACTIVE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Mission Status Dashboard
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div style="font-family: 'Orbitron', monospace; font-size: 1.2rem; color: #00d4ff; margin-bottom: 0.5rem;">
            📡 DATA SOURCE
        </div>
        <div style="font-size: 1.5rem; font-weight: bold; color: #00ff64;">NASA POWER</div>
        <div style="font-size: 0.8rem; color: #ffffff;">Official API</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div style="font-family: 'Orbitron', monospace; font-size: 1.2rem; color: #00d4ff; margin-bottom: 0.5rem;">
            🌍 GLOBAL COVERAGE
        </div>
        <div style="font-size: 1.5rem; font-weight: bold; color: #00ff64;">WORLDWIDE</div>
        <div style="font-size: 0.8rem; color: #ffffff;">0.5° x 0.625° grid</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div style="font-family: 'Orbitron', monospace; font-size: 1.2rem; color: #00d4ff; margin-bottom: 0.5rem;">
            📅 DATA PERIOD
        </div>
        <div style="font-size: 1.5rem; font-weight: bold; color: #00ff64;">1981-2024</div>
        <div style="font-size: 0.8rem; color: #ffffff;">Historical archive</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <div style="font-family: 'Orbitron', monospace; font-size: 1.2rem; color: #00d4ff; margin-bottom: 0.5rem;">
            🛰️ SATELLITES
        </div>
        <div style="font-size: 1.5rem; font-weight: bold; color: #00ff64;">NASA+NOAA</div>
        <div style="font-size: 0.8rem; color: #ffffff;">Multi-satellite</div>
    </div>
    """, unsafe_allow_html=True)

# NASA POWER API Information
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(255, 0, 128, 0.1) 100%); border: 2px solid #00d4ff; border-radius: 15px; padding: 2rem; margin: 2rem 0; text-align: center;">
    <div style="font-family: 'Orbitron', monospace; font-size: 1.4rem; color: #00d4ff; margin-bottom: 1rem;">
        🌍 NASA POWER API INFORMATION
    </div>
    <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">
        <div style="text-align: center;">
            <div style="font-size: 1.2rem; color: #ffffff;">Data Resolution</div>
            <div style="font-family: 'Orbitron', monospace; color: #00ff64;">0.5° x 0.625°</div>
            <div style="font-size: 0.8rem; color: #ffffff;">Spatial grid</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 1.2rem; color: #ffffff;">Time Coverage</div>
            <div style="font-family: 'Orbitron', monospace; color: #00ff64;">1981-2024</div>
            <div style="font-size: 0.8rem; color: #ffffff;">Daily data</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 1.2rem; color: #ffffff;">Update Frequency</div>
            <div style="font-family: 'Orbitron', monospace; color: #00ff64;">Daily</div>
            <div style="font-size: 0.8rem; color: #ffffff;">New data added</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 1.2rem; color: #ffffff;">Data Sources</div>
            <div style="font-family: 'Orbitron', monospace; color: #00ff64;">NASA+NOAA</div>
            <div style="font-size: 0.8rem; color: #ffffff;">Satellites & models</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'activity' not in st.session_state:
    st.session_state.activity = "General Outdoor 🌳"

# Step 1: Location Selection
st.markdown("""
<div style="background: rgba(0, 0, 0, 0.7); border: 1px solid #00d4ff; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; backdrop-filter: blur(10px); box-shadow: 0 0 15px rgba(0, 212, 255, 0.2);">
    <div style="font-family: 'Orbitron', monospace; font-size: 1.4rem; color: #00d4ff; margin-bottom: 1rem; text-align: center; text-shadow: 0 0 10px #00d4ff;">🛡️ LOCATION PROTECTION ZONE</div>
    <div style="font-family: 'Exo 2', sans-serif; font-size: 1.1rem; color: #ffffff; text-align: center; margin-bottom: 2rem;">Select your location for weather protection analysis</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

with col1:
    st.markdown('<div style="font-family: \'Orbitron\', monospace; color: #00d4ff; margin-bottom: 0.5rem;">🌍 COUNTRY</div>', unsafe_allow_html=True)
    selected_country = st.selectbox(
        "Select Country:",
        list(LOCATIONS.keys()),
        label_visibility="collapsed"
    )

with col2:
    st.markdown('<div style="font-family: \'Orbitron\', monospace; color: #00d4ff; margin-bottom: 0.5rem;">🗺️ REGION</div>', unsafe_allow_html=True)
    provinces = list(LOCATIONS[selected_country].keys())
    selected_province = st.selectbox(
        "Select Province/State:",
        provinces,
        label_visibility="collapsed"
    )

with col3:
    st.markdown('<div style="font-family: \'Orbitron\', monospace; color: #00d4ff; margin-bottom: 0.5rem;">🏙️ CITY</div>', unsafe_allow_html=True)
    cities = list(LOCATIONS[selected_country][selected_province].keys())
    selected_city = st.selectbox(
        "Select City:",
        cities + ["🛰️ Custom Coordinates"],
        label_visibility="collapsed"
    )

if selected_city == "🛰️ Custom Coordinates":
    with col4:
        st.markdown('<div style="font-family: \'Orbitron\', monospace; color: #00d4ff; margin-bottom: 0.5rem;">⚙️ SET</div>', unsafe_allow_html=True)
        if st.button("🛰️ SET", use_container_width=True):
            st.session_state.show_custom = True
    
    if 'show_custom' in st.session_state and st.session_state.show_custom:
        st.markdown("""
        <div style="background: rgba(0, 0, 0, 0.5); border: 1px solid #00d4ff; border-radius: 10px; padding: 1rem; margin: 1rem 0;">
            <div style="font-family: 'Orbitron', monospace; color: #00d4ff; text-align: center; margin-bottom: 1rem;">
                🛰️ CUSTOM COORDINATES
            </div>
        """, unsafe_allow_html=True)
        col_lat, col_lon = st.columns(2)
        with col_lat:
            latitude = st.number_input("Latitude", value=40.7128, format="%.4f", min_value=-90.0, max_value=90.0)
        with col_lon:
            longitude = st.number_input("Longitude", value=-74.0060, format="%.4f", min_value=-180.0, max_value=180.0)
        st.markdown("</div>", unsafe_allow_html=True)
        location_name = f"🛰️ {latitude:.3f}°, {longitude:.3f}°"
else:
    latitude, longitude = LOCATIONS[selected_country][selected_province][selected_city]
    location_name = f"{selected_city}, {selected_province}, {selected_country}"

st.markdown(f"""
<div style="background: rgba(0, 212, 255, 0.1); border: 2px solid #00d4ff; border-radius: 10px; padding: 1rem; margin: 1rem 0; text-align: center;">
    <div style="font-family: 'Orbitron', monospace; color: #00d4ff; font-size: 1.2rem; margin-bottom: 0.5rem;">
        🛡️ PROTECTION ZONE SECURED
    </div>
    <div style="font-family: 'Exo 2', sans-serif; color: #ffffff; font-size: 1.1rem;">
        {location_name}
    </div>
    <div style="font-family: 'Orbitron', monospace; color: #00ff64; font-size: 0.9rem; margin-top: 0.5rem;">
        LAT: {latitude:.4f}° | LON: {longitude:.4f}°
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Step 2: Event Timeline
st.markdown("""
<div style="background: rgba(0, 0, 0, 0.7); border: 1px solid #00d4ff; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; backdrop-filter: blur(10px); box-shadow: 0 0 15px rgba(0, 212, 255, 0.2);">
    <div style="font-family: 'Orbitron', monospace; font-size: 1.4rem; color: #00d4ff; margin-bottom: 1rem; text-align: center; text-shadow: 0 0 10px #00d4ff;">📅 EVENT PROTECTION TIMELINE</div>
    <div style="font-family: 'Exo 2', sans-serif; font-size: 1.1rem; color: #ffffff; text-align: center; margin-bottom: 2rem;">Configure your event date for weather protection analysis</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div style="font-family: \'Orbitron\', monospace; color: #00d4ff; margin-bottom: 0.5rem;">🗓️ EVENT DATE</div>', unsafe_allow_html=True)
    min_date = datetime.now()
    max_date = datetime.now() + timedelta(days=365)
    
    target_date = st.date_input(
        "Pick your date:",
        value=datetime.now() + timedelta(days=30),
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed"
    )

with col2:
    st.markdown("""
    <div style="background: rgba(0, 0, 0, 0.5); border: 1px solid #00d4ff; border-radius: 10px; padding: 1rem; margin-top: 2rem;">
        <div style="font-family: 'Orbitron', monospace; color: #00d4ff; text-align: center; margin-bottom: 0.5rem;">
            📡 EVENT STATUS
        </div>
        <div style="font-family: 'Exo 2', sans-serif; color: #ffffff; text-align: center;">
            <div style="font-size: 1.1rem; margin-bottom: 0.3rem;">{}</div>
            <div style="font-size: 1.3rem; color: #00ff64; font-weight: bold;">{}</div>
        </div>
    </div>
    """.format(target_date.strftime('%B %d, %Y'), target_date.strftime('%A')), unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Step 3: Activity Profile Selection
st.markdown("""
<div style="background: rgba(0, 0, 0, 0.7); border: 1px solid #00d4ff; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; backdrop-filter: blur(10px); box-shadow: 0 0 15px rgba(0, 212, 255, 0.2);">
    <div style="font-family: 'Orbitron', monospace; font-size: 1.4rem; color: #00d4ff; margin-bottom: 1rem; text-align: center; text-shadow: 0 0 10px #00d4ff;">🛡️ ACTIVITY PROTECTION PROFILE</div>
    <div style="font-family: 'Exo 2', sans-serif; font-size: 1.1rem; color: #ffffff; text-align: center; margin-bottom: 2rem;">Choose your activity profile for specialized weather protection analysis</div>
""", unsafe_allow_html=True)

# Create activity buttons in a grid layout
activities = list(ACTIVITY_PROFILES.keys())

# Create 2 rows of 4 columns each for better layout
for row in range(2):
    cols = st.columns(4)
    for col_idx in range(4):
        activity_idx = row * 4 + col_idx
        if activity_idx < len(activities):
            activity = activities[activity_idx]
            with cols[col_idx]:
                if st.button(
                    f"{ACTIVITY_PROFILES[activity]['icon']}\n**{activity.replace(' ' + ACTIVITY_PROFILES[activity]['icon'], '')}**",
                    key=f"activity_{activity_idx}",
                    use_container_width=True
                ):
                    st.session_state.activity = activity

# After the loops, you can safely access the selected activity
selected_activity = st.session_state.activity
activity_info = ACTIVITY_PROFILES[selected_activity]


st.markdown(f"""
<div style="background: rgba(0, 212, 255, 0.1); border: 2px solid #00d4ff; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; text-align: center;">
    <div style="font-family: 'Orbitron', monospace; color: #00d4ff; font-size: 1.3rem; margin-bottom: 1rem;">
        🛡️ PROTECTION PROFILE: {selected_activity}
    </div>
    <div style="font-family: 'Exo 2', sans-serif; color: #ffffff; font-size: 1.1rem; font-style: italic;">
        {activity_info['description']}
    </div>
    <div style="margin-top: 1rem; font-family: 'Orbitron', monospace; color: #00ff64; font-size: 0.9rem;">
        PROTECTION PARAMETERS LOADED
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Protection Analysis Button
st.markdown("""
<div style="text-align: center; margin: 3rem 0;">
    <div style="font-family: 'Orbitron', monospace; color: #00d4ff; font-size: 1.2rem; margin-bottom: 1rem;">
        🛡️ READY FOR PROTECTION ANALYSIS
    </div>
    <div style="font-family: 'Exo 2', sans-serif; color: #ffffff; margin-bottom: 2rem;">
        All systems are go. Initiate weather protection analysis?
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("🛡️ **LAUNCH PROTECTION ANALYSIS**", type="primary", use_container_width=True):
    
    with st.spinner(f"🛡️ Analyzing 15 years of weather data for {location_name}..."):
        df = fetch_historical_weather(latitude, longitude, target_date.month, target_date.day, years_back=15)
    
    if df.empty:
        st.error("❌ Unable to retrieve weather data. Please try a different location or check your internet connection.")
    else:
        result = calculate_weather_risks(df, target_date.month, target_date.day, activity_info['thresholds'])
        
        if result is None:
            st.error("❌ Insufficient historical data for this date. Try a different date.")
        else:
            risks, overall_risk, stats, df_filtered = result
            
            st.markdown(f"""
            <div style="background: rgba(0, 255, 100, 0.1); border: 2px solid #00ff64; border-radius: 15px; padding: 2rem; margin: 2rem 0; text-align: center;">
                <div style="font-family: 'Orbitron', monospace; color: #00ff64; font-size: 1.5rem; margin-bottom: 1rem;">
                    ✅ PROTECTION ANALYSIS COMPLETE
                </div>
                <div style="font-family: 'Exo 2', sans-serif; color: #ffffff; font-size: 1.2rem;">
                    Examined <span style="color: #00ff64; font-weight: bold;">{stats['years_analyzed']} years</span> of satellite data 
                    <span style="color: #00ff64; font-weight: bold;">({stats['total_days']} days)</span>
                </div>
                <div style="font-family: 'Orbitron', monospace; color: #00d4ff; font-size: 1rem; margin-top: 1rem;">
                    🛡️ NASA POWER API DATA PROCESSED SUCCESSFULLY
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style="background: rgba(0, 0, 0, 0.7); border: 1px solid #00d4ff; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; backdrop-filter: blur(10px); box-shadow: 0 0 15px rgba(0, 212, 255, 0.2);">
                <div style="font-family: 'Orbitron', monospace; font-size: 1.4rem; color: #00d4ff; margin-bottom: 1rem; text-align: center; text-shadow: 0 0 10px #00d4ff;">📊 WEATHER INTELLIGENCE ASSESSMENT</div>
                <div style="font-family: 'Exo 2', sans-serif; font-size: 1.1rem; color: #ffffff; text-align: center; margin-bottom: 2rem;">Protection-critical weather analysis and risk assessment</div>
            """, unsafe_allow_html=True)
            
            # Risk visualization
            col_gauge, col_breakdown = st.columns([1, 1.2])
            
            with col_gauge:
                st.plotly_chart(create_risk_gauge(overall_risk), use_container_width=True)
                
                # Recommendation
                if overall_risk < 25:
                    st.success(f"🎉 **Perfect!** Great weather conditions expected for your {selected_activity}!")
                elif overall_risk < 50:
                    st.info(f"👍 **Good Odds!** Weather is usually favorable, but have a backup plan ready.")
                elif overall_risk < 70:
                    st.warning(f"⚠️ **Moderate Risk** - Weather can be unpredictable. Monitor forecasts closer to your date.")
                else:
                    st.error(f"❌ **High Risk** - Historically, {int(overall_risk)}% of similar days had unfavorable conditions. Consider rescheduling.")
            
            with col_breakdown:
                st.plotly_chart(create_risk_breakdown(risks), use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Detailed Statistics
            st.markdown("### 📈 Historical Weather Patterns")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "🌡️ Typical High",
                    f"{stats['typical_high']:.1f}°C",
                    f"{stats['typical_high']*9/5+32:.0f}°F"
                )
                st.caption(f"Record: {stats['max_temp_ever']:.1f}°C")
            
            with col2:
                st.metric(
                    "❄️ Typical Low",
                    f"{stats['typical_low']:.1f}°C",
                    f"{stats['typical_low']*9/5+32:.0f}°F"
                )
                st.caption(f"Record: {stats['min_temp_ever']:.1f}°C")
            
            with col3:
                rain_pct = (stats['rainy_days'] / stats['total_days']) * 100
                st.metric(
                    "🌧️ Rain Chance",
                    f"{rain_pct:.0f}%",
                    f"{stats['rainy_days']} days"
                )
                st.caption(f"Avg: {stats['avg_precip']:.1f}mm")
            
            with col4:
                st.metric(
                    "💨 Wind Speed",
                    f"{stats['avg_wind']:.1f} m/s",
                    f"{stats['avg_wind']*2.237:.1f} mph"
                )
                st.caption(f"Max: {stats['max_wind_ever']:.1f} m/s")
            
            st.markdown("---")
            
            # What to Expect section
            st.markdown("### 💡 What to Expect")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**✅ Favorable Conditions:**")
                good_conditions = []
                if risks['too_cold'] < 20:
                    good_conditions.append("- Temperature will likely be comfortable")
                if risks['too_hot'] < 20:
                    good_conditions.append("- Low chance of excessive heat")
                if risks['rainy'] < 30:
                    good_conditions.append("- Generally dry weather expected")
                if risks['windy'] < 25:
                    good_conditions.append("- Calm to light winds typical")
                
                if good_conditions:
                    for cond in good_conditions:
                        st.markdown(cond)
                else:
                    st.markdown("- Weather conditions are highly variable")
            
            with col2:
                st.markdown("**⚠️ Watch Out For:**")
                concerns = []
                if risks['too_cold'] > 30:
                    concerns.append(f"- Cold temperatures ({risks['too_cold']:.0f}% chance)")
                if risks['too_hot'] > 30:
                    concerns.append(f"- Excessive heat ({risks['too_hot']:.0f}% chance)")
                if risks['rainy'] > 30:
                    concerns.append(f"- Rain possible ({risks['rainy']:.0f}% chance)")
                if risks['windy'] > 30:
                    concerns.append(f"- Strong winds ({risks['windy']:.0f}% chance)")
                
                if concerns:
                    for concern in concerns:
                        st.markdown(concern)
                else:
                    st.markdown("- No major weather concerns identified")
            
            st.markdown("---")
            
            # Download Section
            st.markdown("### 📥 Download Your Results")
            
            col_dl1, col_dl2 = st.columns(2)
            
            with col_dl1:
                # Summary report
                summary_data = pd.DataFrame({
                    'Country': [selected_country],
                    'Province_State': [selected_province],
                    'City': [selected_city if selected_city != "📍 Custom Coordinates" else "Custom"],
                    'Location_Name': [location_name],
                    'Latitude': [latitude],
                    'Longitude': [longitude],
                    'Target_Date': [target_date.strftime('%Y-%m-%d')],
                    'Day_of_Week': [target_date.strftime('%A')],
                    'Activity': [selected_activity],
                    'Overall_Risk_Percent': [round(overall_risk, 2)],
                    'Too_Cold_Percent': [round(risks['too_cold'], 2)],
                    'Too_Hot_Percent': [round(risks['too_hot'], 2)],
                    'Rainy_Percent': [round(risks['rainy'], 2)],
                    'Windy_Percent': [round(risks['windy'], 2)],
                    'Typical_High_C': [round(stats['typical_high'], 1)],
                    'Typical_Low_C': [round(stats['typical_low'], 1)],
                    'Avg_Precipitation_mm': [round(stats['avg_precip'], 2)],
                    'Avg_Wind_Speed_ms': [round(stats['avg_wind'], 1)],
                    'Years_Analyzed': [stats['years_analyzed']],
                    'Total_Days_Analyzed': [stats['total_days']],
                    'Data_Source': ['NASA POWER API'],
                    'Analysis_Date': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                })
                
                csv_summary = summary_data.to_csv(index=False)
                st.download_button(
                    label="📊 Download Summary Report (CSV)",
                    data=csv_summary,
                    file_name=f"weather_risk_report_{target_date.strftime('%Y%m%d')}_{selected_city.replace(' ', '_')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col_dl2:
                # Historical data
                df_download = df_filtered[['date', 'year', 'temperature', 'temp_max', 'temp_min', 'precipitation', 'wind_speed']].copy()
                df_download['date'] = df_download['date'].dt.strftime('%Y-%m-%d')
                
                csv_raw = df_download.to_csv(index=False)
                st.download_button(
                    label="📁 Download Historical Data (CSV)",
                    data=csv_raw,
                    file_name=f"historical_weather_data_{target_date.strftime('%Y%m%d')}_{selected_city.replace(' ', '_')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

# Real NASA Data Information
st.markdown("""
<div style="background: rgba(0, 0, 0, 0.7); border: 1px solid #00d4ff; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; backdrop-filter: blur(10px); box-shadow: 0 0 15px rgba(0, 212, 255, 0.2);">
    <div style="font-family: 'Orbitron', monospace; font-size: 1.4rem; color: #00d4ff; margin-bottom: 1rem; text-align: center; text-shadow: 0 0 10px #00d4ff;">📊 REAL NASA WEATHER DATA</div>
    <div style="font-family: 'Exo 2', sans-serif; font-size: 1.1rem; color: #ffffff; text-align: center; margin-bottom: 2rem;">Historical weather analysis using authentic NASA POWER API data</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div style="font-family: 'Orbitron', monospace; font-size: 1.1rem; color: #00d4ff; margin-bottom: 0.5rem;">
            🌡️ TEMPERATURE
        </div>
        <div style="font-size: 1.5rem; font-weight: bold; color: #00ff64;">T2M</div>
        <div style="font-size: 0.8rem; color: #ffffff;">Mean daily temp</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div style="font-family: 'Orbitron', monospace; font-size: 1.1rem; color: #00d4ff; margin-bottom: 0.5rem;">
            🌧️ PRECIPITATION
        </div>
        <div style="font-size: 1.5rem; font-weight: bold; color: #00ff64;">PRECTOT</div>
        <div style="font-size: 0.8rem; color: #ffffff;">Daily rainfall</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div style="font-family: 'Orbitron', monospace; font-size: 1.1rem; color: #00d4ff; margin-bottom: 0.5rem;">
            💨 WIND SPEED
        </div>
        <div style="font-size: 1.5rem; font-weight: bold; color: #00ff64;">WS2M</div>
        <div style="font-size: 0.8rem; color: #ffffff;">2m wind speed</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <div style="font-family: 'Orbitron', monospace; font-size: 1.1rem; color: #00d4ff; margin-bottom: 0.5rem;">
            📈 DATA QUALITY
        </div>
        <div style="font-size: 1.5rem; font-weight: bold; color: #00ff64;">VALIDATED</div>
        <div style="font-size: 0.8rem; color: #ffffff;">NASA quality control</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Parade Guards Footer
st.markdown("""
<div style="background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 100%); border: 2px solid #00d4ff; border-radius: 15px; padding: 3rem 2rem; margin: 3rem 0; text-align: center;">
    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
        <div style="width: 60px; height: 60px; margin-right: 20px; background: linear-gradient(135deg, #00d4ff 0%, #2196f3 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px rgba(0, 212, 255, 0.5);">
            <div style="font-size: 2rem;">🛡️</div>
        </div>
        <div>
            <div style="font-family: 'Orbitron', monospace; color: #00d4ff; font-size: 2rem; font-weight: 900; margin-bottom: 0.5rem;">
                PARADE GUARDS
            </div>
            <div style="font-family: 'Exo 2', sans-serif; color: #ffffff; font-size: 1.3rem;">
                WEATHER INTELLIGENCE SYSTEM
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer content in columns
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background: rgba(0, 0, 0, 0.5); border: 1px solid #00d4ff; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; text-align: center;">
        <div style="font-family: 'Orbitron', monospace; color: #00d4ff; font-size: 1.1rem; margin-bottom: 0.5rem;">
            📡 DATA SOURCE
        </div>
        <div style="font-family: 'Exo 2', sans-serif; color: #ffffff;">
            NASA POWER API<br>
            Prediction Of Worldwide<br>
            Energy Resources
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: rgba(0, 0, 0, 0.5); border: 1px solid #00d4ff; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; text-align: center;">
        <div style="font-family: 'Orbitron', monospace; color: #00d4ff; font-size: 1.1rem; margin-bottom: 0.5rem;">
            🛰️ COVERAGE
        </div>
        <div style="font-family: 'Exo 2', sans-serif; color: #ffffff;">
            Global Coverage<br>
            0.5° x 0.625° Grid<br>
            1981-2024 Archive
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: rgba(0, 0, 0, 0.5); border: 1px solid #00d4ff; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; text-align: center;">
        <div style="font-family: 'Orbitron', monospace; color: #00d4ff; font-size: 1.1rem; margin-bottom: 0.5rem;">
            📊 DATA PARAMETERS
        </div>
        <div style="font-family: 'Exo 2', sans-serif; color: #ffffff;">
            T2M, T2M_MAX, T2M_MIN<br>
            PRECTOTCORR, WS2M<br>
            Daily Observations
        </div>
    </div>
    """, unsafe_allow_html=True)

# Challenge info
st.markdown("""
<div style="background: rgba(0, 0, 0, 0.7); border: 1px solid #00d4ff; border-radius: 15px; padding: 2rem; margin: 2rem 0; text-align: center;">
    <div style="font-family: 'Orbitron', monospace; color: #00ff64; font-size: 1.2rem; margin-bottom: 1rem;">
        🌟 NASA SPACE APPS CHALLENGE 2025
    </div>
    <div style="font-family: 'Exo 2', sans-serif; color: #ffffff; font-size: 1.1rem; margin-bottom: 1rem;">
        Challenge: "Will It Rain On My Parade?"
    </div>
    <div style="font-family: 'Exo 2', sans-serif; color: #ffffff; font-size: 0.9rem; opacity: 0.8;">
        Built with ❤️ using Streamlit • Powered by NASA Earth Science Data<br>
        Temperature: °C | Precipitation: mm | Wind: m/s
    </div>
    <div style="margin-top: 1.5rem; font-family: 'Orbitron', monospace; color: #00d4ff; font-size: 0.9rem;">
        <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; background: #00ff64; animation: blink 1s infinite;"></span>
        <span style="color: #00ff64;">NASA POWER API: CONNECTED</span>
        <span style="margin: 0 1rem; color: #ffa500;">|</span>
        <span style="color: #00d4ff;">PROTECTION ANALYSIS: ACTIVE</span>
        <span style="margin: 0 1rem; color: #ffa500;">|</span>
        <span style="color: #00d4ff;">PARADE GUARDS: OPERATIONAL</span>
    </div>
</div>
""", unsafe_allow_html=True)