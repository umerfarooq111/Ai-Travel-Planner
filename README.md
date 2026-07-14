# AeroPlan AI - Premium Agentic Travel Planner & Dashboard

AeroPlan AI is a state-of-the-art, database-backed personal travel planning application. It features a modern **LangGraph** multi-step agent workflow, **FastAPI Server-Sent Events (SSE)** token and status streaming, asynchronous **SQLite checkpoint persistence**, and a premium **Streamlit** dashboard inspired by ChatGPT, Perplexity AI, Airbnb, and Google Travel.

---

## Architecture Overview

AeroPlan AI separates concerns between a lightweight, high-performance FastAPI backend executing the agent graph and a highly styled Streamlit frontend displaying the data in real-time.

## Features

### 1. Live Agent Status Tracker
The interface displays a visual tracker showing the active step of the AI agent as it plans your trip. It transitions in real-time:
*   **Analyzing**: The AI extracts your destination, duration, budget currency, and preferences from your prompt.
*   **Searching**: The agent calls external tools (weather forecasts, travel databases, currency exchange rates).
*   **Planning**: The LLM crafts the custom day-by-day markdown itinerary.
*   **Completed**: The itinerary and metrics are compiled and stored in the database.

### 2. ChatGPT-Style Chat Interface
*   Token-by-token text streaming for instant response rendering.
*   Conversational history bubbles displaying previous user messages and assistant itineraries.
*   Floating bottom-aligned text input that automatically locks during active streaming to prevent thread pollution.

### 3. Travel Intelligence Dashboard
The right side of the screen is a functional control board displaying structured info from the planning database:
*   **Summary Metric Cards**: At-a-glance grids for Destination, Duration, Budget, and Travel Style.
*   **Dynamic Weather & Info Cards**: Color-coded local climate snapshots and local travel advisories/insights gathered by tools.
*   **Budget Allocation Breakdown**: Visual division of your custom budget (Accommodation 40%, Food & Dining 25%, Transportation 20%, Activities 15%) showing exact currency amounts and progress bars.
*   **Interactive Itinerary Explorer**: Switch between a clean day-by-day expandable accordion and a raw markdown tab.

### 4. Session Persistence & History
*   Fully database-backed checkpointer stores graph state dynamically in `travel_planner_checkpoints.db`.
*   A sidebar selector queries the database to list all your **Recent Trips**. Selecting a past trip instantly restores its exact chat logs, dashboard metrics, and itinerary plans.

### 5. Saved Preferences Profiles
*   Sidebar pills let you choose a style profile (e.g., **Foodie Explorer**, **History Buff**, **Relaxed Leisure**, **Active Adventure**) to instantly populate the builder's preferences.
*   Quick Travel Builder to generate prompts in one click.

### 6. Fluid Light/Dark Mode Styling
*   Injects custom glassmorphic styling (`assets/style.css`) with smooth slide-in animations.
*   Colors are bound to Streamlit's official CSS variables (`var(--secondary-background-color)`, `var(--primary-color)`) so the elements natively adapt to your dark/light browser theme.

---

## 🔌 API Endpoints

### `POST /travel/chat/stream`
Initiates the LangGraph run and yields SSE chunks.
*   **Request Payload**:
    ```json
    {
      "user_query": "Plan a 5 day trip to Turkey with budget of 2000 USD",
      "user_id": "traveler_abcd12"
    }
    ```
*   **Response**: EventSource stream yielding text tokens and status markers (`__STATUS__:analyzer`, `__STATUS__:tools`, etc.).

### `GET /travel/state/{thread_id}`
Loads the current checkpoint values for a given traveler.
*   **Response Payload**:
    ```json
    {
      "user_query": "Plan a 5 day trip to Turkey...",
      "destination": "Turkey",
      "duration": 5,
      "budget": 2000,
      "currency": "USD",
      "preferences": "Historical sites",
      "itinerary": "# Day-by-Day Plan...",
      "required_tools": ["travel", "weather", "currency"],
      "tool_results": {
        "weather": {"destination": "Turkey", "weather": "15-25°C, sunny"},
        "currency": {"currency": "USD", "rate": 280},
        "travel": {"destination": "Turkey", "info": "Historical places..."}
      }
    }
    ```

---

## Project Structure

```
├── app/
│   ├── agent/            # LangGraph nodes, state definition, and workflow compile
│   │   ├── decision.py   # Decision logic for required tools
│   │   ├── graph.py      # Main graph assembly with Sqlite checkpointer
│   │   ├── nodes.py      # LLM invocation and tool call wrappers
│   │   └── state.py      # TravelState TypedDict schema
│   ├── api/              # FastAPI routers and Pydantic schemas
│   │   ├── routes.py     # Stream SSE and State retrieval GET routes
│   │   └── schemas.py    # TravelRequest validator
│   ├── llm/              # LLM client setup (Gemini 2.5 Flash)
│   ├── prompts/          # Itinerary prompt templates
│   ├── streaming/        # SSE event streaming and token parsers
│   └── tools/            # Local mock weather, currency, and travel info tools
├── assets/
│   └── style.css         # Custom card designs, animations, and dark/light classes
├── ui.py                 # Streamlit dual-column dashboard frontend
├── run.py                # Command-line testing script
├── pyproject.toml        # uv lock dependencies
└── requirements.txt      # pip dependency fallback
```

---

## Getting Started

### 1. Installation
Ensure you have **Python 3.11+** and **uv** installed.
```bash
# Clone the repository
git clone <repo_url>
cd Ai-Travel-Planner

# Sync virtual environment dependencies
uv sync
```

### 2. Environment Configuration
Create a `.env` file in the root of the project:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 3. Execution

#### Start the FastAPI Backend
```bash
uv run uvicorn app.main:app --reload
```
The backend API runs on `http://127.0.0.1:8000`.

#### Start the Streamlit Frontend
```bash
uv run streamlit run ui.py
```
The browser will automatically open the UI at `http://localhost:8501`.
