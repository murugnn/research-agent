from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
import json
import httpx

app = FastAPI()

async def fetch_web_info(query: str) -> str:
    """Fetch information from DuckDuckGo Instant Answer API."""
    url = "https://api.duckduckgo.com/"
    params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        data = resp.json()
        # Try to get the abstract, fallback to related topics or a message
        if data.get("AbstractText"):
            return data["AbstractText"]
        elif data.get("Answer"):
            return data["Answer"]
        elif data.get("RelatedTopics"):
            for topic in data["RelatedTopics"]:
                if isinstance(topic, dict) and topic.get("Text"):
                    return topic["Text"]
        return "Sorry, I couldn't find any information on that."

async def handle_mcp_request(request):
    method = request.get("method")
    params = request.get("params", {})
    req_id = request.get("id")

    if method == "mcp.handshake":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocol_version": "1.0",
                "capabilities": ["get_info"]
            }
        }
    elif method == "get_info":
        query = params.get("query", "")
        if not query:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32602, "message": "Missing 'query' parameter"}
            }
        info = await fetch_web_info(query)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"answer": info}
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": "Method not found"}
        }

@app.websocket("/mcp")
async def mcp_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            req = json.loads(data)
            response = await handle_mcp_request(req)
            await websocket.send_text(json.dumps(response))
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    print("MCP server running at ws://localhost:8080/mcp")
    uvicorn.run("mcp_server:app", host="0.0.0.0", port=8080, reload=True)
