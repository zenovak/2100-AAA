import unittest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock

# Import the API components
from agent_integration_api import (
    AgentAPI, BaseAgent, AgentType, 
    agent_api, TextProcessorAgent, urfn_summarize_text
)


class TestAgentAPI(unittest.TestCase):
    """Test cases for the main AgentAPI class"""
    
    def setUp(self):
        """Set up test environment before each test"""
        # Create a temporary registry file for testing
        self.temp_registry = tempfile.NamedTemporaryFile(delete=False)
        self.temp_registry.write(b'{}')
        self.temp_registry.close()
        
        # Patch the registry file path
        self.registry_patcher = patch('agent_integration_api.AgentAPI._load_registry')
        self.mock_load_registry = self.registry_patcher.start()
        
        # Create a fresh API instance for each test
        self.api = AgentAPI()
        self.api.urfn_registry = {}
        self.api.registered_agents = {}
        self.api.api_augmentations = {}
    
    def tearDown(self):
        """Clean up after each test"""
        self.registry_patcher.stop()
        if os.path.exists(self.temp_registry.name):
            os.unlink(self.temp_registry.name)
    
    def test_register_agent(self):
        """Test agent registration functionality"""
        # Define a test agent class
        @self.api.register_agent(
            agent_name="test_agent",
            agent_type=AgentType.TASK,
            description="Test agent for unit tests"
        )
        class TestAgent(BaseAgent):
            def run(self, input_data):
                return {"result": "test"}
        
        # Check if agent was registered correctly
        self.assertIn("test_agent", self.api.registered_agents)
        self.assertEqual(self.api.registered_agents["test_agent"]["type"], AgentType.TASK)
        self.assertEqual(self.api.registered_agents["test_agent"]["description"], "Test agent for unit tests")
        
        # Test registering duplicate agent
        with self.assertRaises(ValueError):
            @self.api.register_agent(
                agent_name="test_agent",
                agent_type=AgentType.CONVERSATION,
                description="Duplicate agent"
            )
            class DuplicateAgent(BaseAgent):
                def run(self, input_data):
                    return {"result": "duplicate"}
    
    def test_register_function(self):
        """Test function registration functionality"""
        # Register a test function
        @self.api.register_function(
            function_name="urfn_test_function",
            description="Test function for unit tests"
        )
        def test_function(param1: str, param2: int = 0):
            return {"result": param1, "count": param2}
        
        # Check if function was registered correctly
        self.assertIn("urfn_test_function", self.api.urfn_registry)
        func_info = self.api.urfn_registry["urfn_test_function"]
        self.assertEqual(func_info["description"], "Test function for unit tests")
        self.assertEqual(func_info["function"], "test_function")
        
        # Check parameter info
        self.assertIn("param1", func_info["parameters"])
        self.assertIn("param2", func_info["parameters"])
        self.assertTrue(func_info["parameters"]["param1"]["required"])
        self.assertFalse(func_info["parameters"]["param2"]["required"])
        
        # Test invalid function name
        with self.assertRaises(ValueError):
            @self.api.register_function(
                function_name="invalid_function_name",
                description="Function with invalid name"
            )
            def invalid_function():
                pass
    
    def test_augment_api(self):
        """Test API augmentation functionality"""
        # Register a test endpoint
        @self.api.augment_api(endpoint="/test/endpoint")
        def test_endpoint(data):
            return {"status": "success", "data": data}
        
        # Check if endpoint was registered correctly
        self.assertIn("/test/endpoint", self.api.api_augmentations)
        self.assertEqual(self.api.api_augmentations["/test/endpoint"]["method"], "POST")
        
        # Test duplicate endpoint
        with self.assertRaises(ValueError):
            @self.api.augment_api(endpoint="/test/endpoint", method="GET")
            def duplicate_endpoint(data):
                return {"status": "duplicate"}
    
    def test_execute_function(self):
        """Test function execution"""
        # Register a test function
        @self.api.register_function(
            function_name="urfn_multiply",
            description="Multiplies two numbers"
        )
        def multiply(a: int, b: int):
            return {"result": a * b}
        
        # Execute the function
        result = self.api.execute_function("urfn_multiply", a=5, b=3)
        self.assertEqual(result["result"], 15)
        
        # Test non-existent function
        with self.assertRaises(ValueError):
            self.api.execute_function("urfn_nonexistent")
    
    def test_list_agents(self):
        """Test listing registered agents"""
        # Register test agents
        @self.api.register_agent(
            agent_name="test_agent1",
            agent_type=AgentType.TASK,
            description="Test agent 1"
        )
        class TestAgent1(BaseAgent):
            def run(self, input_data):
                return {"result": "test1"}
        
        @self.api.register_agent(
            agent_name="test_agent2",
            agent_type=AgentType.CONVERSATION,
            description="Test agent 2"
        )
        class TestAgent2(BaseAgent):
            def run(self, input_data):
                return {"result": "test2"}
        
        # Get agent list
        agents = self.api.list_agents()
        self.assertEqual(len(agents), 2)
        self.assertIn("test_agent1", agents)
        self.assertIn("test_agent2", agents)
        self.assertEqual(agents["test_agent1"]["type"], AgentType.TASK.value)
        self.assertEqual(agents["test_agent2"]["description"], "Test agent 2")
    
    def test_list_functions(self):
        """Test listing registered functions"""
        # Register test functions
        @self.api.register_function(
            function_name="urfn_func1",
            description="Test function 1"
        )
        def func1(param1: str):
            return {"result": param1}
        
        @self.api.register_function(
            function_name="urfn_func2",
            description="Test function 2"
        )
        def func2(param1: int, param2: int):
            return {"result": param1 + param2}
        
        # Get function list
        functions = self.api.list_functions()
        self.assertEqual(len(functions), 2)
        self.assertIn("urfn_func1", functions)
        self.assertIn("urfn_func2", functions)


