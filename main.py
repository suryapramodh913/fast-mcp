import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastmcp import FastMCP

from starlette.applications import Starlette
from starlette.routing import Route, Mount

# ---- MCP server ----
mcp = FastMCP("fast-mcp")

@mcp.tool
def hello(name: str) -> str:
    return f"Hello, {name}!"

# The actual MCP ASGI app
mcp_asgi = mcp.http_app()

# ---- Wrapper sub-app for /mcp so GET /mcp is not 404 ----
async def mcp_probe(_request):
    return JSONResponse({"status": "ok", "note": "MCP endpoint is alive. Use POST for MCP calls."})

mcp_wrapper = Starlette(
    routes=[
        Route("/", mcp_probe, methods=["GET"]),      # <-- makes Alpic probe pass
        Mount("/", app=mcp_asgi),                    # <-- forwards POST/stream calls to FastMCP
    ]
)

# ---- Web app (ASGI) ----
app = FastAPI()

# Mount wrapper at /mcp
app.mount("/mcp", mcp_wrapper)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
      <body style="font-family:system-ui;max-width:640px;margin:40px auto;">
        <h1>FastMCP UI</h1>
        <button onclick="go()">Say Hello to Surya</button>
        <pre id="out"></pre>
        <script>
          async function go(){
            const r = await fetch('/api/hello?name=Surya');
            document.getElementById('out').textContent = JSON.stringify(await r.json(), null, 2);
          }
        </script>
      </body>
    </html>
    """

@app.get("/api/hello")
def api_hello(name: str = "Surya"):
    return {"message": hello(name)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
