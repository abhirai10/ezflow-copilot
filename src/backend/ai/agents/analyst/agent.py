from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver 
from deepagents import create_deep_agent
from src.backend.core.config import settings
from src.backend.ai.prompts.sql_analyst import SQL_ANALYST_AGENT_INSTRUCTION

class SQLAnalystAgent:
    _instance = None  # Class-level variable to store the single instance

    def __new__(cls):
        # If an instance doesn't exist yet, create it
        if cls._instance is None:
            cls._instance = super(SQLAnalystAgent, cls).__new__(cls)
            # Initialize the private components only once
            cls._instance.__initialize_agent()
        return cls._instance

    def __initialize_agent(self):
        """Private initialization logic"""

        model_name="nvidia/nemotron-3-nano-30b-a3b:free"
        model_provider= "openai"
        base_url= "https://openrouter.ai/api/v1"
        api_key=settings.model_api_key.get_secret_value()


        model = init_chat_model(
            model=model_name,
            model_provider=model_provider,
            base_url=base_url,
            api_key=api_key,
        )

        self.agent = create_deep_agent(
            model=model,
            tools=[],
            system_prompt=SQL_ANALYST_AGENT_INSTRUCTION,
            #checkpointer=InMemorySaver(),  Checkpointer requires one or more of the following 'configurable' keys: thread_id, checkpoint_ns, checkpoint_id
        )

        print("🚀 Gemini Agent Initialized (This only happens ONCE)")

    async def get_response(self, user_input: str) -> str:
        response = await self.agent.ainvoke( {"messages": [{"role": "user", "content": user_input}]})
        return response['messages'][-1].content

# Use this everywhere
shared_agent = SQLAnalystAgent()
