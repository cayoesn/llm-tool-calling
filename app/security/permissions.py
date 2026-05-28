from typing import List, Set, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    def __init__(self, max_calls_per_session: int = 10):
        self._blocked_tools: Set[str] = set()
        self._allowed_categories: Set[str] = {"utility", "information", "file_system", "database", "general"}
        self._max_calls_per_session = max_calls_per_session
        self._session_calls: Dict[str, int] = {}

    def block_tool(self, tool_name: str):
        self._blocked_tools.add(tool_name)

    def is_tool_allowed(self, tool_name: str, category: str, session_id: Optional[str] = None) -> bool:
        if tool_name in self._blocked_tools:
            logger.warning(f"Tool {tool_name} is blocked")
            return False
        
        if category not in self._allowed_categories:
            logger.warning(f"Category {category} is not allowed")
            return False

        if session_id:
            count = self._session_calls.get(session_id, 0)
            if count >= self._max_calls_per_session:
                logger.warning(f"Session {session_id} exceeded max tool calls ({self._max_calls_per_session})")
                return False
            self._session_calls[session_id] = count + 1

        return True

    def reset_session(self, session_id: str):
        if session_id in self._session_calls:
            del self._session_calls[session_id]

security_manager = SecurityManager()
