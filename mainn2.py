import os
import uuid
from dotenv import load_dotenv
from typing import Annotated, TypedDict
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

# 2. Initialize Tools & LLM
search_tool = TavilySearch(max_results=3)
llm = ChatGroq(
    model="llama-3.3-70b-versatile", 
    api_key=os.getenv("GROQ_API_KEY")
)

# 3. Researcher Node
def researcher_node(state: AgentState):
    user_input = state['messages'][-1].content
    print(f"\n--- 🔍 Researcher searching: {user_input} ---")
    results = search_tool.invoke({"query": user_input})
    return {
        "research_data": str(results),
        "messages": state['messages'] + [HumanMessage(content="Researcher: Data gathering complete.")]
    }

# 4. Writer Node
def writer_node(state: AgentState):
    print("\n--- ✍️ Writer synthesizing itinerary ---")
    data = state['research_data']
    # Dynamic prompt based on the user's latest request
    prompt = f"Data: {data}\nCreate a professional travel itinerary based on this data. Use Markdown."
    response = llm.invoke(prompt)
    return {"messages": state['messages'] + [response]}

# 5. Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("researcher", researcher_node)
workflow.add_node("writer", writer_node)

workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", END)

# 6. Continuous Loop Logic
if __name__ == "__main__":
    with SqliteSaver.from_conn_string(":memory:") as saver:
        app = workflow.compile(checkpointer=saver, interrupt_before=["writer"])
        
        print("🏨 Welcome to the Hospitality Agentic System")
        print("(Type 'exit' or 'quit' to stop the program)\n")

        while True:
            user_task = input("\n💬 What would you like to plan? (e.g., 2 days in Noida): ")
            
            if user_task.lower() in ['exit', 'quit']:
                print("👋 Goodbye!")
                break
            
            # Generate a unique thread_id for every new plan so they don't mix up
            thread_id = str(uuid.uuid4())
            config = {"configurable": {"thread_id": thread_id}}
            inputs = {"messages": [HumanMessage(content=user_task)]}
            
            # --- PHASE 1: Researcher runs ---
            for event in app.stream(inputs, config=config):
                for key, value in event.items():
                    if "messages" in value:
                        print(f"[{key.upper()}]: {value['messages'][-1].content}")

            # --- HUMAN INTERVENTION ---
            print("\n" + "-"*30)
            print("⏸️  PAUSED: Research is ready for your review.")
            
            decision = input("Do you want to (C)ontinue to generate itinerary or (S)kip this one? [C/S]: ").lower()

            if decision == 'c':
                # --- PHASE 2: Writer runs ---
                for event in app.stream(None, config=config):
                    for key, value in event.items():
                        if "messages" in value:
                            print(f"\n[{key.upper()} FINAL ITINERARY]:\n{value['messages'][-1].content}")
                print("\n✅ Task Completed successfully.")
            else:
                print("⏭️ Skipping to next request.")