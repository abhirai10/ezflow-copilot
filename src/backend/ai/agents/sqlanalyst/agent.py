from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver 
from langchain.agents.middleware import PIIMiddleware, HumanInTheLoopMiddleware, ModelCallLimitMiddleware, ContextEditingMiddleware, ClearToolUsesEdit
from langgraph.checkpoint.memory import InMemorySaver 
from deepagents import create_deep_agent
from src.backend.ai.middleware.contentfilter_guardrail import ContentFilterMiddleware
from src.backend.ai.middleware.delete_old_memory import delete_old_messages
from src.backend.ai.middleware.safety_guardrail import SafetyGuardrailMiddleware
from src.backend.core.config import settings
from src.backend.ai.prompts.sql_analyst import CONTENT_FILTER_LIST, SQL_ANALYST_AGENT_INSTRUCTION
from src.backend.ai.state.customer_state import CustomAgentState

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
            #max_tokens=500 
        )

        self.agent = create_deep_agent(
            model=model,
            tools=[],
            system_prompt=SQL_ANALYST_AGENT_INSTRUCTION,
            middleware=[
                ContentFilterMiddleware(banned_keywords=CONTENT_FILTER_LIST),

                ModelCallLimitMiddleware(
                    run_limit=5,
                    exit_behavior="end",
                ),

                ContextEditingMiddleware(
                    edits=[
                        ClearToolUsesEdit(
                            trigger=100000,
                            keep=3,
                        ),
                    ],
                ),

                PIIMiddleware(
                    "credit_card",
                    strategy="mask",
                    apply_to_input=True,
                ),
                PIIMiddleware(
                    "api_key",
                    detector=r"sk-[a-zA-Z0-9]{32}",
                    strategy="block",
                    apply_to_input=True,
                ),

                delete_old_messages
                #HumanInTheLoopMiddleware(interrupt_on={"delete_database": True}),

                # SafetyGuardrailMiddleware(),
            ],
            context_schema=CustomAgentState, 
            checkpointer=InMemorySaver(),  
            )

        print("SQL Agent initialized")

    async def get_response(self, user_input: str, user_id: str) -> str:
        response = await self.agent.ainvoke( 
            {
                "messages": [{"role": "user", "content": user_input}],
                "user_id": user_id
            },
            {"configurable": {"thread_id": user_id}},  
            )
        return response['messages'][-1].content

# Use this everywhere
shared_agent = SQLAnalystAgent()
