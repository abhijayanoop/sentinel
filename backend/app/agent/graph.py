from langgraph.graph import StateGraph, START, END
from app.agent.state import AgentState
from app.agent.nodes import plan_and_gather, synthesize_diagnosis


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("plan_and_gather", plan_and_gather)
    graph.add_node("synthesize_diagnosis", synthesize_diagnosis)

    graph.add_edge(START, "plan_and_gather")
    graph.add_edge("plan_and_gather", "synthesize_diagnosis")
    graph.add_edge("synthesize_diagnosis", END)

    return graph.compile()

agent_graph = build_graph()