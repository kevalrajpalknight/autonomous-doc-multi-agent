from langgraph.graph import END, StateGraph

from .nodes import cloner_node, manager_node, summarizer_node, writer_node
from .state import AgentState


def create_graph():
    workflow = StateGraph(AgentState)

    # Nodes
    workflow.add_node("cloner", cloner_node)
    workflow.add_node("manager", manager_node)
    workflow.add_node("summarizer", summarizer_node)
    workflow.add_node("writer", writer_node)

    # Edges
    workflow.set_entry_point("cloner")
    workflow.add_edge("cloner", "manager")

    # The summarizer node will iterate over selected_files itself.
    workflow.add_edge("manager", "summarizer")

    # Fan-in occurs within summarizer by returning a list of summaries
    workflow.add_edge("summarizer", "writer")
    workflow.add_edge("writer", END)

    return workflow.compile()


# Initialize the runnable graph
app_graph = create_graph()
