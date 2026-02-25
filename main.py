import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.messages import BaseMessage, HumanMessage

# Load keys
load_dotenv()


# 1. Define State
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], "History"]
    research_data: str


# 2. Initialize (Using Groq for speed and stability)
search_tool = TavilySearch(max_results=3)
llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))


# 3. Researcher Node
def researcher_node(state: AgentState):
    user_input = state["messages"][-1].content
    print(f"\n--- 🔍 Researcher searching: {user_input} ---")
    results = search_tool.invoke({"query": user_input})
    return {
        "research_data": str(results),
        "messages": state["messages"] + [HumanMessage(content="Research complete.")],
    }


# 4. Writer Node
def writer_node(state: AgentState):
    print("--- ✍️ Writer synthesizing itinerary ---")
    data = state["research_data"]
    prompt = f"Data: {data}\nCreate a luxury 2-day food tour in Noida. Use Markdown."
    response = llm.invoke(prompt)
    return {"messages": state["messages"] + [response]}


# 5. Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("researcher", researcher_node)
workflow.add_node("writer", writer_node)
workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", END)
app = workflow.compile()

# 6. Run
if __name__ == "__main__":
    inputs = {
        "messages": [HumanMessage(content="Plan a 2-day luxury food tour in Noida")]
    }
    print(" Running Multi-Agent System...")
    for output in app.stream(inputs):
        for key, value in output.items():
            if "messages" in value:
                print(f"\n[{key.upper()}]: {value['messages'][-1].content}...")
