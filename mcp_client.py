import asyncio
import websockets
import json

async def mcp_call(ws, method, params=None, req_id=1):
    req = {
        "jsonrpc": "2.0",
        "method": method,
        "id": req_id
    }
    if params:
        req["params"] = params
    await ws.send(json.dumps(req))
    resp = await ws.recv()
    return json.loads(resp)

async def main():
    uri = "ws://localhost:8080/mcp"
    async with websockets.connect(uri) as ws:
        # Handshake
        handshake = await mcp_call(ws, "mcp.handshake", req_id=1)
        print("Handshake:", handshake["result"])
        # Interactive user query
        while True:
            user_input = input("\nAsk anything (or type 'exit'): ").strip()
            if user_input.lower() == "exit":
                break
            resp = await mcp_call(ws, "get_info", {"query": user_input}, req_id=2)
            print("Answer:", resp.get("result", {}).get("answer", resp.get("error", "")))

if __name__ == "__main__":
    asyncio.run(main())
