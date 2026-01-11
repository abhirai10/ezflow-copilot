"""SQL Analyst Agent for database queries with stateful conversation history."""

import threading
from typing import Any

from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

from src.backend.services.sql_service import DatabaseManager
from src.backend.agents.prompts import SQL_ANALYST_AGENT_PROMPT


class SQLAnalystAgent:
    """
    Thread-safe singleton SQL analyst agent for database queries.
    
    Maintains a single shared agent instance across all users with per-session
    state isolation via thread_id. Each user gets their own conversation history
    without creating duplicate agents or tools.
    
    Attributes:
        _agent: Shared agent instance (class-level, created once)
        _memory: Shared memory checkpoint for conversation history (class-level)
        _lock: Threading lock for safe initialization
        _initialized: Flag to avoid redundant initialization checks
    """

    _agent = None
    _memory = None
    _lock = threading.Lock()
    _initialized = False

    def __init__(self, model: Any, system_prompt: str | None = None):
        """
        Initialize the SQL Analyst Agent (thread-safe singleton).
        
        The underlying agent is created only once, even if multiple threads
        call this constructor simultaneously. Each instance shares the same
        agent but maintains independent model references.
        
        Args:
            model: Language model instance (ChatOpenAI, init_chat_model, etc.)
            system_prompt: Optional custom system prompt. Defaults to SQL_ANALYST_AGENT_PROMPT.
        
        Raises:
            ValueError: If model is None.
        """
        if model is None:
            raise ValueError("model cannot be None")
        
        self.model = model
        self._system_prompt = system_prompt or SQL_ANALYST_AGENT_PROMPT
        self._ensure_agent_initialized()

    @classmethod
    def _ensure_agent_initialized(cls):
        """
        Thread-safe initialization of the shared agent.
        
        Only the first caller creates the agent; subsequent callers reuse it.
        Uses double-check pattern to minimize lock contention.
        """
        if cls._initialized:
            return
        
        with cls._lock:
            # Double-check: another thread may have initialized while waiting
            if cls._initialized:
                return
            
            cls._initialize_agent()
            cls._initialized = True
    
    @classmethod
    def _initialize_agent(cls):
        """Create the shared agent and memory (called once under lock)."""
        model = cls._get_model()
        tools = DatabaseManager.get_tools(model=model)
        cls._memory = MemorySaver()
        cls._agent = create_deep_agent(
            model=model,
            tools=tools,
            system_prompt=SQL_ANALYST_AGENT_PROMPT,
            checkpointer=cls._memory,
        )
    
    @classmethod
    def _get_model(cls):
        """
        Get a model instance for initialization.
        
        TODO: Store model at class level or retrieve from dependency container.
        """
        from langchain.chat_models import init_chat_model
        return init_chat_model(model="gpt-4o", temperature=0)

    def run(self, user_query: str, session_id: str) -> str:
        """
        Execute the agent with a user query (blocking).
        
        Conversation history is isolated per session_id, allowing multiple
        concurrent users without cross-contamination.
        
        Args:
            user_query: User's question or request.
            session_id: Unique session ID for conversation history isolation.
        
        Returns:
            Agent's text response.
        
        Raises:
            RuntimeError: If agent failed to initialize.
            ValueError: If user_query or session_id is empty.
        """
        self._validate_inputs(user_query, session_id)
        
        if self._agent is None:
            raise RuntimeError("Agent failed to initialize")
        
        config = {"configurable": {"thread_id": session_id}}
        
        try:
            response = self._agent.invoke(
                {"messages": [("user", user_query)]},
                config=config,
            )
            return response["messages"][-1].content
        except IndexError:
            raise RuntimeError("Agent returned unexpected response format")
        except Exception as e:
            raise RuntimeError(f"Agent execution failed: {str(e)}") from e

    async def arun(self, user_query: str, session_id: str) -> str:
        """
        Execute the agent asynchronously (non-blocking).
        
        Best for concurrent request handling in async frameworks (FastAPI, etc.).
        Uses thread pool to avoid blocking the event loop.
        
        Args:
            user_query: User's question or request.
            session_id: Unique session ID for conversation history isolation.
        
        Returns:
            Agent's text response.
        
        Raises:
            Same as run().
        """
        self._validate_inputs(user_query, session_id)
        
        if self._agent is None:
            raise RuntimeError("Agent failed to initialize")
        
        config = {"configurable": {"thread_id": session_id}}
        
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self._agent.invoke(
                    {"messages": [("user", user_query)]},
                    config=config,
                )
            )
            return response["messages"][-1].content
        except IndexError:
            raise RuntimeError("Agent returned unexpected response format")
        except Exception as e:
            raise RuntimeError(f"Async agent execution failed: {str(e)}") from e

    @staticmethod
    def _validate_inputs(user_query: str, session_id: str):
        """
        Validate user inputs.
        
        Raises:
            ValueError: If user_query or session_id is empty.
        """
        if not user_query or not user_query.strip():
            raise ValueError("user_query cannot be empty")
        if not session_id or not session_id.strip():
            raise ValueError("session_id cannot be empty")

