from langchain.agents import AgentState

class CustomAgentState(AgentState):  
    user_id: str