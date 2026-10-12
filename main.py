import hashlib
import json
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("exam-mcp-server")

@mcp.tool(name="solve_challenge")
def solve_challenge() -> str:
    """Return the required hash for the current exam challenge."""
    return ""

app = FastAPI()

@app.post("/mcp")
async def handle_mcp(request: Request):
    body = await request.json()
    method = body.get("method")
    headers = request.headers

    if method == "initialize":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {
                "protocolVersion": "2025-03-26",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "exam-mcp-server",
                    "version": "1.0.0"
                }
            }
        })

    if method == "notifications/initialized":
        return Response(status_code=202)

    if method == "tools/list":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {
                "tools": [{
                    "name": "solve_challenge",
                    "description": "Hash the challenge header with the registered exam email.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }]
            }
        })

    if method == "tools/call":
        params = body.get("params", {})
        if params.get("name") != "solve_challenge":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {"code": -32602, "message": "Unknown tool"}
            })

        challenge = headers.get("x-exam-challenge", "")
        email = "24f2001122@ds.study.iitm.ac.in"
        digest = hashlib.sha256(
            f"{challenge}:{email}".encode("utf-8")
        ).hexdigest()[:16]

        return JSONResponse({
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {
                "content": [{
                    "type": "text",
                    "text": digest
                }]
            }
        })

    return JSONResponse({
        "jsonrpc": "2.0",
        "id": body.get("id"),
        "error": {"code": -32601, "message": "Method not found"}
    })

@app.get("/")
async def health():
    return {"status": "ok"}

@app.get("/mcp")
async def mcp_info():
    return {"status": "MCP endpoint ready"}

