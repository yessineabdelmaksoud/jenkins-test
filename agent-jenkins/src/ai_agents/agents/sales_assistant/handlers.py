def query_database(
    state, model=None, tools=None, memory=None, node_type=None, **kwargs
):
    """
    Queries the database and returns the next action.

    Args:
        state: The current state or context for the query.
        model (optional): The model to use for querying, if applicable.
        tools (optional): Additional tools or resources for the query.
        memory (optional): Memory or context to use during the query.
        node_type (optional): The type of node involved in the query.
        **kwargs: Additional keyword arguments.

    Returns:
        dict: A dictionary indicating the next action, e.g., {"next": "summarize"}.
    """
    print("Querying database...")
    # Use DeepSeek R1 model via OpenRouter
    from openai import OpenAI
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
    )
    customer_query = state.get("customer_query", "What is the meaning of life?")
    completion = client.chat.completions.create(
        extra_body={},
        model="deepseek/deepseek-r1-0528:free",
        messages=[
            {
                "role": "user",
                "content": customer_query
            }
        ]
    )
    db_result = completion.choices[0].message.content
    print(f"LLM result: {db_result}")
    return {**state, "db_result": db_result, "next": "decide"}


def summarize_answer(
    state, model=None, tools=None, memory=None, node_type=None, **kwargs
):
    """
    Summarizes the answer based on the current state and optional parameters.

    Args:
        state (dict): The current state containing relevant information for summarization.
        model (optional): The model to use for summarization.
        tools (optional): Additional tools that may assist in summarization.
        memory (optional): Memory object for context retention.
        node_type (optional): The type of node being processed.
        **kwargs: Additional keyword arguments.

    Returns:
        dict: A dictionary indicating the next step in the process.
    """
    print("Summarizing answer...")
    from openai import OpenAI
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
    )
    db_result = state.get("db_result", "No result found.")
    completion = client.chat.completions.create(
        extra_body={},
        model="deepseek/deepseek-r1-0528:free",
        messages=[
            {
                "role": "user",
                "content": f"Summarize this result for a customer: {db_result}"
            }
        ]
    )
    summary = completion.choices[0].message.content
    print(f"Summary: {summary}")
    return {**state, "summary": summary, "next": "finish"}


def handle_error(state, model=None, tools=None, memory=None, node_type=None, **kwargs):
    """
    Handles errors encountered during the agent's execution.

    Args:
        state (dict): The current state of the agent.
        model (optional): The model being used by the agent.
        tools (optional): Tools available to the agent.
        memory (optional): Memory or context for the agent.
        node_type (optional): The type of node where the error occurred.
        **kwargs: Additional keyword arguments.

    Returns:
        dict: A dictionary indicating the next step, typically ending the process.
    """
    print("Handling error...")
    return {"next": "END"}


def start_node_prompt(state, prompt_template):
    """
    Constructs a prompt for the start node in a sales assistant workflow.

    This function uses a provided prompt template and the current state to generate a customized prompt.
    It utilizes the `render_prompt` utility to fill the template with state information, and then
    prepends a "[SALES PROMPT]" tag to the result.

    Args:
        state (dict): The current state containing context or variables for prompt rendering.
        prompt_template (str): The template string to be rendered with state information.

    Returns:
        str: The constructed sales prompt string.
    """
    # Example: use the template as a base, then add extra info
    from ai_agents.workflows.utils.prompts_utils import render_prompt

    base_prompt = render_prompt(prompt_template, state) if prompt_template else ""
    return f"[SALES PROMPT] {base_prompt}"
 