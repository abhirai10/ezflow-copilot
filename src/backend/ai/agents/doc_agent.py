from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from src.backend.ai.prompts.prompt import DOCUMENT_ANALYST_AGENT_PROMPT
from src.backend.ai.tools.retrieve_context_tool import retrieve_context_tool
from src.backend.core.config import settings

class DocAnalystAgent:
    _instance = None  # Class-level variable to store the single instance

    def __new__(cls):
        # If an instance doesn't exist yet, create it
        if cls._instance is None:
            cls._instance = super(DocAnalystAgent, cls).__new__(cls)
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
            #max_tokens=500 
        )

        self.agent = create_agent(
            model=model,
            tools=[retrieve_context_tool],
            system_prompt=DOCUMENT_ANALYST_AGENT_PROMPT
        )

        print("Document RAG Agent initialized")

    async def get_response(self, user_input: str, user_id: str) -> str:
        response = await self.agent.ainvoke( 
            {
                "messages": [{"role": "user", "content": user_input}]
            },
            )
        return response['messages'][-1].content

# Use this everywhere
doc_analyst_agent = DocAnalystAgent()
