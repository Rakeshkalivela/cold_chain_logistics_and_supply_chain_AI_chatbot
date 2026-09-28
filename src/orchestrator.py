import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

# ==========================================================
# 1. Path resolution & Setup
# ==========================================================

script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent

# Force Python to look inside main project folder whenever it tries to import custom modules or scripts
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agent_tools import query_telemetry_db, fetch_corridor_conditions, search_compliance_sop

load_dotenv(project_root /".env")

# Creating agent state
# By using annotated, add_messages is understood as annotate
# list[BaseMessages] "The data type is a list of messages. However, when a node returns a new message, do not overwrite the old list. "
# "Instead, pass the old list and the new message into the add_messages function to append them together."
# If we didn't use Annotated and just wrote messages: list[BaseMessage], every time a node in graph returned a message, 
# LangGraph would completely overwrite the old list with the new message. We would lose the entire conversation history
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# ==========================================================
# 2. Factory Initialization: Agent Resoner LLM
# ==========================================================

AGENT_LLM_SETTINGS = os.getenv("Agent_llm")

if AGENT_LLM_SETTINGS == "OPENAI":
    print("🤖Brain Mode: Utilizing Cloud OpenAI Reasoner (gpt-4o)...")
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model = "gpt-4o", temperature = 0)

elif AGENT_LLM_SETTINGS == "DEEPSEEK":
    print("🐳 Brain Mode: Utilizing Flagship DeepSeek Cloud Reasoner (deeppseek-v4-flash)....")
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(
        model = "deepseek-v4-flash",
        temperature=0,
        openai_api_key=os.getenv("DEEPSEEk_API_KEY"),
        base_url="https://api.deepseek.com",
        max_tokens=2048
        #extra_body={"thinking":{"type":"enabled"}}
    )
else: # Fallback / Default Runner Mode
    print("🤗 Brain Mode: Local Fallback Activated. Binding Local Ollama(qwen2.5:7b).....")
    from langchain_community.chat_models import ChatOllama
    llm = ChatOllama(
        model="qwen2.5:7b",
        temperature=0,
        num_predict=1024
    )

fde_tools = [query_telemetry_db, fetch_corridor_conditions, search_compliance_sop]
llm_with_tools = llm.bind_tools(fde_tools)

# ===================================================================================
# 3. Graph Architecture Assembly
# ===================================================================================
def resoning_node(state: AgentState):
    response=llm_with_tools.invoke(state["messages"])
    return {"messages":[response]}

print("⚙️ Compiling LangGraph FDE Orchestrator...")
graph_builder = StateGraph(AgentState)
graph_builder.add_node("reasoner", resoning_node)
graph_builder.add_node("tools", ToolNode(fde_tools))
graph_builder.add_edge(START, "reasoner")
graph_builder.add_conditional_edges("reasoner", tools_condition)
graph_builder.add_edge("tools", "reasoner")

fde_agent = graph_builder.compile(checkpointer=MemorySaver())


# ==========================================
# 4. CHAT LOOP TESTING PANEL
# ==========================================
if __name__ == "__main__":
    print("\n" + "="*55)
    print("🚀 FDE Supply Chain Orchestrator State Machine Online")
    print(f"Configured Execution: [LLM: {AGENT_LLM_SETTINGS}] -> [Embeddings: {os.getenv('Embeddings_model', 'LOCAL')}]")
    print("="*55 + "\n")
    
    # Load the business-structured system prompt from the external file
    prompt_path = project_root / "src" / "prompts" / "system_prompt.txt"
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_instructions = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find {prompt_path}")
        system_instructions = "You are a helpful AI assistant." # Basic fallback

    system_prompt = SystemMessage(content=system_instructions)
    
    thread_config = {"configurable": {"thread_id": "production_test_1"}}
    fde_agent.invoke({"messages": [system_prompt]}, config=thread_config)
    
    while True:
        user_input = input("\nDispatcher > ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        events = fde_agent.stream({"messages": [("user", user_input)]}, config=thread_config, stream_mode="updates")
        for event in events:
            for node_name, node_state in event.items():
                if node_name == "tools":
                    print("   [System] 🔄 Retrieving external data elements via ToolNode...")
                elif node_name == "reasoner":
                    latest_msg = node_state["messages"][-1]
                    if latest_msg.content:
                        print(f"\n🤖 FDE Agent:\n{latest_msg.content}")

