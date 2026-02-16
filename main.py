from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastmcp import FastMCP

# ---- MCP server ----
mcp = FastMCP("fast-mcp")

@mcp.tool
def hello(name: str) -> str:
    return f"Hello, {name}!"

# ---- Web app (ASGI) ----
app = FastAPI()

# ✅ Alpic probes this endpoint; MUST exist
app.mount("/mcp", mcp.http_app())

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
