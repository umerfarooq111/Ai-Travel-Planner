# AI Travel Planner

AI Travel planner is an agent-driven FastAPI project that streams tokenized responses for travel planning tasks.

Prerequisites
- Python 3.11 or newer
- A virtual environment (venv, conda, or similar)

Install dependencies

```bash
python -m venv .venv
source .venv/Scripts/activate    # Windows: .venv\\Scripts\\activate
pip install --upgrade pip
pip install -r requirements.txt  # or: pip install . (uses pyproject.toml)
```

Running the API (development)

Start the FastAPI server with Uvicorn:

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at http://127.0.0.1:8000. A simple health route is exposed at `/`.

Streaming chat endpoint

- POST `/travel/chat/stream` — server-sent events streaming of token updates.

Example: streaming runner

There is a simple streamer runner at `run.py` that demonstrates the `stream_agent` function. Run it with:

```bash
python run.py
```

Project layout

- `app/` — application package
	- `main.py` — FastAPI application instance and router inclusion
	- `api/routes.py` — API routes (SSE streaming endpoint)
	- `streaming/` — streaming helpers and runner
	- `agent/` — agent graph, nodes, and state management

Troubleshooting

- If Uvicorn fails to start, ensure your Python environment is active and dependencies installed.
- Common commands:

```bash
python -V
pip freeze | findstr uvicorn
```

If you still see an error when starting Uvicorn, paste the full traceback into an issue and I'll help debug further.

Contributing

Open a PR with fixes or features. For large changes, open an issue first to discuss design.

License

Add your license here.
