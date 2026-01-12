from langchain.messages import RemoveMessage
from langchain.agents import AgentState
from langchain.agents.middleware import after_model
from langgraph.runtime import Runtime


# Production use a store to save memory
@after_model
def delete_old_messages(state: AgentState, runtime: Runtime) -> dict | None:
    """Remove old messages to keep conversation manageable."""
    messages = state["messages"]
    if len(messages) > 10:
        # remove the earliest two messages
        return {"messages": [RemoveMessage(id=m.id) for m in messages[:2]]}
    return None