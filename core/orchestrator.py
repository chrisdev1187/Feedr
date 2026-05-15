"""
Core orchestration logic for Spoon Feedr using LangGraph.
Handles intent parsing, planning, research, execution, and verification.
"""

from typing import Annotated, List, Union, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import json
import re

# Import components
try:
    from vibe_launcher import CloudLLM, parse_intent as original_parse_intent
except ImportError:
    class CloudLLM:
        def chat(self, messages, **kwargs): return "Mock Response"
    def original_parse_intent(input_str): return {"mode": "app"}

from core.memory import MemoryEngine, memory_agent_node
from core.monitor import ProactiveResearcher
from core.tools import ToolDelegator
from core.coderabbit import CodeRabbit

class SpoonFeedrState(TypedDict):
    """The state of the Spoon Feedr orchestrator."""
    messages: Annotated[List[BaseMessage], add_messages]
    intent: Dict[str, Any]
    plan: List[str]
    current_step: int
    context: Dict[str, Any]
    suggestions: List[str]
    next_action: str

def intent_parser_node(state: SpoonFeedrState):
    """Parses the user's intent from the last message."""
    user_msg = state["messages"][-1].content
    intent = original_parse_intent(user_msg)
    return {"intent": intent}

def planner_node(state: SpoonFeedrState):
    """Creates a spoon-feeding plan based on the parsed intent."""
    intent = state.get("intent", {})
    mode = intent.get("mode", "app")

    # Only set plan if it hasn't been set yet
    if "plan" in state and state["plan"]:
        return {}

    if mode == "research":
        plan = ["research", "memory_update"]
    elif mode == "app" or mode == "coding_task":
        plan = ["research", "generate", "test", "memory_update"]
    else:
        plan = ["generate", "memory_update"]

    return {"plan": plan, "current_step": 0}

def researcher_node(state: SpoonFeedrState):
    """Performs GitHub research to find relevant patterns or tools."""
    engine = MemoryEngine()
    researcher = ProactiveResearcher(engine)
    last_msg = state["messages"][-1].content

    results = researcher.research_github(last_msg)
    new_context = {**state.get("context", {}), "research": f"Found {len(results)} relevant repos on GitHub."}
    return {
        "context": new_context,
        "current_step": state["current_step"] + 1
    }

def executor_node(state: SpoonFeedrState):
    """Delegates the core task to specialized CLI tools like Aider or Jules."""
    intent = state.get("intent", {})
    last_msg = state["messages"][-1].content

    if intent.get("complexity") == "complex":
        res = ToolDelegator.run_jules(last_msg)
        execution_msg = f"Jules: {res.get('stdout', res.get('error'))}"
    else:
        res = ToolDelegator.run_aider(last_msg)
        execution_msg = f"Aider: {res.get('stdout', res.get('error'))}"

    new_context = {**state.get("context", {}), "execution": execution_msg}
    return {"context": new_context, "current_step": state["current_step"] + 1}

def verifier_node(state: SpoonFeedrState):
    """Verifies the execution results by running tests and Code Rabbit review."""
    # 1. Proactively run tests
    res = ToolDelegator._run_command(["pytest"])
    test_status = "Passed" if res["success"] else "Failed"

    # 2. Run Code Rabbit review on changed files (placeholder: review all)
    rabbit = CodeRabbit()
    findings = rabbit.review_project()
    rabbit_status = f"Code Rabbit found {sum(len(f) for f in findings.values())} potential issues."

    new_context = {
        **state.get("context", {}),
        "verification": f"Tests {test_status}. {rabbit_status}"
    }
    return {
        "context": new_context,
        "current_step": state["current_step"] + 1
    }

def memory_agent_wrap_node(state: SpoonFeedrState):
    """Wrapper for the memory agent to persist project knowledge."""
    return memory_agent_node(state)

def router(state: SpoonFeedrState):
    """Decides the next node to execute based on the plan and current step."""
    plan = state.get("plan", [])
    step_idx = state.get("current_step", 0)

    if step_idx < len(plan):
        next_step = plan[step_idx]
        if next_step == "research":
            return "researcher"
        elif next_step == "generate":
            return "executor"
        elif next_step == "test":
            return "verifier"
        elif next_step == "memory_update":
            return "memory_agent"
    return END

def create_spoon_feedr_graph():
    """Compiles the Spoon Feedr LangGraph workflow."""
    workflow = StateGraph(SpoonFeedrState)

    workflow.add_node("intent_parser", intent_parser_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("verifier", verifier_node)
    workflow.add_node("memory_agent", memory_agent_wrap_node)

    workflow.set_entry_point("intent_parser")
    workflow.add_edge("intent_parser", "planner")

    workflow.add_conditional_edges(
        "planner",
        router,
        {
            "researcher": "researcher",
            "executor": "executor",
            "verifier": "verifier",
            "memory_agent": "memory_agent",
            END: END
        }
    )

    workflow.add_edge("researcher", "planner")
    workflow.add_edge("executor", "planner")
    workflow.add_edge("verifier", "planner")
    workflow.add_edge("memory_agent", "planner")

    return workflow.compile()

if __name__ == "__main__":
    app = create_spoon_feedr_graph()
    initial_state = {
        "messages": [HumanMessage(content="Build a simple flask app")],
        "current_step": 0
    }
    for event in app.stream(initial_state):
        print(event)
