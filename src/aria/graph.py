"""
LangGraph Topology Compilation for ARIA Agent.
Provides native LangGraph integration with self-contained fallback for local testing.
"""

from typing import Dict, Any, Literal, Optional, Callable

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    END = "__END__"

    class SimpleCompiledGraph:
        """Lightweight runtime fallback for local environments without external langgraph package."""
        def __init__(self, nodes: Dict[str, Callable], edges: Dict[str, str], conditional_edges: Dict[str, Any], entry_point: str):
            self.nodes = nodes
            self.edges = edges
            self.conditional_edges = conditional_edges
            self.entry_point = entry_point

        def invoke(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
            current_node = self.entry_point
            state = dict(initial_state)
            visited_count = 0
            max_hops = 100

            while current_node != END and visited_count < max_hops:
                visited_count += 1
                node_func = self.nodes.get(current_node)
                if not node_func:
                    break
                state = node_func(state)

                if current_node in self.conditional_edges:
                    routing_func, path_map = self.conditional_edges[current_node]
                    decision = routing_func(state)
                    target = path_map.get(decision, END)
                    current_node = target
                elif current_node in self.edges:
                    current_node = self.edges[current_node]
                else:
                    break

            return state

    class StateGraph:  # type: ignore
        """Drop-in interface compatible with langgraph.graph.StateGraph."""
        def __init__(self, state_schema: Any):
            self.state_schema = state_schema
            self.nodes: Dict[str, Callable] = {}
            self.edges: Dict[str, str] = {}
            self.conditional_edges: Dict[str, Any] = {}
            self.entry_point: Optional[str] = None

        def add_node(self, name: str, func: Callable):
            self.nodes[name] = func

        def set_entry_point(self, name: str):
            self.entry_point = name

        def add_edge(self, start: str, end: str):
            self.edges[start] = end

        def add_conditional_edges(self, start: str, routing_func: Callable, path_map: Dict[str, str]):
            self.conditional_edges[start] = (routing_func, path_map)

        def compile(self, checkpointer: Any = None) -> SimpleCompiledGraph:
            return SimpleCompiledGraph(self.nodes, self.edges, self.conditional_edges, self.entry_point or "intake")


from aria.state import AgentState
from aria.nodes import NodeRegistry


def route_after_execute(state: AgentState) -> Literal["human_gate", "checkpoint", "observe"]:
    if state.get("human_approval_required"):
        return "human_gate"
    if state.get("checkpoint_and_pause"):
        return "checkpoint"
    return "observe"


def route_after_reflect(state: AgentState) -> Literal["complete", "checkpoint", "execute"]:
    if state.get("completion_status") == "completed":
        return "complete"
    if state.get("checkpoint_and_pause"):
        return "checkpoint"
    plan = state.get("plan", [])
    if state.get("current_step_idx", 0) < len(plan):
        return "execute"
    return "complete"


def build_aria_graph(registry: NodeRegistry | None = None) -> Any:
    """Builds and compiles the complete LangGraph workflow."""
    reg = registry or NodeRegistry()

    workflow = StateGraph(AgentState)

    # Register Nodes
    workflow.add_node("intake", reg.intake_task_node)
    workflow.add_node("plan", reg.planner_node)
    workflow.add_node("execute", reg.executor_node)
    workflow.add_node("human_gate", reg.human_approval_node)
    workflow.add_node("observe", reg.observation_node)
    workflow.add_node("reflect", reg.reflection_node)
    workflow.add_node("checkpoint", reg.checkpoint_node)
    workflow.add_node("complete", reg.completion_node)

    # Set Entry Point
    workflow.set_entry_point("intake")

    # Transitions
    workflow.add_edge("intake", "plan")
    workflow.add_edge("plan", "execute")

    workflow.add_conditional_edges(
        "execute",
        route_after_execute,
        {
            "human_gate": "human_gate",
            "checkpoint": "checkpoint",
            "observe": "observe"
        }
    )

    workflow.add_edge("human_gate", "checkpoint")
    workflow.add_edge("observe", "reflect")

    workflow.add_conditional_edges(
        "reflect",
        route_after_reflect,
        {
            "execute": "execute",
            "checkpoint": "checkpoint",
            "complete": "complete"
        }
    )

    workflow.add_edge("checkpoint", END)
    workflow.add_edge("complete", "checkpoint")

    return workflow.compile()
