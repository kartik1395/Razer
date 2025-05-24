from langgraph.graph import StateGraph, END
from openai import OpenAI
import requests
import os
from dotenv import load_dotenv
from typing import TypedDict


load_dotenv()

MCP_SERVER_URL = "http://localhost:8000"  
key = os.getenv("OPEN_AI_KEY")
client = OpenAI(api_key=key) #Use your open ai key, I have not passed the .env file in the repo

FACTUAL_KEYWORDS = ["what is", "what are", "how many", "when did", "where is", "who is",
            "define", "explain", "tell me about", "information about", "facts about",
            "history of", "genres", "types of", "examples of", "list of"]

state = {
    "user_input": "",
    "context": "",
    "tool_result": "",
    "use_tool": False,
    "final_prompt": "",
    "llm_response": ""
}

class GraphState(TypedDict, total=False):
    user_input: str
    context: str
    tool_result: str
    prompt: str
    response: str

#InputNode
def input_node(state):
    user_input = state["user_input"]
    return {"user_input": user_input}

#CheckContextNode
def check_context_node(state):
    r = requests.post("http://localhost:8000/get_context")
    context = r.text
    return {"context": context, **state}

#ToolDecisionNode
def is_factual_question(text):
    lowered = text.lower()
    return any(kw in lowered for kw in FACTUAL_KEYWORDS)

def tool_decision_node(state):
    user_input = state["user_input"]
    if is_factual_question(user_input):
        print("It's a factual question")
        return {"use_tool": True, **state}
    return {"use_tool": False, **state}


#ToolCallNode
def tool_call_node(state):
    print("Calling Google Tool")
    query = state["user_input"]
    r = requests.post("http://localhost:8000/tool_call", json={"query": f"{query}"})
    tool_result = r.text#.json()["result"]
    return {"tool_result": tool_result, "response": tool_result, **state}

#PromptAssemblyNode
def prompt_assembly_node(state):
    persona = "Adam is a wise, centuries-old sage of the northern isles who guides with empathy and lore."
    context = state.get("context", "")
    user_input = state["user_input"]
    tool_info = state.get("tool_result", "")

    prompt = f"{persona}\n\nContext:\n{context}\n\nTool Result:\n{tool_info}\n\nUser: {user_input}"
    return {"prompt": prompt, **state}

#LLMNode
def llm_node(state):
    prompt = state["prompt"]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    reply = response.choices[0].message.content
    return {"response": reply, **state}

#OutputNode
def output_node(state):
    user_msg = {"role": "user", "content": state["user_input"]}
    assistant_msg = {"role": "assistant", "content": state["response"]}

    requests.post("http://localhost:8000/add_message", json=user_msg)
    requests.post("http://localhost:8000/add_message", json=assistant_msg)

    print(f"Adam: {state['response']}")
    return state

def tool_router(state):
    return "use_tool" if is_factual_question(state["user_input"]) else "skip_tool"

def build_langgraph():
    builder = StateGraph(GraphState)
    
    builder.set_entry_point("Input")
    builder.add_node("Input", input_node)
    builder.add_node("CheckContext", check_context_node)
    builder.add_node("ToolDecision", tool_decision_node)
    builder.add_node("ToolCall", tool_call_node)
    builder.add_node("PromptAssembly", prompt_assembly_node)
    builder.add_node("LLM", llm_node)
    builder.add_node("Output", output_node)

    builder.add_edge("Input", "CheckContext")
    builder.add_edge("CheckContext", "ToolDecision")
    builder.add_conditional_edges("ToolDecision", 
        tool_router,
        {
        "use_tool": "ToolCall",
        "skip_tool": "PromptAssembly"
    }
    )
    builder.add_edge("ToolCall", "Output")
    builder.add_edge("PromptAssembly", "LLM")
    builder.add_edge("LLM", "Output")
    builder.add_edge("Output", END)

    return builder.compile()

if __name__ == "__main__":
    graph = build_langgraph()
    while True:
        user_input = input("You: ")
        print("-" * 100)
        graph.invoke({"user_input": user_input})