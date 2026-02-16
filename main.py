from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastmcp import FastMCP

mcp = FastMCP("fast-mcp")

@mcp.tool
def hello(name: str) -> str:
    return f"Hello, {name}!"

app = FastAPI()

# ✅ Alpic probes /mcp — must exist
app.mount("/mcp", mcp.http_app())

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
      <body style="font-family:system-ui;max-width:720px;margin:40px auto;">
        <h2>FastMCP is running ✅</h2>
        <ul>
          <li><a href="/health">/health</a></li>
          <li>/mcp (MCP endpoint)</li>
        </ul>
      </body>
    </html>
    """
