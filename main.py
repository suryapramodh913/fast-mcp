import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastmcp import FastMCP

# ----- MCP -----
mcp = FastMCP("my-fastmcp-server")

@mcp.tool
def hello(name: str) -> str:
    return f"Hello, {name}!"

# ----- Web App -----
app = FastAPI()

# Mount MCP at /mcp (so ChatGPT can connect)
app.mount("/mcp", mcp.http_app())

# Tiny UI page
@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>FastMCP UI</title>
    <style>
      body { font-family: system-ui, Arial; max-width: 640px; margin: 40px auto; padding: 0 16px; }
      button { padding: 10px 14px; font-size: 16px; cursor: pointer; }
      #out { margin-top: 16px; font-size: 20px; font-weight: 600; }
      .muted { color: #666; margin-top: 8px; }
    </style>
  </head>
  <body>
    <h1>FastMCP Test UI</h1>
    <button id="btn">Say Hello to Surya</button>
    <div id="out"></div>
    <div class="muted">This calls <code>/api/hello?name=Surya</code> (separate from MCP).</div>

    <script>
      const btn = document.getElementById("btn");
      const out = document.getElementById("out");

      btn.onclick = async () => {
        out.textContent = "Loading...";
        try {
          const r = await fetch("/api/hello?name=Surya");
          const data = await r.json();
          out.textContent = data.message;
        } catch (e) {
          out.textContent = "Error: " + (e?.message ?? e);
        }
      };
    </script>
  </body>
</html>
"""

# Simple JSON API for the UI (reuses same hello() logic)
@app.get("/api/hello")
def api_hello(name: str = "Surya"):
    return {"message": hello(name)}

# Optional health check
@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
