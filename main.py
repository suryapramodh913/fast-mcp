import os
from fastmcp import FastMCP
from starlette.responses import JSONResponse

mcp = FastMCP("my-fastmcp-server")

@mcp.tool
def hello(name: str) -> str:
    return f"Hello, {name}!"

# Health check endpoint (helps confirm deployment works)
@mcp.custom_route("/health", methods=["GET"])
async def health(_request):
    return JSONResponse({"status": "ok"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))  # Alpic/platforms often set PORT
    mcp.run(transport="http", host="0.0.0.0", port=port)
