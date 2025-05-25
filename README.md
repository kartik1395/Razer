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
Please ensure that you create a `.env` file with your Open AI API Key and SERP API Key.
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

### Sample Screenshots of the conversations

![image](https://github.com/user-attachments/assets/fb1de055-9976-4ef0-923c-20c7357f148c)
![image](https://github.com/user-attachments/assets/305599f9-dd86-473e-baf3-e8a6846571dc)


### Notes
1. You can navigate to ```localhost:8000/summarize_history``` to get the summary of the conversation
2. You can navigate to ```localhost:8000/reset``` to reset the chat history. It prints null which means the chat is reset. You can confirm this by going back to ```localhost:8000/summarize_history```
3. This is my first MCP Project. I have tried my best to implement all functions as requested. 


