"""
Custom middleware for FastMCP to run logic before tool calls.
"""
from fastmcp.server.middleware.middleware import Middleware, MiddlewareContext, CallNext
from mcp.types import CallToolRequestParams, Tool
import logging

logger = logging.getLogger(__name__)


class ToolCallLoggerMiddleware(Middleware):
    """
    Middleware that logs tool calls before execution.
    
    This demonstrates how to run custom logic before an MCP tool call.
    You can extend this to add validation, authentication, rate limiting, etc.
    """
    
    async def on_call_tool(
        self,
        context: MiddlewareContext[CallToolRequestParams],
        call_next: CallNext[CallToolRequestParams, any],
    ) -> any:
        """
        Hook that runs before every tool call.
        
        Args:
            context: Contains the tool call request with name and arguments
            call_next: Function to call to continue the middleware chain
            
        Returns:
            The result from the tool execution
        """
        # Access tool information from the context
        tool_name = context.message.name
        tool_args = context.message.arguments
        
        # Pre-processing logic - runs BEFORE the MCP call
        logger.info(f"[PRE-CALL] Tool: {tool_name}")
        logger.info(f"[PRE-CALL] Arguments: {tool_args}")
        
        # You can add custom logic here:
        # - Validation of inputs
        # - Authentication/authorization checks
        # - Rate limiting
        # - Metrics collection
        # - Input transformation
        
        # Call the next middleware or the actual tool
        result = await call_next(context)
        
        # Post-processing logic - runs AFTER the MCP call
        logger.info(f"[POST-CALL] Tool: {tool_name} completed")
        
        return result
