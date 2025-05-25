from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from typing import List, Dict 
from dotenv import load_dotenv
import openai
import requests
import tiktoken
import uvicorn
import os

load_dotenv()

MAX_TOKENS = 4000
SUMMARY_THRESHOLD = 3000
SERP_API_KEY = os.getenv("GOOGLE_SERP_KEY")

client = openai.OpenAI(api_key=os.getenv("OPEN_AI_KEY"))

app = FastAPI()

history: List[Dict[str,str]] = []
summaries: List[str] = []
model = 'gpt-4o-mini'
tokenizer = tiktoken.encoding_for_model(model) 

@app.post("/add_message")
def add_message( query: Dict):
    role = query['role']
    content = query['content']
    history.append({"role": role, "content": content})

@app.get("/reset")
def reset_history():
    history.clear()
    summaries.clear()

def count_tokens( messages: List[Dict[str, str]]):
    print(messages)
    num_tokens = 0
    for msg in messages: 
        num_tokens += len(tokenizer.encode(msg['content']))

    return num_tokens

async def enforce_token_limit():
    history_tokens = count_tokens(history)
    summary_tokens = len(tokenizer.encode('\n'.join(summaries)))
    all_tokens = history_tokens + summary_tokens
    print(f"Tokens used: {history_tokens} tokens from history, {summary_tokens} tokens from summaries, total {all_tokens} tokens")
    if all_tokens > SUMMARY_THRESHOLD:
        print(f"Token limit exceeded: {all_tokens} tokens, summarizing history")
        await summarise()

@app.get("/summarize_history")
async def summarise():
    if len(history) == 0:
        return "No conversation yet, nothing to summarise"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=
            [{"role": "system", "content": "Summarize this conversation"}] + history
        
    )

    summary = response.choices[0].message.content
    summaries.append(summary)
    history.clear()
    print(f"Summary added: {summary}")
    print(f"History cleared, {history}")
    return summary

@app.post("/get_context")
async def get_context( max_tokens: int = MAX_TOKENS):
    await enforce_token_limit()
    context = "\n".join(summaries) + '\n'
    context_tokens = len(tokenizer.encode(context))

    result = []

    for msg in reversed(history):
        msg_tokens = len(tokenizer.encode(msg['content']))
        if context_tokens + msg_tokens > max_tokens:
            break

        result.append(f"{msg['role']}: {msg['content']}")
        context_tokens += msg_tokens

    result.reverse()

    return context + "\n".join(result)


@app.post("/tool_call", operation_id="get_info_from_google")
async def GoogleSearchTool(query: Dict) -> str:
    """Searches Google using the Serp Google API to fetch factual information"""
    search_term = query['query']

    URL = "https://serpapi.com/search.json?engine=google"
    PARAMS = {
        "q": search_term,
        "api_key": SERP_API_KEY
    }
    
    try:
        response = requests.get(URL, PARAMS)
        results = response.json()
        # print(results)
        overview = results['ai_overview']
        print(overview)
        answer = overview['text_blocks'][0]['snippet']
        print(answer)
        if response.status_code == 200:
            return answer
        else:
            return "No result found."
    except Exception as e:
        return f"Error: {str(e)}"


mcp = FastApiMCP(
    app,
    name = "Razer Bot",
    description="MCP Server for Adam",
)

mcp.mount()

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
