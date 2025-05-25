# MCP Project

This project implements a basic Message Control Protocol (MCP) system with two main components:

- **MCP Server**: Built using [`fastapi_mcp`](https://github.com/epfml/fastapi-mcp) as the backbone.
- **MCP Client**: Built using [`langgraph`](https://github.com/langchain-ai/langgraph) as the backbone.

The client and server communicate over HTTP and exchange messages according to the assignment specifications.

---
## Project Structure
├── mcp_server.py   # MCP server implementation (FastAPI)

├── mcp_client.py   # MCP client implementation (LangGraph)

├── requirements.txt

---

## Getting Started

Before running the server or client, it is **strongly recommended** to set up a virtual environment.

### Create a Virtual Environment

Using `uv` (recommended for speed and environment isolation):

```bash
pip install uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```
---
### Install Dependencies
```bash
pip install -r requirements.txt
```
---

### Running the MCP Server
```bash
python mcp_server.py
```
---

### Running the MCP Client
```bash
python mcp_client.py
```
##### Once the client is running, you can use the same terminal to send the messages to the MCP Server.
---



