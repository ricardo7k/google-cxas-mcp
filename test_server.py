"""Test suite for Shows MCP Server."""

from starlette.testclient import TestClient
from server import SHOWS, app, list


def test_shows_data_loaded():
    """Verify that all 10 concert events are loaded."""
    assert len(SHOWS) == 10


def test_list_all():
    """Verify returning all concerts without filters."""
    assert len(list()) == 10


def test_list_filter_event():
    """Verify filtering by event name."""
    results = list(event="Maiden")
    assert len(results) == 1
    assert results[0]["evento"] == "Iron Maiden"


def test_list_filter_venue():
    """Verify filtering by venue name."""
    results = list(venue="Nubank Parque")
    assert len(results) == 3


def test_health():
    """Verify health check endpoint."""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_mcp_flow():
    """Verify MCP protocol initialize, tools/list, and tools/call."""
    with TestClient(app) as client:
        # 1. Initialize
        res_init = client.post(
            "/mcp/",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0"},
                },
            },
        )
        assert res_init.status_code == 200

        # 2. Tools list
        res_list = client.post(
            "/mcp/",
            json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        )
        assert res_list.status_code == 200
        assert '"name":"list"' in res_list.text

        # 3. Tools call
        res_call = client.post(
            "/mcp/",
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "list", "arguments": {"event": "BTS"}},
            },
        )
        assert res_call.status_code == 200
        assert "BTS" in res_call.text
