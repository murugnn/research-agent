# Research Agent

This is a real-time user query application powered by **MCP servers** and **WebSockets**. Users can input queries about various topics such as news, movies, finance, or general knowledge. The system processes these queries using structured JSON-RPC 2.0 messages over WebSocket connections and returns relevant responses from integrated sources.

---

## 🚀 Features

- Real-time communication using WebSockets
- JSON-RPC 2.0-based MCP server architecture
- Session-aware, bidirectional messaging
- Tool-based query resolution
- Supports:
  - Wikipedia search
  - News updates via NewsData.io
  - Stock data via `yfinance`
  - Movie information via TMDb
  - Web scraping with BeautifulSoup

---

## 🛠️ Tech Stack

- Python 3
- WebSockets (`websockets`, `asyncio`)
- JSON-RPC 2.0
- BeautifulSoup + `requests`
- `yfinance`, `wikipedia`, and other APIs

---

## 📦 Setup

1. Clone the repository 

2. Install dependencies  
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server and client
    ```bash
    python server.py
    python client.py #run this only after the server program
    ```
