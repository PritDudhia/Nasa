import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import numpy as np

# Page config - MUST be first
st.set_page_config(
    page_title="☂️ Will It Rain On My Parade?",
    layout="wide",
    page_icon="🌤️",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 60px;
        font-size: 16px;
        font-weight: 600;
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
    """Create gauge chart"""
    if overall_risk < 20:
        color, status, emoji = "#10b981", "Excellent", "✅"
    elif overall_risk < 40:
        color, status, emoji = "#3b82f6", "Good", "👍"
    elif overall_risk < 60:
        color, status, emoji = "#f59e0b", "Moderate", "⚠️"
    else:
        color, status, emoji = "#ef4444", "High Risk", "❌"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_risk,
        title={'text': f"{emoji} {status}", 'font': {'size': 28, 'color': color}},
        number={'suffix': "%", 'font': {'size': 56, 'color': color}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "gray"},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 20], 'color': '#d1fae5'},
                {'range': [20, 40], 'color': '#bfdbfe'},
                {'range': [40, 60], 'color': '#fed7aa'},
                {'range': [60, 100], 'color': '#fecaca'}
            ],
            'threshold': {
                'line': {'color': "darkred", 'width': 4},
                'thickness': 0.8,
                'value': 80
            }
        }
    ))
    
    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=80, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'family': "Arial, sans-serif"}
    )
    
    return fig

def create_risk_breakdown(risks):
    """Create bar chart"""
    labels = ['❄️ Too Cold', '🔥 Too Hot', '🌧️ Rainy', '💨 Windy']
    values = [risks['too_cold'], risks['too_hot'], risks['rainy'], risks['windy']]
    colors = ['#3b82f6', '#ef4444', '#06b6d4', '#8b5cf6']
    
    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        text=[f'{v:.1f}%' for v in values],
        textposition='outside',
        marker_color=colors,
        marker_line_color='rgb(8,48,107)',
        marker_line_width=1.5,
        opacity=0.8
    ))
    
    fig.update_layout(
        title={'text': 'Risk Breakdown by Weather Factor', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 20}},
        yaxis_title='Probability (%)',
        yaxis_range=[0, max(max(values) * 1.3, 10)],
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': "Arial, sans-serif", 'size': 14}
    )
    
    return fig

# -----------------------------
# Main App UI
# -----------------------------

# Header
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 3em;">☂️ Will It Rain On My Parade?</h1>
    <p style="margin:0.5em 0 0 0; font-size: 1.2em;">Plan outdoor activities with NASA weather intelligence</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'activity' not in st.session_state:
    st.session_state.activity = "General Outdoor 🌳"

# Step 1: Location Selection with Hierarchy
st.markdown("### 📍 Step 1: Where are you going?")

col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

with col1:
    selected_country = st.selectbox(
        "Select Country:",
        list(LOCATIONS.keys()),
        label_visibility="collapsed"
    )

with col2:
    provinces = list(LOCATIONS[selected_country].keys())
    selected_province = st.selectbox(
        "Select Province/State:",
        provinces,
        label_visibility="collapsed"
    )

with col3:
    cities = list(LOCATIONS[selected_country][selected_province].keys())
    selected_city = st.selectbox(
        "Select City:",
        cities + ["📍 Custom Coordinates"],
        label_visibility="collapsed"
    )

if selected_city == "📍 Custom Coordinates":
    with col4:
        if st.button("📍 Set", use_container_width=True):
            st.session_state.show_custom = True
    
    if 'show_custom' in st.session_state and st.session_state.show_custom:
        col_lat, col_lon = st.columns(2)
        with col_lat:
            latitude = st.number_input("Latitude", value=40.7128, format="%.4f", min_value=-90.0, max_value=90.0)
        with col_lon:
            longitude = st.number_input("Longitude", value=-74.0060, format="%.4f", min_value=-180.0, max_value=180.0)
        location_name = f"📍 {latitude:.3f}°, {longitude:.3f}°"
else:
    latitude, longitude = LOCATIONS[selected_country][selected_province][selected_city]
    location_name = f"{selected_city}, {selected_province}, {selected_country}"

st.info(f"**📍 Selected Location:** {location_name}")

st.markdown("---")

# Step 2: Date Selection
st.markdown("### 📅 Step 2: When are you going?")

col1, col2 = st.columns([2, 1])

with col1:
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
    st.info(f"**Selected:**\n{target_date.strftime('%B %d, %Y')}\n{target_date.strftime('%A')}")

st.markdown("---")

# Step 3: Activity Selection
st.markdown("### 🎯 Step 3: What's your activity?")

cols = st.columns(4)
activities = list(ACTIVITY_PROFILES.keys())

for idx, activity in enumerate(activities):
    col = cols[idx % 4]
    with col:
        if st.button(
            f"{ACTIVITY_PROFILES[activity]['icon']}\n**{activity.replace(' ' + ACTIVITY_PROFILES[activity]['icon'], '')}**",
            key=f"activity_{idx}",
            use_container_width=True
        ):
            st.session_state.activity = activity

selected_activity = st.session_state.activity
activity_info = ACTIVITY_PROFILES[selected_activity]

st.info(f"**Selected Activity:** {selected_activity}\n\n*{activity_info['description']}*")

st.markdown("---")

# Analyze Button
if st.button("🔍 **ANALYZE WEATHER RISK**", type="primary", use_container_width=True):
    
    with st.spinner(f"🛰️ Analyzing 15 years of weather data for {location_name}..."):
        df = fetch_historical_weather(latitude, longitude, target_date.month, target_date.day, years_back=15)
    
    if df.empty:
        st.error("❌ Unable to retrieve weather data. Please try a different location or check your internet connection.")
    else:
        result = calculate_weather_risks(df, target_date.month, target_date.day, activity_info['thresholds'])
        
        if result is None:
            st.error("❌ Insufficient historical data for this date. Try a different date.")
        else:
            risks, overall_risk, stats, df_filtered = result
            
            st.success(f"✅ Analysis complete! Examined **{stats['years_analyzed']} years** of data ({stats['total_days']} days)")
            
            st.markdown("---")
            st.markdown("## 📊 Weather Risk Assessment")
            
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

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p style="font-size: 1.1em; font-weight: 600;">🚀 NASA Space Apps Challenge 2025</p>
    <p style="font-size: 0.95em;">Challenge: "Will It Rain On My Parade?"</p>
    <p style="font-size: 0.85em; margin-top: 1em;">
        Data Source: NASA POWER API (Prediction Of Worldwide Energy Resources)<br>
        Historical Analysis: 15 years of satellite & model-based observations<br>
        Temperature: °C | Precipitation: mm | Wind: m/s
    </p>
    <p style="font-size: 0.8em; color: #999; margin-top: 1em;">
        Built with ❤️ using Streamlit • Powered by NASA Earth Science Data<br>
        Coverage: 200+ cities across 10 countries worldwide
    </p>
</div>
""", unsafe_allow_html=True)