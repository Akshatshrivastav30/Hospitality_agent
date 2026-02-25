import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict, Literal
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
    is_travel_related: bool

# 2. Initialize (Using Groq for speed)
llm = ChatGroq(
    model="llama-3.3-70b-versatile", 
    api_key=os.getenv("GROQ_API_KEY")
)
search_tool = TavilySearch(max_results=3)

# 3. Nodes
def gatekeeper_node(state: AgentState):
    user_input = state['messages'][-1].content
    check_prompt = (
        f"Is the following prompt related to travel, hospitality, or food tours? "
        f"Answer ONLY with 'YES' or 'NO'.\n\nPrompt: {user_input}"
    )
    response = llm.invoke(check_prompt).content.strip().upper()
    return {"is_travel_related": "YES" in response}

def block_node(state: AgentState):
    return {"messages": [HumanMessage(content="🚫 This system only handles travel and hospitality inquiries.")]}

def researcher_node(state: AgentState):
    user_input = state['messages'][-1].content
    results = search_tool.invoke({"query": user_input})
    return {"research_data": str(results)}

def writer_node(state: AgentState):
    print("\n--- ✍️ Writer synthesizing itinerary ---")
    data = state['research_data']
    
    # Get the user's original request from the message history
    user_request = state['messages'][0].content 
    
    # We make the prompt dynamic using the user_request
    prompt = (
        f"The user wants: {user_request}\n\n"
        f"Using this research data: {data}\n"
        f"Create a high-end, professional travel itinerary that exactly matches the duration and location requested above. "
        f"Use Markdown for a clean look."
    )
    
    response = llm.invoke(prompt)
    return {"messages": [response]} 

# 4. Routing Logic
def router(state: AgentState) -> Literal["researcher", "block"]:
    return "researcher" if state["is_travel_related"] else "block"

# 5. Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("gatekeeper", gatekeeper_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("writer", writer_node)
workflow.add_node("block", block_node)

workflow.set_entry_point("gatekeeper")
workflow.add_conditional_edges("gatekeeper", router, {"researcher": "researcher", "block": "block"})
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", END)
workflow.add_edge("block", END)

app = workflow.compile()

# 6. Function for Django to call
def run_hospitality_agent(user_query: str):
    """
    This function takes the query from the Django web form,
    runs the LangGraph, and returns the final string.
    """
    inputs = {"messages": [HumanMessage(content=user_query)]}
    
    # Run the graph until the end
    final_state = app.invoke(inputs)
    
    # Return the last message from the graph
    return final_state["messages"][-1].content