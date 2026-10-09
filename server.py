"""MCP Server providing confirmed concerts and live music events."""

import json
from pathlib import Path
from typing import Any, Dict, List

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse

# Load concert data
DATA_PATH = Path(__file__).parent / "shows.json"
with open(DATA_PATH, "r", encoding="utf-8") as f:
    SHOWS: List[Dict[str, Any]] = json.load(f)

# Initialize FastMCP server
mcp = FastMCP(
    name="Shows MCP Server",
    instructions="MCP server providing confirmed 2026 concert events.",
)


@mcp.tool(
    name="list",
    description=(
        "Returns the list of confirmed concerts and musical events for 2026. "
        "Each item contains the artist/event name ('evento'), date in YYYY-MM-DD format ('data'), "
        "and venue location ('local'). "
        "Allows optional filtering by event/artist name or venue location."
    ),
)
def list(event: str = "", venue: str = "") -> List[Dict[str, Any]]:
    """Retrieve the list of concerts with optional filters.

    Args:
        event: Event or artist name to filter by.
        venue: Venue name or location to filter by.

    Returns:
        List of concerts matching the criteria.
    """
    results = SHOWS

    if event and event.strip():
        term = event.strip().lower()
        results = [show for show in results if term in show["evento"].lower()]

    if venue and venue.strip():
        term = venue.strip().lower()
        results = [show for show in results if term in show["local"].lower()]

    return results


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for container monitoring."""
    return JSONResponse(
        {
            "status": "healthy",
            "service": "shows-mcp-server",
            "total_shows": len(SHOWS),
        }
    )


@mcp.custom_route("/", methods=["GET"])
async def root_info(request: Request) -> JSONResponse:
    """Root metadata endpoint with service details."""
    return JSONResponse(
        {
            "service": "Shows MCP Server",
            "status": "online",
            "mcp_endpoint": "/mcp/",
            "transport": "Streamable HTTP",
            "tools": ["list"],
            "total_shows": len(SHOWS),
        }
    )


# Underlying ASGI app with Streamable HTTP transport at /mcp
_base_app = mcp.http_app(
    path="/mcp",
    stateless_http=True,
    host_origin_protection=False,
)


class NormalizeSlashMiddleware:
    """Handles requests directly for /mcp and /mcp/ without redirects,
    and returns SSE ping for GET probes required by Streamable HTTP."""

    def __init__(self, asgi_app):
        self.asgi_app = asgi_app

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            path = scope.get("path", "")
            method = scope.get("method", "")
            if path in ("/mcp/", "/mcp") and method == "GET":
                async def sse_gen():
                    yield "event: ping\ndata: {}\n\n"
                response = StreamingResponse(sse_gen(), media_type="text/event-stream")
                await response(scope, receive, send)
                return
            if path == "/mcp/":
                scope = dict(scope)
                scope["path"] = "/mcp"
        await self.asgi_app(scope, receive, send)


app = NormalizeSlashMiddleware(_base_app)