class TestBaseAgent(unittest.TestCase):
    """Test cases for the BaseAgent class"""
    
    def setUp(self):
        """Set up test environment before each test"""
        # Create API instance
        self.api = AgentAPI()
        self.api.urfn_registry = {}
        self.api.registered_agents = {}
        
        # Register a test agent
        @self.api.register_agent(
            agent_name="test_agent",
            agent_type=AgentType.TASK,
            description="Test agent"
        )
        class TestAgent(BaseAgent):
            def __init__(self):
                super().__init__("test_agent")
            
            def run(self, input_data):
                return {"result": input_data.get("text", "")}
        
        self.TestAgent = TestAgent
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        # Create agent instance
        agent = self.TestAgent()
        self.assertEqual(agent.name, "test_agent")
        
        # Test invalid agent name
        with self.assertRaises(ValueError):
            class InvalidAgent(BaseAgent):
                def __init__(self):
                    super().__init__("nonexistent_agent")
                
                def run(self, input_data):
                    pass
            
            invalid_agent = InvalidAgent()
    
    def test_agent_run(self):
        """Test agent run method"""
        # Create agent instance
        agent = self.TestAgent()
        
        # Run agent
        result = agent.run({"text": "test input"})
        self.assertEqual(result["result"], "test input")
    
    def test_call_function(self):
        """Test agent calling functions"""
        # Register a test function
        @self.api.register_function(
            function_name="urfn_reverse",
            description="Reverses input text"
        )
        def reverse(text: str):
            return {"reversed": text[::-1]}
        
        # Create a subclass that uses the function
        class FunctionCallingAgent(BaseAgent):
            def __init__(self):
                super().__init__("test_agent")
            
            def run(self, input_data):
                text = input_data.get("text", "")
                return self.call_function("urfn_reverse", text=text)
        
        # Create agent instance
        agent = FunctionCallingAgent()
        
        # Mock execute_function to avoid actual function lookup
        self.api.execute_function = MagicMock(return_value={"reversed": "tset"})
        
        # Set global instance to our test instance
        import agent_integration_api
        agent_integration_api.agent_api = self.api
        
        # Run agent
        result = agent.run({"text": "test"})
        self.api.execute_function.assert_called_once_with("urfn_reverse", text="test")
        self.assertEqual(result["reversed"], "tset")


