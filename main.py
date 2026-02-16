import os
from pathlib import Path
from fastmcp import FastMCP
from starlette.responses import HTMLResponse, JSONResponse

# -------------------------
# MCP server (Alpic detects this)
# -------------------------
mcp = FastMCP("fast-mcp")

@mcp.tool
def hello(name: str) -> str:
    return f"Hello, {name}!"

# -------------------------
# HTML UI (served by same server)
# -------------------------
PUBLIC_DIR = Path(__file__).parent / "public"
WIDGET_PATH = PUBLIC_DIR / "hello-widget.html"

@mcp.custom_route("/", methods=["GET"])
async def home(_request):
    # simple landing page
    return HTMLResponse(
        """
        <html>
          <body style="font-family:system-ui;max-width:720px;margin:40px auto;padding:0 16px;">
            <h2>FastMCP is running ✅</h2>
            <p>Try:</p>
            <ul>
              <li><a href="/hello">/hello</a> (HTML response)</li>
              <li><a href="/health">/health</a> (health check)</li>
            </ul>
          </body>
        </html>
        """
    )

@mcp.custom_route("/hello", methods=["GET"])
async def hello_html(_request):
    # This prints HTML in browser
    return HTMLResponse("<h1>Hello Surya</h1>")

@mcp.custom_route("/api/hello", methods=["GET"])
async def api_hello(request):
    name = request.query_params.get("name", "Surya")
    return JSONResponse({"message": hello(name)})

@mcp.custom_route("/health", methods=["GET"])
async def health(_request):
    return JSONResponse({"status": "ok"})

# -------------------------
# ChatGPT App Widget (serve the HTML file)
# -------------------------
# We expose your widget HTML via a normal URL so ChatGPT can load it.
@mcp.custom_route("/public/hello-widget.html", methods=["GET"])
async def widget_html(_request):
    if not WIDGET_PATH.exists():
        return HTMLResponse("<h3>Missing public/hello-widget.html</h3>", status_code=404)
    return HTMLResponse(WIDGET_PATH.read_text(encoding="utf-8"))

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    mcp.run(transport="http", host="0.0.0.0", port=port)
