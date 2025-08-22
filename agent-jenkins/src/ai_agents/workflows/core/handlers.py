"""Common LangGraph node handler implementations."""


def start_node(state, model=None, tools=None, memory=None, node_type=None, **kwargs):
    """Handle the start node in the core workflow."""
    query = state.get("query", "What is LangGraph?")
    return {"query": query, "next_node": "search"}


def search_knowledge(
    state, model=None, tools=None, memory=None, node_type=None, **kwargs
):
    """Handle the search knowledge node in the core workflow."""
    query = state["query"]
    knowledge = {
        "LangGraph": "LangGraph is a library for building stateful agents using graphs.",
        "RAG": "Retrieval-Augmented Generation helps enhance LLM answers using documents.",
    }
    results = [v for k, v in knowledge.items() if k.lower() in query.lower()]
    return {**state, "results": results, "next_node": "summarize"}


def summarize_results(
    state, model=None, tools=None, memory=None, node_type=None, **kwargs
):
    """Handle the summarize results node in the core workflow."""
    results = state.get("results", [])
    summary = " ".join(results) if results else "No relevant info found."
    return {**state, "summary": summary, "next_node": "end"}


def end_node(state, model=None, tools=None, memory=None, node_type=None, **kwargs):
    """Handle the end node in the core workflow."""
    return {
        "final_answer": state.get("summary", "No summary generated."),
        "status": "complete",
    }
