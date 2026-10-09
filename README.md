# Shows MCP Server

A lightweight **Model Context Protocol (MCP)** server built with **FastMCP** and **Streamable HTTP**, designed to run on **Google Cloud Run** and serve tools to **Google Cloud CX Agent Studio (CES)**.

The server provides a single tool, `list`, which queries confirmed 2026 concert events in São Paulo.

---

## Project Structure

```text
.
├── shows.json        # Concert data source
├── server.py         # FastMCP server and 'list' tool definition
├── main.py           # Application entrypoint (Uvicorn on $PORT)
├── requirements.txt  # Dependencies (fastmcp, uvicorn)
├── Dockerfile        # Container image for Cloud Run
├── deploy.sh         # Deployment script (loads .env)
├── test_server.py    # Test suite
├── .env.example      # Example environment variables template
├── .dockerignore     # Build exclusions
└── .gitignore        # Git exclusions
```

---

## MCP Tool: `list`

- **Name**: `list`
- **Description**: Returns confirmed concerts and musical events for 2026 with event name (`evento`), date (`data`), and venue (`local`).
- **Optional Parameters**:
  - `event` *(string)*: Case-insensitive filter by artist/event name.
  - `venue` *(string)*: Case-insensitive filter by venue location.

---

## Local Development & Testing

### 1. Setup Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pytest
```

### 2. Run Tests

```bash
pytest test_server.py -v
```

### 3. Run Locally

```bash
python main.py
```

The server starts on `http://0.0.0.0:8080`.
- MCP Endpoint: `http://localhost:8080/mcp/`
- Health check: `http://localhost:8080/health`

---

## Deploy to Google Cloud Run

### 1. Configure Environment Variables

Copy the example template and set your GCP project details:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
GCP_PROJECT_ID=your-gcp-project-id
GCP_REGION=us-central1
GCP_SERVICE_NAME=shows-mcp-server
```

### 2. Deploy

Run the deploy script (it automatically loads `.env`):

```bash
./deploy.sh
```

Or deploy directly via `gcloud`:

```bash
gcloud run deploy shows-mcp-server \
  --source . \
  --project "<YOUR_GCP_PROJECT_ID>" \
  --region us-central1 \
  --allow-unauthenticated
```

---

## CX Agent Studio Configuration

1. In **CX Agent Studio**, navigate to **Tools** > **Create Tool** > **MCP server**.
2. Fill in the configuration:
   - **Name**: `list`
   - **Server address**: `https://<CLOUD_RUN_URL>/mcp/` *(include trailing slash `/mcp/`)*
   - **Authentication**: `Service agent ID token`
3. Attach the tool to your agent (e.g. `concert_search_agent`).
4. Reference the tool in your agent prompt instructions using:
   ```xml
   <step name="PresentConcerts">
     Ask which artist or city the user wants.
     Present available concerts by retrieving the shows from {@TOOL:list}.
   </step>
   ```
