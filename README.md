# AI Travel Planner

AI Travel Planner is an agentic, database-backed personal assistant that builds personalized travel itineraries. It features a modern LangGraph agent workflow, FastAPI Server-Sent Events (SSE) streaming, SQLite checkpoint persistence, and a premium Streamlit chat interface.

---

## Key Features

1. **LangGraph Agent Workflow**: Orchestrates travel analysis, itinerary drafting, budget optimization (via `toon-format` serialization), and final output formatting.
2. **SQLite Checkpoint Persistence**: Automatically saves conversation state in a local `travel_planner_checkpoints.db` database using synchronous (`SqliteSaver` for CLI) and asynchronous (`AsyncSqliteSaver` for FastAPI) checkpointing.
3. **FastAPI SSE Streaming**: Serves real-time token streaming over `POST /travel/chat/stream`.
4. **Premium Streamlit UI**: A gorgeous slate-dark themed chat interface (`ui.py`) with:
   - Modern Material Symbols icons.
   - Built-in session ID thread persistence settings to reload previous itineraries.
   - An interactive sidebar "Quick Travel Builder" to instantly pre-fill prompts.

---

## Prerequisites

- **Python 3.11** or newer
- **uv** (recommended fast package manager) or standard **pip**

---

## Installation & Setup

1. **Clone the repository and install dependencies**:
   Using `uv`:
   ```bash
   uv sync
   ```
   Or using standard `pip`:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure your environment variables**:
   Create a `.env` file at the root of the project:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key
   ```

---

## Running the Application

### 1. Start the Backend API
Run the FastAPI application with Uvicorn:
```bash
uv run uvicorn app.main:app --reload
```
The backend API runs on `http://127.0.0.1:8000`. You can test the streaming route at `/travel/chat/stream`.

### 2. Start the Frontend UI
Run the Streamlit application:
```bash
uv run streamlit run ui.py
```
The browser will automatically open to `http://localhost:8501`.

### 3. Run the CLI Streamer (Alternative)
For command-line testing with synchronous SQLite persistence:
```bash
uv run python run.py
```

---

## Project Structure

* `app/` — Application source directory
  * `main.py` — FastAPI application entrypoint with asynchronous context lifespan database setup
  * `api/` — API route schemas and endpoints
  * `agent/` — LangGraph agent nodes, state definitions, and graph compilation
  * `llm/` — LLM interface configuration (configured with `gemini-2.5-flash`)
  * `optimization/` — Custom optimization engine integration (`toon-format` serialization)
  * `streaming/` — Event stream transformers and CLI runner helpers
* `.streamlit/` — Streamlit native layout configuration
  * `config.toml` — Custom Slate/Ocean Dark theme settings
* `ui.py` — Streamlit chat application frontend
* `run.py` — CLI test runner
* `requirements.txt` / `pyproject.toml` — Project dependencies

---

## Troubleshooting

- **Gemini API Key issues**: Make sure your `GOOGLE_API_KEY` is active and set in `.env`.
- **Database Lock errors**: Checkpoints are stored in `travel_planner_checkpoints.db`. Ensure the running user has read/write permissions in the project root directory.
