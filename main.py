"""Server entrypoint for local execution and Google Cloud Run."""

import os
import uvicorn
from server import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"Starting Shows MCP Server on {host}:{port}...")
    uvicorn.run(
        app,
        host=host,
        port=port,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