class TestTextProcessorAgent(unittest.TestCase):
    """Test cases for the sample TextProcessorAgent"""
    
    def setUp(self):
        """Set up test environment before each test"""
        # Mock API instance
        self.api = AgentAPI()
        self.api.urfn_registry = {
            "urfn_summarize_text": {
                "description": "Summarizes text",
                "module": "agent_integration_api",
                "function": "urfn_summarize_text"
            },
            "urfn_analyze_text": {
                "description": "Analyzes text",
                "module": "agent_integration_api",
                "function": "urfn_analyze_text"
            }
        }
        self.api.registered_agents = {
            "text_processor": {
                "type": AgentType.TASK,
                "description": "Text processor agent",
                "functions": {}
            }
        }
        
        # Set global instance to our test instance
        import agent_integration_api
        agent_integration_api.agent_api = self.api
        
        # Create agent instance
        self.agent = TextProcessorAgent()
    
    def test_summarize_operation(self):
        """Test summarize operation"""
        # Mock execute_function
        self.api.execute_function = MagicMock(return_value={"summary": "Summarized text"})
        
        # Run agent with summarize operation
        result = self.agent.run({
            "text": "This is a test text",
            "operation": "summarize"
        })
        
        # Check execute_function call
        self.api.execute_function.assert_called_once_with(
            "urfn_summarize_text", 
            input_text="This is a test text"
        )
        self.assertEqual(result["summary"], "Summarized text")
    
    def test_analyze_operation(self):
        """Test analyze operation"""
        # Mock execute_function
        self.api.execute_function = MagicMock(return_value={"sentiment": "positive"})
        
        # Run agent with analyze operation
        result = self.agent.run({
            "text": "This is a test text",
            "operation": "analyze"
        })
        
        # Check execute_function call
        self.api.execute_function.assert_called_once_with(
            "urfn_analyze_text", 
            input_text="This is a test text"
        )
        self.assertEqual(result["sentiment"], "positive")
    
    def test_unknown_operation(self):
        """Test unknown operation"""
        # Run agent with unknown operation
        result = self.agent.run({
            "text": "This is a test text",
            "operation": "unknown"
        })
        
        # Check error response
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Unknown operation: unknown")


class TestURFNFunctions(unittest.TestCase):
    """Test cases for URFN functions"""
    
    def test_summarize_text(self):
        """Test urfn_summarize_text function"""
        # Test with short text
        short_text = "This is a short text"
        result = urfn_summarize_text(input_text=short_text)
        self.assertEqual(result["summary"], short_text)
        
        # Test with long text
        long_text = "This is a very long text that should be summarized by the function. " * 10
        result = urfn_summarize_text(input_text=long_text)
        self.assertLess(len(result["summary"]), len(long_text))
        self.assertTrue(result["summary"].endswith("..."))


class TestIntegration(unittest.TestCase):
    """Integration tests for the Agent API"""
    
    def test_full_workflow(self):
        """Test full workflow from registration to execution"""
        # Create a fresh API instance
        api = AgentAPI()
        api.urfn_registry = {}
        api.registered_agents = {}
        api.api_augmentations = {}
        
        # Register a function
        @api.register_function(
            function_name="urfn_count_words",
            description="Counts words in text"
        )
        def count_words(text: str):
            return {"count": len(text.split())}
        
        # Register an agent
        @api.register_agent(
            agent_name="word_counter",
            agent_type=AgentType.TASK,
            description="Counts words in text"
        )
        class WordCounterAgent(BaseAgent):
            def __init__(self):
                super().__init__("word_counter")
            
            def run(self, input_data):
                text = input_data.get("text", "")
                return self.call_function("urfn_count_words", text=text)
        
        # Register an API endpoint
        @api.augment_api(endpoint="/v1/count-words")
        def count_words_endpoint(data):
            agent = WordCounterAgent()
            return agent.run(data)
        
        # Set global instance
        import agent_integration_api
        agent_integration_api.agent_api = api
        
        # Create agent and run
        agent = WordCounterAgent()
        result = agent.run({"text": "This is a test sentence with seven words"})
        
        # Check result
        self.assertEqual(result["count"], 7)
        
        # Check API documentation
        docs = api.get_api_documentation()
        self.assertIn("/v1/count-words", docs)


if __name__ == "__main__":
    unittest.main()
