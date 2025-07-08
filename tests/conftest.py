import sys
from unittest.mock import MagicMock

import pytest


# Mock the agno module and its imports
class MockAgent:
    pass


class MockMemory:
    pass


class MockModel:
    pass


class MockStorageAgent:
    pass


class MockTools:
    pass


# Set up mock modules
sys.modules["agno"] = MagicMock()
sys.modules["agno.agent"] = MagicMock()
sys.modules["agno.agent"].Agent = MockAgent
sys.modules["agno.memory"] = MagicMock()
sys.modules["agno.memory.v2"] = MagicMock()
sys.modules["agno.memory.v2.memory"] = MagicMock()
sys.modules["agno.memory.v2.memory"].Memory = MockMemory
sys.modules["agno.memory.v2.db"] = MagicMock()
sys.modules["agno.memory.v2.db.postgres"] = MagicMock()
sys.modules["agno.memory.v2.db.postgres"].PostgresMemoryDb = MagicMock()
sys.modules["agno.models"] = MagicMock()
sys.modules["agno.models.google"] = MagicMock()
sys.modules["agno.models.google"].GoogleGenAIChat = MockModel
sys.modules["agno.storage"] = MagicMock()
sys.modules["agno.storage.agent"] = MagicMock()
sys.modules["agno.storage.agent.postgres"] = MagicMock()
sys.modules["agno.storage.agent.postgres"].PostgresAgentStorage = MockStorageAgent
sys.modules["agno.tools"] = MagicMock()
sys.modules["agno.tools.duckduckgo"] = MagicMock()
sys.modules["agno.tools.duckduckgo"].DuckDuckGoTools = MockTools

# Mock app
sys.modules["app"] = MagicMock()
sys.modules["app.main"] = MagicMock()
sys.modules["app.main"].app = MagicMock()


@pytest.fixture
def mock_agent():
    return MockAgent()
