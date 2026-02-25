import os
import uuid
from dotenv import load_dotenv
from typing import Annotated, TypedDict, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.messages import BaseMessage, HumanMessage

# Load keys
load_dotenv()


# 1. Define State
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], "History"]
    research_data: str
    is_travel_related: bool  # New field to track valid prompts


# 2. Initialize LLM
llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
search_tool = TavilySearch(max_results=3)


# 3. GATEKEEPER NODE (The Filter)
def gatekeeper_node(state: AgentState):
    user_input = state["messages"][-1].content
    print(f"\n--- 🛡️ Gatekeeper analyzing intent: {user_input} ---")

    # We ask the LLM to classify the intent
    check_prompt = (
        f"Is the following prompt related to travel, hospitality, tourism, or food tours? "
        f"Answer ONLY with 'YES' or 'NO'.\n\nPrompt: {user_input}"
    )
    response = llm.invoke(check_prompt).content.strip().upper()

    is_travel = "YES" in response
    return {"is_travel_related": is_travel}


# 4. ROUTING LOGIC
def router(state: AgentState) -> Literal["researcher", "block"]:
    if state["is_travel_related"]:
        return "researcher"
    return "block"


# 5. BLOCK NODE (For non-travel prompts)
def block_node(state: AgentState):
    return {
        "messages": [
            HumanMessage(
                content="🚫 Access Denied: This system only handles travel and hospitality inquiries."
            )
        ]
    }


# 6. Researcher & Writer (Same as before)
def researcher_node(state: AgentState):
    user_input = state["messages"][-1].content
    results = search_tool.invoke({"query": user_input})
    return {
        "research_data": str(results),
        "messages": [HumanMessage(content="Research done.")],
    }


def writer_node(state: AgentState):
    data = state["research_data"]
    prompt = f"Data: {data}\nCreate a luxury travel/food itinerary. Use Markdown."
    response = llm.invoke(prompt)
    return {"messages": [response]}


# 7. Build Graph with Filtering Logic
workflow = StateGraph(AgentState)

workflow.add_node("gatekeeper", gatekeeper_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("writer", writer_node)
workflow.add_node("block", block_node)

workflow.set_entry_point("gatekeeper")

# Conditional Edge: If travel, go to researcher; else, go to block
workflow.add_conditional_edges(
    "gatekeeper", router, {"researcher": "researcher", "block": "block"}
)

workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", END)
workflow.add_edge("block", END)

# 8. Run Loop
if __name__ == "__main__":
    with SqliteSaver.from_conn_string(":memory:") as saver:
        app = workflow.compile(checkpointer=saver, interrupt_before=["writer"])

        print("🏨 Hospitality Specialist Agent Ready")

        while True:
            user_task = input("\n💬 Plan a trip: ")
            if user_task.lower() in ["exit", "quit"]:
                break

            config = {"configurable": {"thread_id": str(uuid.uuid4())}}

            for event in app.stream(
                {"messages": [HumanMessage(content=user_task)]}, config=config
            ):
                for key, value in event.items():
                    if "messages" in value:
                        print(f"[{key.upper()}]: {value['messages'][-1].content}")

            # Only ask to continue if it wasn't blocked
            state = app.get_state(config)
            if state.values.get("is_travel_related"):
                decision = input("\nProceed to itinerary? [C/S]: ").lower()
                if decision == "c":
                    for event in app.stream(None, config=config):
                        for key, value in event.items():
                            if "messages" in value:
                                print(f"\n[FINAL]:\n{value['messages'][-1].content}")
