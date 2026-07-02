## Copilot FastAPI App

### Run with uv

- Dev server (auto-reload):

```bash
uv run --package copilot copilot-dev
```

- Production-style local run:

```bash
uv run --package copilot copilot-server
```

The server runs on `http://127.0.0.1:8000`.

### Endpoints

- `GET /` returns a simple hello payload.
- `GET /items/{item_id}?q=...` returns item data.
- `POST /agent` sends user input to the OpenAI Agent runtime.

Example request:

```bash
curl -X POST http://127.0.0.1:8000/agent \
	-H "Content-Type: application/json" \
	-d '{"user_input":"When did the Roman Empire fall?"}'
```
