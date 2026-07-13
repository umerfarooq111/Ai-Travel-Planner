import streamlit as st
import requests
import uuid
import sys

# Configure page layout and style
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling
st.markdown("""
<style>
    .reportview-container {
        background: #0f172a;
    }
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f1f5f9;
    }
    .stSidebar {
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    h1 {
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    .stButton>button {
        background: linear-gradient(90deg, #0284c7 0%, #4f46e5 100%) !important;
        color: white !important;
        border: none !important;
        transition: all 0.3s ease !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to generate stream
def get_assistant_stream(user_query, user_id):
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
                    yield token
    except Exception as e:
        yield f"⚠️ **Connection Error**: Could not connect to travel planner API at {url}.\n\n*Error details: {str(e)}*"

# Title and App Header
st.title("🗺️ AI Personal Travel Assistant")
st.caption("Plan your dream vacation with real-time agentic streaming and database-backed persistence.")

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = f"traveler_{uuid.uuid4().hex[:6]}"

# Sidebar config
with st.sidebar:
    st.markdown("## ✈️ Travel Settings")
    
    # Session Persistence Section
    st.markdown("### 🔑 Persistence Thread")
    session_id = st.text_input(
        "Session ID / Thread ID",
        value=st.session_state.session_id,
        help="This ID saves your conversation checkpoints in the SQLite checkpointer database. Enter the same ID to resume later."
    )
    if session_id != st.session_state.session_id:
        st.session_state.session_id = session_id
        st.session_state.messages = []  # Reset view if thread changed
        st.rerun()

    st.markdown("---")
    
    # Quick Travel Builder Section
    st.markdown("### 📝 Quick Travel Builder")
    dest = st.text_input("Destination", placeholder="e.g. Turkey, Paris, Rome")
    days = st.slider("Duration (Days)", min_value=1, max_value=30, value=5)
    budget = st.number_input("Budget Amount", min_value=1, value=2000, step=100)
    curr = st.selectbox("Currency", ["USD", "EUR", "PKR", "GBP"])
    prefs = st.text_area("Preferences / Style", placeholder="e.g. food tourism, historical places, low pace")
    
    if st.button("Generate & Send Prompt"):
        if dest:
            prompt = f"Plan a {days} day trip to {dest} with budget of {budget} {curr}."
            if prefs:
                prompt += f" Preferences: {prefs}"
            st.session_state.builder_prompt = prompt
        else:
            st.warning("Please specify a destination in the builder!")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle builder trigger
user_input = None
if "builder_prompt" in st.session_state:
    user_input = st.session_state.pop("builder_prompt")

# Regular chat input
chat_input = st.chat_input("Ask anything or fill details in the Quick Builder...")
if chat_input:
    user_input = chat_input

if user_input:
    # Save & Display user query
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    # Generate & Display streamed response
    with st.chat_message("assistant"):
        stream = get_assistant_stream(user_input, st.session_state.session_id)
        response_text = st.write_stream(stream)
        
    # Save response
    st.session_state.messages.append({"role": "assistant", "content": response_text})
