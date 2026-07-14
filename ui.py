import streamlit as st
import requests
import uuid
import sys
import re
import sqlite3
import os

# Configure page layout and style
st.set_page_config(
    page_title="AeroPlan AI - Travel Assistant",
    page_icon=":material/travel_explore:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper function to load custom CSS
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
            st.html(f"<style>{css}</style>")

# Inject custom CSS
load_css()

# Backend state fetcher
def load_session_state(thread_id):
    url = f"http://127.0.0.1:8000/travel/state/{thread_id}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return {}

# Query recent threads from DB
def get_recent_threads():
    try:
        conn = sqlite3.connect("travel_planner_checkpoints.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
        threads = [r[0] for r in cursor.fetchall() if r[0]]
        conn.close()
        # Filter out testing names for a cleaner look
        return [t for t in threads if not t.startswith("test_")]
    except Exception:
        return []

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = f"traveler_{uuid.uuid4().hex[:6]}"
if "agent_status" not in st.session_state:
    st.session_state.agent_status = None
if "loaded_state" not in st.session_state:
    st.session_state.loaded_state = {}

# Load current thread's state on first load or session switch
if "loaded_session_id" not in st.session_state or st.session_state.loaded_session_id != st.session_state.session_id:
    db_state = load_session_state(st.session_state.session_id)
    st.session_state.loaded_state = db_state
    st.session_state.loaded_session_id = st.session_state.session_id
    
    # Restore messages from db if itinerary exists
    if db_state and db_state.get("itinerary") and db_state.get("user_query"):
        st.session_state.messages = [
            {"role": "user", "content": db_state.get("user_query")},
            {"role": "assistant", "content": db_state.get("itinerary")}
        ]
        st.session_state.agent_status = "completed"
    else:
        st.session_state.messages = []
        st.session_state.agent_status = None

# Custom Header Render
def render_header():
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 0; margin-bottom: 25px; border-bottom: 1px solid var(--border-color);">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);">
                <span style="font-size: 22px; color: white;">✈️</span>
            </div>
            <div>
                <h2 style="margin: 0; font-size: 22px; font-weight: 700; background: linear-gradient(to right, #38bdf8, #0284c7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">AeroPlan AI</h2>
                <span style="font-size: 11px; color: rgba(248, 250, 252, 0.5);">Premium Agentic Travel Planner & Dashboard</span>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 15px;">
            <div style="display: flex; align-items: center; gap: 6px; font-size: 12px; background: var(--secondary-background-color); padding: 6px 12px; border-radius: 8px; border: 1px solid var(--border-color);">
                <span style="color: #22c55e;">●</span> Live Backend Connected
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Helper function to parse itinerary days
def parse_itinerary_days(itinerary_text):
    if not itinerary_text:
        return [], ""
    
    # Try to find Days
    pattern = r'(?:\n|^)(?:##\s*|###\s*|\*\*|)(Day\s+\d+[:\-\s\w]*)(?:\*\*|)(?:\n|$)'
    parts = re.split(pattern, itinerary_text)
    
    days = []
    if len(parts) > 1:
        intro = parts[0].strip()
        for i in range(1, len(parts), 2):
            day_title = parts[i].strip()
            day_content = parts[i+1].strip() if i+1 < len(parts) else ""
            days.append({"title": day_title, "content": day_content})
        return days, intro
    return [], itinerary_text

# Get assistant stream and handle agent status
def get_assistant_stream(user_query, user_id, status_placeholder):
    url = "http://127.0.0.1:8000/travel/chat/stream"
    try:
        response = requests.post(
            url,
            json={"user_query": user_query, "user_id": user_id},
            stream=True,
            timeout=120
        )
        if response.status_code != 200:
            yield f"❌ **Backend Error**: API returned status code {response.status_code}"
            return
        
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data:"):
                    token = decoded_line[5:].strip()
                    # Strip surrounding quotes if EventSourceResponse wrapped it
                    if token.startswith('"') and token.endswith('"'):
                        token = token[1:-1]
                    # Replace escaped newlines
                    token = token.replace('\\n', '\n').replace('\\t', '\t')
                    
                    # Intercept status signals
                    if token.startswith("__STATUS__:"):
                        status_val = token.split(":")[1]
                        st.session_state.agent_status = status_val
                        with status_placeholder:
                            render_agent_status(status_val)
                    else:
                        yield token
    except Exception as e:
        yield f"⚠️ **Connection Error**: Could not connect to travel planner API at {url}.\n\n*Error details: {str(e)}*"

# Sidebar configuration
with st.sidebar:
    st.markdown("## :material/travel_explore: Navigation & Settings")
    
    # Session Persistence Section
    with st.sidebar.container(border=True):
        st.markdown("### :material/history: Saved Trips & Sessions")
        recent_threads = get_recent_threads()
        
        selected_thread = st.selectbox(
            "Select recent trip",
            options=["New Session"] + recent_threads,
            index=0 if st.session_state.session_id not in recent_threads else recent_threads.index(st.session_state.session_id) + 1,
            label_visibility="collapsed"
        )
        
        if selected_thread != "New Session" and selected_thread != st.session_state.session_id:
            st.session_state.session_id = selected_thread
            st.session_state.messages = []
            st.rerun()
            
        st.text_input(
            "Session/Thread ID",
            value=st.session_state.session_id,
            key="session_id_input",
            help="Saves your conversation checkpoints in the SQLite checkpointer database. Enter the same ID to resume later."
        )
        
        if st.session_state.session_id_input != st.session_state.session_id:
            st.session_state.session_id = st.session_state.session_id_input
            st.session_state.messages = []
            st.rerun()

    # Preference Profiles autofill Section
    with st.sidebar.container(border=True):
        st.markdown("### :material/psychology: Saved Preferences")
        profile_options = {
            "🍕 Foodie Explorer": "focus on local food tourism, cafes, traditional dining, culinary workshops",
            "🏛️ History Buff": "historical landmarks, museums, architecture, heritage tours, low pace",
            "🌴 Relaxed Leisure": "luxury beaches, resorts, spa, relaxed pace, minimal walking",
            "🏔️ Active Adventure": "hiking, outdoor activities, nature reserves, adventure sports, fast pace"
        }
        
        selected_profile = st.pills(
            "Select travel style profile:",
            options=list(profile_options.keys()),
            selection_mode="single",
            label_visibility="collapsed"
        )
        if selected_profile:
            st.session_state.autofill_prefs = profile_options[selected_profile]
            st.toast(f"Preferences loaded for {selected_profile}!", icon=":material/thumb_up:")

    # Quick Travel Builder Section
    with st.sidebar.container(border=True):
        st.markdown("### :material/edit_note: Quick Travel Builder")
        dest = st.text_input("Destination", placeholder="e.g. Turkey, Paris, Rome")
        days = st.slider("Duration (days)", min_value=1, max_value=30, value=5)
        budget = st.number_input("Budget amount", min_value=1, value=2000, step=100)
        curr = st.selectbox("Select currency", ["USD", "EUR", "PKR", "GBP"])
        
        default_pref_val = st.session_state.get("autofill_prefs", "")
        prefs = st.text_area("Preferences or style", value=default_pref_val, placeholder="e.g. food tourism, historical places, low pace")
        
        if st.button("Generate & Send Prompt", icon=":material/rocket_launch:", width="stretch"):
            if dest:
                prompt = f"Plan a {days} day trip to {dest} with budget of {budget} {curr}."
                if prefs:
                    prompt += f" Preferences: {prefs}"
                st.session_state.builder_prompt = prompt
            else:
                st.warning("Please specify a destination in the builder!")

    # Theme indicator
    with st.sidebar.container(border=True):
        st.markdown("### :material/contrast: Light / Dark Mode")
        st.caption("Auto-adapts to your browser/system preferences. Toggle theme in Streamlit settings (top right ⚙).")

# Render Custom Header
render_header()

# Layout splitting: Left = Chat, Right = Dashboard
col_chat, col_dash = st.columns([5, 6], gap="large")

# Render Live Agent Status component
def render_agent_status(status):
    steps = [
        {"id": "analyzer", "label": "Analyzing"},
        {"id": "decision", "label": "Searching"},
        {"id": "tools", "label": "Planning"},
        {"id": "planner", "label": "Finalizing"},
    ]
    
    active_idx = -1
    for idx, step in enumerate(steps):
        if step["id"] == status:
            active_idx = idx
            break
            
    if status == "completed":
        active_idx = len(steps)
        
    if active_idx == -1:
        progress_width = 0
    else:
        progress_width = (active_idx / (len(steps) - 1)) * 75
        if active_idx == len(steps):
            progress_width = 75
            
    html = f"""
    <div class="status-tracker">
        <div class="status-line"></div>
        <div class="status-line-fill" style="width: {progress_width}%;"></div>
    """
    
    for idx, step in enumerate(steps):
        step_class = "status-step"
        icon = str(idx + 1)
        
        if status == "completed":
            step_class += " completed"
            icon = "✓"
        elif idx < active_idx:
            step_class += " completed"
            icon = "✓"
        elif idx == active_idx:
            step_class += " active"
            if status != "planner":
                icon = "⚙"
            else:
                icon = "✍"
        
        if status == "completed" and idx == len(steps) - 1:
            step_class = "status-step done"
            
        html += f"""
        <div class="{step_class}">
            <div class="status-circle">{icon}</div>
            <div class="status-label">{step["label"]}</div>
        </div>
        """
        
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

# Render Summary Cards component
def render_summary_cards(state):
    dest = state.get("destination") or "N/A"
    duration = f'{state.get("duration")} Days' if state.get("duration") else "N/A"
    
    budget_val = state.get("budget")
    currency = state.get("currency") or ""
    
    tool_results = state.get("tool_results") or {}
    currency_info = tool_results.get("currency", {})
    
    if budget_val:
        if currency_info and "converted_amount" in currency_info:
            conv_amt = int(currency_info.get("converted_amount"))
            conv_curr = currency_info.get("to")
            budget = f'{budget_val:,} {currency} (~{conv_amt:,} {conv_curr})'
        else:
            budget = f'{budget_val:,} {currency}'
    else:
        budget = "N/A"
        
    prefs = state.get("preferences") or "Standard Style"
    if len(prefs) > 20:
        prefs = prefs[:17] + "..."
        
    html = f"""
    <div class="summary-grid">
        <div class="summary-item">
            <div class="summary-label">Destination</div>
            <div class="summary-val">{dest}</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">Duration</div>
            <div class="summary-val">{duration}</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">Budget</div>
            <div class="summary-val" style="font-size: 13px; line-height: 1.2; word-break: break-all;">{budget}</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">Travel Style</div>
            <div class="summary-val">{prefs}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# Render Weather and Insights
def render_weather_and_info(state):
    tool_results = state.get("tool_results") or {}
    weather = tool_results.get("weather", {})
    travel = tool_results.get("travel", {})
    
    if not weather and not travel:
        return
        
    w_col, i_col = st.columns(2)
    
    if weather and "temperature" in weather:
        temp = weather.get("temperature")
        feels_like = weather.get("feels_like")
        cond = weather.get("condition")
        desc = weather.get("description", "").title()
        humidity = weather.get("humidity")
        
        w_icons = {
            "Clear": "☀️",
            "Clouds": "☁️",
            "Rain": "🌧️",
            "Drizzle": "🌦️",
            "Thunderstorm": "⛈️",
            "Snow": "❄️",
            "Mist": "🌫️",
            "Smoke": "🌫️",
            "Haze": "🌫️",
            "Dust": "🌫️",
            "Fog": "🌫️"
        }
        icon = w_icons.get(cond, "🌤️")
        
        with w_col:
            st.markdown(f"""
            <div class="travel-card weather-card">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 20px;">{icon}</span>
                        <span style="font-size: 14px; font-weight: 600;">Destination Weather</span>
                    </div>
                    <span style="font-size: 11px; padding: 2px 6px; background: rgba(56, 189, 248, 0.2); border-radius: 4px; color: #38bdf8; font-weight: 500;">{cond}</span>
                </div>
                <div style="font-size: 24px; font-weight: 700; color: var(--primary-color); margin-bottom: 2px;">
                    {temp}°C
                </div>
                <div style="font-size: 12px; color: var(--text-color); margin-bottom: 4px;">
                    Feels like {feels_like}°C • {desc}
                </div>
                <div style="font-size: 11px; color: rgba(248, 250, 252, 0.5);">
                    💧 Humidity: {humidity}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    if travel and "capital" in travel:
        country_name = travel.get("country")
        capital = travel.get("capital")
        currency = travel.get("currency")
        pop = travel.get("population", 0)
        pop_fmt = f"{pop:,}" if pop else "N/A"
        langs = ", ".join(travel.get("language", []))
        flag_url = travel.get("flag")
        
        with i_col:
            st.markdown(f"""
            <div class="travel-card info-card">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 20px;">🏛️</span>
                        <span style="font-size: 14px; font-weight: 600;">Country Details</span>
                    </div>
                    {f'<img src="{flag_url}" style="height: 18px; border-radius: 2px; border: 1px solid rgba(255,255,255,0.1);">' if flag_url else ''}
                </div>
                <div style="font-size: 16px; font-weight: 700; color: #a78bfa; margin-bottom: 4px;">
                    {country_name}
                </div>
                <div style="font-size: 12px; color: var(--text-color); line-height: 1.4; margin-bottom: 4px;">
                    🗣️ Lang: {langs} • Capital: {capital}
                </div>
                <div style="font-size: 11px; color: rgba(248, 250, 252, 0.5);">
                    👥 Pop: {pop_fmt} • 💱 Currency: {currency}
                </div>
            </div>
            """, unsafe_allow_html=True)


# Render Budget Allocation Progress
def render_budget_breakdown(state):
    budget_val = state.get("budget")
    currency = state.get("currency") or "USD"
    
    if not budget_val:
        return
        
    st.markdown("<h4 style='font-size: 16px; font-weight: 600; margin-bottom: 12px;'>💰 Budget Allocation Breakdown</h4>", unsafe_allow_html=True)
    
    categories = [
        {"name": "🏨 Accommodation", "percent": 40, "color": "#38bdf8"},
        {"name": "🍔 Food & Dining", "percent": 25, "color": "#fb923c"},
        {"name": "🚗 Transportation", "percent": 20, "color": "#34d399"},
        {"name": "🎟️ Activities", "percent": 15, "color": "#a78bfa"}
    ]
    
    for cat in categories:
        amount = int(budget_val * (cat["percent"] / 100))
        html = f"""
        <div class="budget-item">
            <div class="budget-header">
                <div class="budget-name">{cat["name"]}</div>
                <div class="budget-val">{amount} {currency} ({cat["percent"]}%)</div>
            </div>
            <div class="budget-progress-bg">
                <div class="budget-progress-fill" style="width: {cat["percent"]}%; background-color: {cat["color"]};"></div>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

# Render Itinerary Section
def render_itinerary(state):
    itinerary_text = state.get("itinerary")
    if not itinerary_text:
        st.markdown("""
        <div style="text-align: center; padding: 40px; color: rgba(248, 250, 252, 0.4); border: 1px dashed var(--border-color); border-radius: 12px;">
            <span style="font-size: 40px;">🗓️</span>
            <div style="font-size: 15px; font-weight: 500; margin-top: 10px;">No Active Itinerary</div>
            <div style="font-size: 12px; margin-top: 5px;">Fill the Quick Builder or ask the AI to start generating your custom schedule.</div>
        </div>
        """, unsafe_allow_html=True)
        return
        
    days, intro = parse_itinerary_days(itinerary_text)
    
    tab_details, tab_raw = st.tabs(["🗓️ Detailed Itinerary", "📝 Plain Markdown"])
    
    with tab_details:
        if intro:
            st.markdown(intro)
        
        if days:
            for day in days:
                with st.expander(day["title"], icon=":material/calendar_today:"):
                    st.markdown(day["content"])
        else:
            st.markdown(itinerary_text)
            
    with tab_raw:
        st.code(itinerary_text, language="markdown")

# --- Column 1: Chat Interface ---
with col_chat:
    st.markdown("<h4 style='font-size: 16px; font-weight: 600; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;'><span style='font-size: 18px;'>💬</span> Conversation</h4>", unsafe_allow_html=True)
    
    # Message History Container
    chat_container = st.container(height=500)
    with chat_container:
        if not st.session_state.messages:
            st.markdown("""
            <div style="text-align: center; padding: 40px 20px; color: rgba(248, 250, 252, 0.4);">
                <span style="font-size: 32px;">👋</span>
                <div style="font-size: 14px; font-weight: 500; margin-top: 10px;">Welcome to AeroPlan AI!</div>
                <div style="font-size: 12px; margin-top: 5px;">Describe your dream vacation, or use the Quick Travel Builder in the sidebar.</div>
            </div>
            """, unsafe_allow_html=True)
        
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
    # Handle inputs
    user_input = None
    if "builder_prompt" in st.session_state:
        user_input = st.session_state.pop("builder_prompt")
        
    chat_input = st.chat_input("Ask anything or fill details in the Quick Builder...", submit_mode="disable")
    if chat_input:
        user_input = chat_input
        
    if user_input:
        # Add user query
        st.session_state.messages.append({"role": "user", "content": user_input})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)
                
        # Status placeholder in main col_dash so it updates live
        # We will stream the assistant response inside the chat container
        with chat_container:
            with st.chat_message("assistant"):
                # Define placeholders
                response_placeholder = st.empty()
                
                # Retrieve the status placeholder in col_dash
                # Wait, we need to declare it before the stream loop!
                
        # We use a placeholder on the dashboard side to display live status
        # and update it during streaming
        with col_dash:
            status_placeholder = st.empty()
            
        # Stream response
        response_text = ""
        stream = get_assistant_stream(user_input, st.session_state.session_id, status_placeholder)
        
        for token in stream:
            response_text += token
            response_placeholder.markdown(response_text)
            
        # Save assistant response
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        
        # Load final state after completion to fetch tool results and update dashboard
        st.session_state.agent_status = "completed"
        final_state = load_session_state(st.session_state.session_id)
        st.session_state.loaded_state = final_state
        
        # Rerun to update the entire dashboard view
        st.rerun()

# --- Column 2: Dashboard Interface ---
with col_dash:
    st.markdown("<h4 style='font-size: 16px; font-weight: 600; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;'><span style='font-size: 18px;'>📊</span> Travel Intelligence Dashboard</h4>", unsafe_allow_html=True)
    
    # Active Agent Status Card
    if st.session_state.agent_status:
        render_agent_status(st.session_state.agent_status)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 12px; color: rgba(248, 250, 252, 0.3); border: 1px dashed var(--border-color); border-radius: 8px; margin-bottom: 20px; font-size: 12px;">
            Agent Idle. Waiting for request.
        </div>
        """, unsafe_allow_html=True)
        
    # Summary Metrics Cards
    render_summary_cards(st.session_state.loaded_state)
    
    # Weather & Local Insights Cards
    render_weather_and_info(st.session_state.loaded_state)
    
    # Budget Breakdown
    render_budget_breakdown(st.session_state.loaded_state)
    st.space("medium")
    
    # Collapsible day-by-day Itinerary
    render_itinerary(st.session_state.loaded_state)
