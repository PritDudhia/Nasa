import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import numpy as np
import os

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
LOCATIONS = {
    "🇨🇦 Canada": {
        "Ontario": {
            "Toronto": (43.6532, -79.3832),
            "Ottawa": (45.4215, -75.6972),
            "Windsor": (42.3149, -83.0364),
            "Hamilton": (43.2557, -79.8711),
            "London": (42.9849, -81.2453)
        },
        "Quebec": {
            "Montreal": (45.5017, -73.5673),
            "Quebec City": (46.8139, -71.2080),
            "Laval": (45.6066, -73.7124)
        },
        "British Columbia": {
            "Vancouver": (49.2827, -123.1207),
            "Victoria": (48.4284, -123.3656)
        },
        "Alberta": {
            "Calgary": (51.0447, -114.0719),
            "Edmonton": (53.5461, -113.4938)
        }
    },
    "🇺🇸 United States": {
        "California": {
            "Los Angeles": (34.0522, -118.2437),
            "San Francisco": (37.7749, -122.4194),
            "San Diego": (32.7157, -117.1611)
        },
        "Texas": {
            "Houston": (29.7604, -95.3698),
            "Dallas": (32.7767, -96.7970),
            "Austin": (30.2672, -97.7431)
        },
        "Florida": {
            "Miami": (25.7617, -80.1918),
            "Orlando": (28.5383, -81.3792)
        },
        "New York": {
            "New York City": (40.7128, -74.0060),
            "Buffalo": (42.8864, -78.8784)
        }
    },
    "🇬🇧 United Kingdom": {
        "England": {
            "London": (51.5074, -0.1278),
            "Manchester": (53.4808, -2.2426)
        },
        "Scotland": {
            "Edinburgh": (55.9533, -3.1883),
            "Glasgow": (55.8642, -4.2518)
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
def fetch_historical_weather(lat, lon, target_month, target_day, years_back=15):
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
            
            url = (f"https://power.larc.nasa.gov/api/temporal/daily/point?"
                   f"parameters=T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,WS2M&"
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
                temp = parameters['T2M'][date_str]
                temp_max = parameters['T2M_MAX'][date_str]
                temp_min = parameters['T2M_MIN'][date_str]
                precip = parameters['PRECTOTCORR'][date_str]
                wind = parameters['WS2M'][date_str]
                
                if all(v not in [None, -999, -999.0] for v in [temp, temp_max, temp_min, precip, wind]):
                    all_data.append({
                        'year': year, 'date': date_obj, 'month': date_obj.month, 'day': date_obj.day,
                        'temperature': float(temp), 'temp_max': float(temp_max), 'temp_min': float(temp_min),
                        'precipitation': float(precip), 'wind_speed': float(wind)
                    })
            
            successful_years += 1
            progress_bar.progress((idx + 1) / (current_year - start_year))
        except:
            pass
    
    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(all_data)

def calculate_weather_risks(df, target_month, target_day, thresholds):
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
    if overall_risk < 20:
        color, status = "#00ff64", "MISSION GO 🚀"
    elif overall_risk < 40:
        color, status = "#00d4ff", "NOMINAL ✅"
    elif overall_risk < 60:
        color, status = "#ffa500", "CAUTION ⚠️"
    else:
        color, status = "#ff0080", "HIGH RISK ❌"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_risk,
        title={'text': f"🛰️ {status}", 'font': {'size': 24, 'color': color, 'family': "Orbitron"}},
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
    
    fig.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)", font={'color': "#ffffff"})
    return fig

def create_risk_breakdown(risks):
    labels = ['❄️ COLD', '🔥 HEAT', '🌧️ RAIN', '💨 WIND']
    values = [risks['too_cold'], risks['too_hot'], risks['rainy'], risks['windy']]
    
    fig = go.Figure(go.Bar(
        x=labels, y=values,
        text=[f'{v:.1f}%' for v in values],
        textposition='outside',
        marker_color=['#00d4ff', '#ff0080', '#00ff64', '#ffa500']
    ))
    
    fig.update_layout(
        title={'text': '🛰️ THREAT ASSESSMENT', 'font': {'color': '#00d4ff', 'family': "Orbitron"}},
        yaxis={'gridcolor': 'rgba(0, 212, 255, 0.2)'},
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "#ffffff"}
    )
    return fig

# -----------------------------
# Header
# -----------------------------
st.markdown("""
<div style="background: linear-gradient(135deg, #0c1445 0%, #1a237e 50%, #0c1445 100%);
            border: 2px solid #00d4ff; border-radius: 15px; padding: 2rem;
            margin-bottom: 2rem; text-align: center; box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);">
    <div style="font-family: 'Orbitron', monospace; font-size: 3.5rem; font-weight: 900;
                color: #00d4ff; text-shadow: 0 0 20px #00d4ff; margin: 0;">
        🛡️ PARADE GUARDS
    </div>
    <div style="font-family: 'Exo 2', sans-serif; font-size: 1.3rem; color: #ffffff; margin-top: 0.5rem;">
        WEATHER INTELLIGENCE SYSTEM
    </div>
    <div style="margin-top: 1rem; font-family: 'Orbitron', monospace;">
        <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%;
                    background: #00ff64; animation: blink 1s infinite;"></span>
        <span style="color: #00ff64;"> SYSTEMS ONLINE</span>
        <span style="margin: 0 1rem; color: #ffa500;">|</span>
        <span style="color: #00d4ff;">NASA POWER API: CONNECTED</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Mission Status
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div style="font-family: 'Orbitron', monospace; color: #00d4ff;">📡 DATA SOURCE</div>
        <div style="font-size: 1.5rem; font-weight: bold; color: #00ff64;">NASA POWER</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div style="font-family: 'Orbitron', monospace; color: #00d4ff;">🌍 COVERAGE</div>
        <div style="font-size: 1.5rem; font-weight: bold; color: #00ff64;">GLOBAL</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div style="font-family: 'Orbitron', monospace; color: #00d4ff;">📅 ARCHIVE</div>
        <div style="font-size: 1.5rem; font-weight: bold; color: #00ff64;">1981-2024</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <div style="font-family: 'Orbitron', monospace; color: #00d4ff;">🛰️ SATELLITES</div>
        <div style="font-size: 1.5rem; font-weight: bold; color: #00ff64;">MULTI</div>
    </div>
    """, unsafe_allow_html=True)

# Initialize session state
if 'activity' not in st.session_state:
    st.session_state.activity = "General Outdoor 🌳"

# Location Selection
st.markdown('<div class="mission-panel"><div class="panel-title">🛡️ LOCATION PROTECTION ZONE</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    selected_country = st.selectbox("🌍 COUNTRY", list(LOCATIONS.keys()))

with col2:
    provinces = list(LOCATIONS[selected_country].keys())
    selected_province = st.selectbox("🗺️ REGION", provinces)

with col3:
    cities = list(LOCATIONS[selected_country][selected_province].keys())
    selected_city = st.selectbox("🏙️ CITY", cities + ["🛰️ Custom"])

if selected_city == "🛰️ Custom":
    col_lat, col_lon = st.columns(2)
    with col_lat:
        latitude = st.number_input("Latitude", value=40.7128, format="%.4f")
    with col_lon:
        longitude = st.number_input("Longitude", value=-74.0060, format="%.4f")
    location_name = f"{latitude:.3f}°, {longitude:.3f}°"
else:
    latitude, longitude = LOCATIONS[selected_country][selected_province][selected_city]
    location_name = f"{selected_city}, {selected_province}"

st.info(f"**📍 SECURED:** {location_name} | LAT: {latitude:.4f}° LON: {longitude:.4f}°")
st.markdown('</div>', unsafe_allow_html=True)

# Date Selection
st.markdown('<div class="mission-panel"><div class="panel-title">📅 EVENT TIMELINE</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    target_date = st.date_input(
        "🗓️ EVENT DATE",
        value=datetime.now() + timedelta(days=30),
        min_value=datetime.now(),
        max_value=datetime.now() + timedelta(days=365)
    )

with col2:
    st.info(f"**{target_date.strftime('%B %d, %Y')}**\n{target_date.strftime('%A')}")

st.markdown('</div>', unsafe_allow_html=True)

# Activity Selection
st.markdown('<div class="mission-panel"><div class="panel-title">🛡️ ACTIVITY PROFILE</div>', unsafe_allow_html=True)

cols = st.columns(len(ACTIVITY_PROFILES))
for idx, (activity, profile) in enumerate(ACTIVITY_PROFILES.items()):
    with cols[idx]:
        if st.button(f"{profile['icon']}\n{activity.split()[0]}", key=f"act_{idx}", use_container_width=True):
            st.session_state.activity = activity

selected_activity = st.session_state.activity
st.success(f"**ACTIVE:** {selected_activity} - {ACTIVITY_PROFILES[selected_activity]['description']}")
st.markdown('</div>', unsafe_allow_html=True)

# Launch Button
if st.button("🛡️ **LAUNCH PROTECTION ANALYSIS**", type="primary", use_container_width=True):
    
    with st.spinner(f"🛰️ Analyzing 15 years of data for {location_name}..."):
        df = fetch_historical_weather(latitude, longitude, target_date.month, target_date.day)
    
    if df.empty:
        st.error("❌ DATA UNAVAILABLE")
    else:
        result = calculate_weather_risks(df, target_date.month, target_date.day, ACTIVITY_PROFILES[selected_activity]['thresholds'])
        
        if result is None:
            st.error("❌ INSUFFICIENT DATA")
        else:
            risks, overall_risk, stats, df_filtered = result
            
            st.success(f"✅ ANALYSIS COMPLETE: {stats['years_analyzed']} years ({stats['total_days']} days)")
            
            st.markdown('<div class="mission-panel"><div class="panel-title">📊 INTELLIGENCE ASSESSMENT</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1.2])
            
            with col1:
                st.plotly_chart(create_risk_gauge(overall_risk), use_container_width=True)
            
            with col2:
                st.plotly_chart(create_risk_breakdown(risks), use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Stats
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🌡️ High", f"{stats['typical_high']:.1f}°C", f"{stats['max_temp_ever']:.1f}°C max")
            with col2:
                st.metric("❄️ Low", f"{stats['typical_low']:.1f}°C", f"{stats['min_temp_ever']:.1f}°C min")
            with col3:
                st.metric("🌧️ Rain", f"{(stats['rainy_days']/stats['total_days'])*100:.0f}%", f"{stats['rainy_days']} days")
            with col4:
                st.metric("💨 Wind", f"{stats['avg_wind']:.1f} m/s", f"{stats['max_wind_ever']:.1f} max")
            
            # Downloads
            st.markdown("---")
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
                
                st.download_button("📊 SUMMARY", summary.to_csv(index=False), 
                                 f"summary_{target_date.strftime('%Y%m%d')}.csv", use_container_width=True)
            
            with col2:
                st.download_button("📁 RAW DATA", df_filtered.to_csv(index=False),
                                 f"data_{target_date.strftime('%Y%m%d')}.csv", use_container_width=True)

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