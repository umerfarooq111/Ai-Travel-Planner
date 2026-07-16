import os
import sqlite3
import sys
import uuid
from datetime import date, timedelta

import requests
import streamlit as st

st.set_page_config(
    page_title="AeroPlan AI — Simple Travel Planner",
    page_icon=":material/flight_takeoff:",
    layout="wide",
    initial_sidebar_state="expanded",
)

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.html(f"<style>{f.read()}</style>")


load_css()

# Travel Style Profiles and their default preferences
PROFILE_PREFS = {
    "Foodie Explorer": "Local street food, culinary tours, fine dining, and cooking workshops.",
    "History Buff": "Museums, historic landmarks, archaeological ruins, and cultural heritage sites.",
    "Relaxed Leisure": "Spa sessions, beach relaxation, scenic views, and slow-paced exploration.",
    "Active Adventure": "Hiking trails, nature exploration, outdoor sports, and adventure tours.",
}

SUGGESTIONS = [
    "Plan a 5-day trip to Turkey with a budget of 2000 USD",
    "I want a 7-day culinary trip to Tokyo under 4000 EUR",
    "Plan a historical tour of Rome for 4 days with 1500 GBP",
    "Active adventure trip to Switzerland for 6 days with 3000 USD",
]


def load_backend_state(thread_id: str) -> dict:
    try:
        response = requests.get(
            f"http://127.0.0.1:8000/travel/state/{thread_id}",
            timeout=5,
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return {}


def get_saved_trips() -> list[str]:
    try:
        conn = sqlite3.connect("travel_planner_checkpoints.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
        trips = [row[0] for row in cursor.fetchall() if row[0]]
        conn.close()
        return [trip for trip in trips if not trip.startswith("test_") and not trip.startswith("cli_")]
    except Exception:
        return []


def render_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-icon">✈</div>
                <div>
                    <h1>AeroPlan AI</h1>
                    <p>Travel Planner</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(":material/add: New Trip", width="stretch", type="primary"):
            st.session_state.session_id = f"trip_{uuid.uuid4().hex[:8]}"
            st.session_state.messages = []
            st.session_state.agent_status = None
            st.session_state.loaded_state = {}
            st.session_state.selected_profile = None
            st.session_state.builder_dest = "Paris"
            st.session_state.builder_days = 5
            st.session_state.builder_budget = 2000
            st.session_state.builder_currency = "USD"
            st.session_state.builder_pref = ""
            st.rerun()

        st.caption("1. Select a Travel Style")
        
        # Style Profile segmented control
        profile = st.segmented_control(
            "Style profile",
            options=list(PROFILE_PREFS.keys()),
            key="selected_profile",
            label_visibility="collapsed",
        )
        
        # Reactive update of builder preferences
        if "last_profile" not in st.session_state:
            st.session_state.last_profile = None
            
        if st.session_state.selected_profile != st.session_state.last_profile:
            st.session_state.last_profile = st.session_state.selected_profile
            if st.session_state.selected_profile:
                st.session_state.builder_pref = PROFILE_PREFS[st.session_state.selected_profile]

        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("2. Customize Criteria")
        
        # Builder Form Elements
        builder_dest = st.text_input(
            "Destination", 
            value=st.session_state.get("builder_dest", "Paris"),
            placeholder="e.g. Paris, Tokyo, Turkey"
        )
        st.session_state.builder_dest = builder_dest
        
        builder_days = st.number_input(
            "Duration (days)",
            min_value=1,
            max_value=30,
            value=st.session_state.get("builder_days", 5)
        )
        st.session_state.builder_days = builder_days
        
        col_b1, col_b2 = st.columns([2, 1])
        with col_b1:
            builder_budget = st.number_input(
                "Budget",
                min_value=100,
                max_value=100000,
                value=st.session_state.get("builder_budget", 2000)
            )
            st.session_state.builder_budget = builder_budget
        with col_b2:
            builder_currency = st.selectbox(
                "Currency",
                ["USD", "EUR", "GBP", "PKR", "TRY", "AED"],
                index=0
            )
            st.session_state.builder_currency = builder_currency
            
        builder_pref = st.text_area(
            "Preferences",
            value=st.session_state.get("builder_pref", ""),
            placeholder="e.g. historic tours, fine dining, beach relaxation",
            height=80
        )
        st.session_state.builder_pref = builder_pref

        if st.button(":material/send: Generate Itinerary", type="primary", width="stretch"):
            prompt = (
                f"Plan a {builder_days}-day trip to {builder_dest} "
                f"with a budget of {builder_budget} {builder_currency}. "
                f"My preferences are: {builder_pref if builder_pref else 'standard sightseeing'}."
            )
            st.session_state.messages = []
            st.session_state.agent_status = "analyzer"
            st.session_state.pending_query = prompt
            st.rerun()

        st.markdown("<hr style='margin: 12px 0; border: none; border-top: 1px solid rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
        st.caption("Recent Itineraries")

        saved_trips = get_saved_trips()
        if saved_trips:
            for trip in saved_trips[:8]:
                label = trip.replace("trip_", "Trip ").replace("traveler_", "Trip ")
                if st.button(label, key=f"trip_btn_{trip}", width="stretch"):
                    st.session_state.session_id = trip
                    st.session_state.messages = []
                    st.session_state.agent_status = "completed"
                    st.session_state.loaded_state = load_backend_state(trip)
                    
                    # Populate builder with this trip state if available
                    state_vals = st.session_state.loaded_state
                    if state_vals.get("destination"):
                        st.session_state.builder_dest = state_vals.get("destination")
                        st.session_state.builder_days = state_vals.get("duration", 5)
                        st.session_state.builder_budget = state_vals.get("budget", 2000)
                        st.session_state.builder_currency = state_vals.get("currency", "USD")
                        st.session_state.builder_pref = state_vals.get("preferences", "")
                    
                    st.rerun()
        else:
            st.caption("No previous trips yet.")


def render_status_tracker(status: str | None):
    if not status:
        return

    # Map the current agent status node to 4 steps
    step_states = {
        "step1": "pending", "step2": "pending", "step3": "pending", "step4": "pending",
        "line1": "", "line2": "", "line3": ""
    }

    if status in ("analyzer", "preference"):
        step_states["step1"] = "active"
    elif status in ("decision", "tools"):
        step_states["step1"] = "completed"
        step_states["step2"] = "active"
        step_states["line1"] = "active"
    elif status == "planner":
        step_states["step1"] = "completed"
        step_states["step2"] = "completed"
        step_states["step3"] = "active"
        step_states["line1"] = "completed"
        step_states["line2"] = "active"
    elif status == "completed":
        step_states["step1"] = "completed"
        step_states["step2"] = "completed"
        step_states["step3"] = "completed"
        step_states["step4"] = "completed"
        step_states["line1"] = "completed"
        step_states["line2"] = "completed"
        step_states["line3"] = "completed"

    st.markdown(
        f"""
        <div class="status-tracker-container">
            <div class="steps-tracker">
                <div class="step {step_states['step1']}">
                    <div class="step-num">{"✓" if step_states['step1'] == "completed" else "1"}</div>
                    <div class="step-name">Analyzing</div>
                </div>
                <div class="step-line {step_states['line1']}"></div>
                <div class="step {step_states['step2']}">
                    <div class="step-num">{"✓" if step_states['step2'] == "completed" else "2"}</div>
                    <div class="step-name">Searching</div>
                </div>
                <div class="step-line {step_states['line2']}"></div>
                <div class="step {step_states['step3']}">
                    <div class="step-num">{"✓" if step_states['step3'] == "completed" else "3"}</div>
                    <div class="step-name">Planning</div>
                </div>
                <div class="step-line {step_states['line3']}"></div>
                <div class="step {step_states['step4']}">
                    <div class="step-num">{"✓" if step_states['step4'] == "completed" else "4"}</div>
                    <div class="step-name">Completed</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_typing_indicator():
    st.markdown(
        """
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_summary_metrics(destination: str, duration: int, budget: float, currency: str, preferences: str):
    style = preferences if preferences else "General"
    if len(style) > 20:
        style = style[:18] + "..."
        
    formatted_budget = f"{currency} {budget:,.0f}" if currency else f"${budget:,.0f}"
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Destination", destination or "N/A", border=True)
    with col2:
        st.metric("Duration", f"{duration or 0} Days", border=True)
    with col3:
        st.metric("Total Budget", formatted_budget, border=True)
    with col4:
        st.metric("Travel Style", style, border=True)


def render_weather_and_info(tool_results: dict):
    if not tool_results:
        return
        
    weather = tool_results.get("weather", {})
    travel = tool_results.get("travel", {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("**🌦️ Destination Weather**")
            if weather:
                temp = weather.get("temperature", 20.0)
                cond = weather.get("condition", "Clear")
                desc = weather.get("description", "clear sky")
                feels = weather.get("feels_like", 20.0)
                humidity = weather.get("humidity", 50)
                wind = weather.get("wind_speed", 3.0)
                city = weather.get("city", "Local")
                
                # Temperature info in a simple text layout
                st.markdown(f"### {temp:.1f}°C")
                st.caption(f"{cond} ({desc}) in {city}")
                st.markdown(
                    f"""
                    - **Feels Like:** {feels:.1f}°C
                    - **Humidity:** {humidity}%
                    - **Wind Speed:** {wind} m/s
                    """
                )
            else:
                st.write("Weather insights not available.")
            
    with col2:
        with st.container(border=True):
            st.markdown("**🌐 Destination Guide**")
            if travel:
                country = travel.get("country", "Unknown")
                capital = travel.get("capital", "N/A")
                curr = travel.get("currency", "USD")
                langs = ", ".join(travel.get("language", ["Local"]))
                pop = travel.get("population", 0)
                
                st.markdown(f"### {country}")
                st.caption("Country Profile & Guide")
                st.markdown(
                    f"""
                    - **Capital City:** {capital}
                    - **Local Currency:** {curr}
                    - **Languages:** {langs}
                    - **Population:** {pop:,}
                    """
                )
            else:
                st.write("Country details not available.")


def render_budget_breakdown(budget: float, currency: str):
    if not budget:
        return
        
    categories = [
        {"name": "Accommodation (40%)", "pct": 40},
        {"name": "Food & Dining (25%)", "pct": 25},
        {"name": "Transportation (20%)", "pct": 20},
        {"name": "Activities (15%)", "pct": 15},
    ]
    
    st.markdown("#### Budget Breakdown")
    
    with st.container(border=True):
        for cat in categories:
            amount = budget * (cat["pct"] / 100)
            formatted = f"{currency} {amount:,.2f}" if currency else f"${amount:,.2f}"
            st.progress(cat["pct"] / 100, text=f"**{cat['name']}** — {formatted}")


def get_assistant_stream(user_query: str, user_id: str, status_slot):
    url = "http://127.0.0.1:8000/travel/chat/stream"
    try:
        response = requests.post(
            url,
            json={"user_query": user_query, "user_id": user_id},
            stream=True,
            timeout=120,
        )
        if response.status_code != 200:
            yield "I'm having trouble reaching our travel service right now. Please try again in a moment."
            return

        for line in response.iter_lines():
            if not line:
                continue
            decoded = line.decode("utf-8")
            if not decoded.startswith("data:"):
                continue

            token = decoded[5:].strip()
            if token.startswith('"') and token.endswith('"'):
                token = token[1:-1]
            token = token.replace("\\n", "\n").replace("\\t", "\t")

            if token.startswith("__STATUS__:"):
                status = token.split(":", 1)[1]
                st.session_state.agent_status = status
                with status_slot:
                    render_status_tracker(status)
            else:
                yield token
    except Exception:
        yield (
            "I couldn't connect to the travel planner service. "
            "Make sure the backend is running, then try your search again."
        )


# ── Session state ──────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = f"trip_{uuid.uuid4().hex[:8]}"
if "agent_status" not in st.session_state:
    st.session_state.agent_status = None
if "loaded_state" not in st.session_state:
    st.session_state.loaded_state = {}

# Initialize builder fields
if "builder_dest" not in st.session_state:
    st.session_state.builder_dest = "Paris"
if "builder_days" not in st.session_state:
    st.session_state.builder_days = 5
if "builder_budget" not in st.session_state:
    st.session_state.builder_budget = 2000
if "builder_currency" not in st.session_state:
    st.session_state.builder_currency = "USD"
if "builder_pref" not in st.session_state:
    st.session_state.builder_pref = ""

# Load database state if session changes
if (
    "loaded_session_id" not in st.session_state
    or st.session_state.loaded_session_id != st.session_state.session_id
):
    db_state = load_backend_state(st.session_state.session_id)
    st.session_state.loaded_state = db_state
    st.session_state.loaded_session_id = st.session_state.session_id
    if db_state.get("itinerary") and db_state.get("user_query"):
        st.session_state.messages = [
            {"role": "user", "content": db_state["user_query"]},
            {"role": "assistant", "content": db_state["itinerary"]},
        ]
        st.session_state.agent_status = "completed"
        
        # Populate builder widgets with loaded state
        st.session_state.builder_dest = db_state.get("destination", "Paris")
        st.session_state.builder_days = db_state.get("duration", 5)
        st.session_state.builder_budget = db_state.get("budget", 2000)
        st.session_state.builder_currency = db_state.get("currency", "USD")
        st.session_state.builder_pref = db_state.get("preferences", "")
    else:
        st.session_state.messages = []
        st.session_state.agent_status = None

render_sidebar()

# ── Hero ───────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="hero-banner">
        <div>
            <h2>Explore the World with AeroPlan AI</h2>
            <p>Premium Agentic Travel Planner · Dynamic Climate & Budget Analytics · Seamless Itineraries</p>
        </div>
        <div class="hero-plane">✈️</div>
    </div>
    """,
    unsafe_allow_html=True,
)

col_chat, col_dashboard = st.columns([5, 6], gap="large")

# ── Left Column: AI chat ───────────────────────────────────────────────────

with col_chat:
    st.markdown(
        """
        <div class="glass-card" style="padding:20px;min-height:640px;">
            <div class="chat-panel-header">
                <div class="chat-avatar">🤖</div>
                <div>
                    <h3>AeroPlan Concierge</h3>
                    <p>Ask me to design, adjust, or detail your dream trip itinerary</p>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    chat_box = st.container(height=420)
    with chat_box:
        if not st.session_state.messages:
            st.markdown(
                """
                <div class="chat-welcome">
                    <div class="chat-welcome-icon">🌍</div>
                    <h4>Your Personal Travel Planner</h4>
                    <p>Tell me where you want to go, for how long, and your budget.<br>
                    Or use the <strong>Quick Travel Builder</strong> on the left panel to get started.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            for suggestion in SUGGESTIONS:
                if st.button(suggestion, key=f"sug_{suggestion[:25]}", width="stretch"):
                    st.session_state.pending_query = suggestion

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"], avatar="🧑‍✈️" if msg["role"] == "assistant" else None):
                st.markdown(msg["content"])

    st.markdown("</div>", unsafe_allow_html=True)

    user_input = st.session_state.pop("pending_query", None)
    chat_input = st.chat_input("Plan a 5 day trip to Istanbul with budget of 3000 USD...")
    if chat_input:
        user_input = chat_input

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.agent_status = "analyzer"

        with chat_box:
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant", avatar="🧑‍✈️"):
                typing_slot = st.empty()
                with typing_slot:
                    render_typing_indicator()
                response_slot = st.empty()

        with col_dashboard:
            status_slot = st.empty()
            
        response_text = ""
        stream = get_assistant_stream(user_input, st.session_state.session_id, status_slot)

        for token in stream:
            response_text += token
            typing_slot.empty()
            response_slot.markdown(response_text + "▌")

        typing_slot.empty()
        response_slot.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.session_state.agent_status = "completed"

        final_state = load_backend_state(st.session_state.session_id)
        st.session_state.loaded_state = final_state
        st.rerun()

# ── Right Column: Travel Intelligence Dashboard ───────────────────────────

with col_dashboard:
    state_vals = st.session_state.loaded_state
    
    # 1. Real-time / Completed Status Tracker
    if st.session_state.agent_status:
        render_status_tracker(st.session_state.agent_status)
        
    if state_vals and state_vals.get("destination"):
        # We have active planning results!
        dest = state_vals.get("destination")
        duration = state_vals.get("duration", 0)
        budget = state_vals.get("budget", 0)
        currency = state_vals.get("currency", "USD")
        prefs = state_vals.get("preferences", "")
        itinerary = state_vals.get("itinerary")
        tool_results = state_vals.get("tool_results", {})
        
        # Dashboard Wrapper Card
        st.markdown('<div class="glass-card" style="padding:20px;">', unsafe_allow_html=True)
        
        st.markdown(
            f"""
            <div class="search-card-header">
                <h3>Travel Dashboard</h3>
                <span>{dest} Plan</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # Summary metrics
        render_summary_metrics(dest, duration, budget, currency, prefs)
        
        st.write("")
        
        # Dashboard Tabs
        tab_itin, tab_budget, tab_info = st.tabs([
            "📅 Itinerary Explorer",
            "💰 Budget Breakdown",
            "🌤️ Destination Insights"
        ])
        
        with tab_itin:
            if itinerary:
                st.markdown(itinerary)
            else:
                st.write("No itinerary generated.")
                
        with tab_budget:
            render_budget_breakdown(budget, currency)
            
        with tab_info:
            render_weather_and_info(tool_results)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        # Welcome Screen if no active search has been performed
        st.markdown(
            """
            <div class="empty-dashboard">
                <div class="empty-dashboard-icon">🛫</div>
                <h3>Ready to Design Your Trip?</h3>
                <p>Use the Quick Travel Builder in the sidebar or ask the concierge to generate your itinerary and trip metrics.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
