"""
Client-side wrapper for FastMCP to run logic before making MCP calls.

This demonstrates how to add pre-processing logic on the client side
before sending requests to the MCP server.
"""
from typing import Any, Dict, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class MCPClientWrapper:
    """
    Wrapper around MCP client calls that allows running custom logic
    before the actual MCP call is made.
    
    Usage:
        wrapper = MCPClientWrapper()
        
        # Add custom pre-call logic
        @wrapper.before_tool_call
        def my_pre_logic(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
            print(f"About to call {tool_name}")
            # Modify arguments if needed
            return arguments
        
        # Make the call with pre-processing
        result = await wrapper.call_tool(client, "hello", {"name": "World"})
    """
    
    def __init__(self):
        self._pre_call_hooks: list[Callable] = []
    
    def before_tool_call(self, func: Callable) -> Callable:
        """
        Decorator to register a function that runs before tool calls.
        
        The decorated function should accept (tool_name, arguments) and
        return the potentially modified arguments.
        """
        self._pre_call_hooks.append(func)
        return func
    
    def add_pre_call_hook(self, hook: Callable):
        """
        Add a pre-call hook function.
        
        Args:
            hook: Function with signature (tool_name: str, arguments: dict) -> dict
        """
        self._pre_call_hooks.append(hook)
    
    async def call_tool(
        self,
        client: Any,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Any:
        """
        Call a tool with pre-processing logic.
        
        Args:
            client: The MCP client instance
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            The result from the tool call
        """
        # Run all pre-call hooks
        processed_args = arguments
        for hook in self._pre_call_hooks:
            logger.info(f"🚀 [CLIENT PRE-CALL] Running hook: {hook.__name__}")
            processed_args = hook(tool_name, processed_args)
        
        # Log the call
        logger.info(f"🚀 [CLIENT PRE-CALL] Calling tool: {tool_name}")
        logger.info(f"🚀 [CLIENT PRE-CALL] Arguments: {processed_args}")
        
        # Make the actual MCP call
        result = await client.call_tool(tool_name, processed_args)
        
        # Log completion
        logger.info(f"✅ [CLIENT POST-CALL] Tool {tool_name} completed")
        
        return result


# Example usage function
def example_pre_call_hook(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example pre-call hook that validates and logs arguments.
    """
    logger.info(f"Validating call to {tool_name} with args: {arguments}")
    
    # Example: Add timestamp to arguments
    from datetime import datetime
    arguments["_client_timestamp"] = datetime.now().isoformat()
    
    # Example: Validate required fields
    if tool_name == "hello" and "name" not in arguments:
        raise ValueError("Missing required field 'name'")
    
    return arguments


# Convenience function for direct use
async def call_tool_with_logging(
    client: Any,
    tool_name: str,
    arguments: Dict[str, Any],
) -> Any:
    """
    Convenience function to call a tool with basic logging.
    
    Args:
        client: The MCP client instance
        tool_name: Name of the tool to call
        arguments: Arguments to pass to the tool
        
    Returns:
        The result from the tool call
    """
    wrapper = MCPClientWrapper()
    wrapper.add_pre_call_hook(example_pre_call_hook)
    return await wrapper.call_tool(client, tool_name, arguments)
