import os
import logging
from fastmcp import FastMCP
from starlette.responses import JSONResponse
from middleware import ToolCallLoggerMiddleware

# Configure logging to see middleware output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

mcp = FastMCP("my-fastmcp-server")

# Add the custom middleware to run logic before tool calls
mcp.add_middleware(ToolCallLoggerMiddleware())

@mcp.tool
def hello(name: str) -> str:
    return f"Hello, {name} Super!"

# Health check endpoint (helps confirm deployment works)
@mcp.custom_route("/health", methods=["GET"])
async def health(_request):
    return JSONResponse({"status": "ok"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))  # Alpic/platforms often set PORT
    mcp.run(transport="http", host="0.0.0.0", port=port)
