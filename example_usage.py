"""
Example demonstrating pre-call logic on both client and server side.

This example shows:
1. Server-side middleware that runs before tool execution
2. Client-side wrapper that runs before sending the MCP request

Run this example:
    python3 example_usage.py
"""
import asyncio
import logging
from typing import Dict, Any
from fastmcp import FastMCP, Client
from middleware import ToolCallLoggerMiddleware
from client_wrapper import MCPClientWrapper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# SERVER SIDE: Create MCP server with middleware
# ============================================================================

mcp_server = FastMCP("example-server")

# Add server-side middleware for pre-call logic
mcp_server.add_middleware(ToolCallLoggerMiddleware())


@mcp_server.tool
def greet(name: str, language: str = "en") -> str:
    """Greet someone in different languages."""
    greetings = {
        "en": f"Hello, {name}!",
        "es": f"¡Hola, {name}!",
        "fr": f"Bonjour, {name}!",
        "de": f"Guten Tag, {name}!",
    }
    return greetings.get(language, greetings["en"])


@mcp_server.tool
def calculate(operation: str, a: float, b: float) -> float:
    """Perform basic math operations."""
    operations = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else float('inf'),
    }
    return operations.get(operation, 0.0)


# ============================================================================
# CLIENT SIDE: Create client wrapper with pre-call hooks
# ============================================================================

async def demo_client_server_interaction():
    """
    Demonstrate client-side pre-call logic before sending to server.
    The server-side middleware will also run its pre-call logic.
    """
    logger.info("=" * 80)
    logger.info("DEMO: Client-Side and Server-Side Pre-Call Logic")
    logger.info("=" * 80)
    
    # Create client wrapper with pre-call hooks
    client_wrapper = MCPClientWrapper()
    
    # Register a custom client-side pre-call hook
    @client_wrapper.before_tool_call
    def validate_and_log(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Client-side validation before sending to server."""
        logger.info(f"🌐 [CLIENT BROWSER-SIDE] Validating {tool_name}")
        
        # Example: Add metadata
        from datetime import datetime
        arguments["_client_request_time"] = datetime.now().isoformat()
        
        # Example: Validate inputs
        if tool_name == "greet" and len(arguments.get("name", "")) == 0:
            logger.warning("⚠️  [CLIENT BROWSER-SIDE] Empty name provided!")
        
        return arguments
    
    # Start the server in stdio mode for testing
    async with Client.stdio("python3", "-m", "example_usage_server") as client:
        logger.info("\n📡 Connected to MCP server\n")
        
        # List available tools
        tools_response = await client.list_tools()
        logger.info(f"Available tools: {[t.name for t in tools_response.tools]}")
        
        logger.info("\n" + "=" * 80)
        logger.info("TEST 1: Calling 'greet' tool")
        logger.info("=" * 80)
        
        # Call the greet tool with client-side pre-processing
        result1 = await client_wrapper.call_tool(
            client,
            "greet",
            {"name": "Alice", "language": "es"}
        )
        logger.info(f"✨ Result: {result1}\n")
        
        logger.info("=" * 80)
        logger.info("TEST 2: Calling 'calculate' tool")
        logger.info("=" * 80)
        
        # Call the calculate tool
        result2 = await client_wrapper.call_tool(
            client,
            "calculate",
            {"operation": "multiply", "a": 7.0, "b": 6.0}
        )
        logger.info(f"✨ Result: {result2}\n")
        
        logger.info("=" * 80)
        logger.info("DEMO COMPLETE")
        logger.info("=" * 80)


if __name__ == "__main__":
    # Note: This requires the server to be run separately or via stdio
    # For this example, we'll show what the interaction would look like
    
    logger.info("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║                                                                    ║
    ║         Pre-Call Logic Example for FastMCP                        ║
    ║                                                                    ║
    ║  This demonstrates running custom logic BEFORE MCP calls:         ║
    ║                                                                    ║
    ║  1. 🌐 Browser/Client Side: Runs before sending request           ║
    ║     - Validation                                                   ║
    ║     - Adding metadata                                              ║
    ║     - Logging                                                      ║
    ║                                                                    ║
    ║  2. 🖥️  Server Side: Runs before executing tool                    ║
    ║     - Authentication/Authorization                                 ║
    ║     - Rate limiting                                                ║
    ║     - Logging                                                      ║
    ║     - Input transformation                                         ║
    ║                                                                    ║
    ╚════════════════════════════════════════════════════════════════════╝
    """)
    
    logger.info("\nTo run the full demo, you would:")
    logger.info("1. Start the server: python3 -m example_usage_server")
    logger.info("2. In another terminal: python3 example_usage.py")
    logger.info("\nFor now, showing the server configuration...\n")
    
    # Show the server setup
    logger.info("Server configured with:")
    logger.info(f"  - Name: {mcp_server.name}")
    logger.info(f"  - Tools: greet, calculate")
    logger.info(f"  - Middleware: ToolCallLoggerMiddleware (runs before each tool call)")
    logger.info("\nServer is ready to receive requests with pre-call logic enabled!")
