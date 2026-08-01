from langgraph.graph import StateGraph, START, END

from app.agent.state import AgentState
from app.agent.nodes import (
    plan_and_gather, synthesize_diagnosis,
    draft_action_and_request_approval, escalate_high_risk, route_on_risk,
)


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("plan_and_gather", plan_and_gather)
    graph.add_node("synthesize_diagnosis", synthesize_diagnosis)
    graph.add_node("draft_action_and_request_approval", draft_action_and_request_approval)
    graph.add_node("escalate_high_risk", escalate_high_risk)

    graph.add_edge(START, "plan_and_gather")
    graph.add_edge("plan_and_gather", "synthesize_diagnosis")

    graph.add_conditional_edges(
        "synthesize_diagnosis",
        route_on_risk,
        {
            "draft_action_and_request_approval": "draft_action_and_request_approval",
            "escalate_high_risk": "escalate_high_risk",
        },
    )

    graph.add_edge("draft_action_and_request_approval", END)
    graph.add_edge("escalate_high_risk", END)

    return graph.compile()


agent_graph = build_graph()