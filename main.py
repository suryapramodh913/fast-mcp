from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastmcp import FastMCP

# -------------------------
# Config
# -------------------------
APP_MIME = "text/html;profile=mcp-app"
UI_URI = "ui://widget/hello-widget.html"

PUBLIC_DIR = Path(__file__).parent / "public"
WIDGET_FILE = PUBLIC_DIR / "hello-widget.html"

# -------------------------
# MCP Server
# -------------------------
mcp = FastMCP("fast-mcp-hello")

@mcp.tool(
    name="hello",
    description="Return a friendly greeting message.",
)
def hello(name: str) -> str:
    return f"Hello, {name}!"

# ✅ Expose the widget HTML as an MCP resource so ChatGPT Apps can render it
@mcp.resource(
    UI_URI,
    name="HelloWidget",
    description="HTML widget for showing the hello message.",
    mime_type=APP_MIME,
    meta={
        "ui": {
            # These are optional, but helpful.
            # Add domains you need if your widget fetches from APIs.
            "prefersBorder": True,
            "csp": {
                "connectDomains": ["https://fast-mcp-f337845e.alpic.live"],
                "resourceDomains": ["https://*.oaistatic.com"],
            },
        }
    },
)
def hello_widget_resource() -> str:
    if not WIDGET_FILE.exists():
        return "<html><body><h3>Missing public/hello-widget.html</h3></body></html>"
    return WIDGET_FILE.read_text(encoding="utf-8")

# ✅ Tool that tells ChatGPT which widget to load
# ChatGPT Apps looks at _meta.ui.resourceUri to choose the template to render.
@mcp.tool(
    name="show_hello_widget",
    description="Show the hello widget and provide a greeting in structuredContent.",
    meta={"ui": {"resourceUri": UI_URI}},
)
def show_hello_widget(name: str = "Surya") -> dict:
    message = hello(name)
    return {
        "structuredContent": {"message": message},
        "content": [{"type": "text", "text": message}],
        "_meta": {"ui": {"resourceUri": UI_URI}},
    }

# -------------------------
# FastAPI host (Alpic)
# -------------------------
app = FastAPI()

# ✅ This is CRITICAL: Alpic probes /mcp and ChatGPT connects here
app.mount("/mcp", mcp.http_app())

# Optional: simple browser page
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
      <body style="font-family:system-ui;max-width:720px;margin:40px auto;padding:0 16px;">
        <h1>FastMCP + ChatGPT App</h1>
        <ul>
          <li><a href="/hello">/hello</a> (plain HTML test)</li>
          <li><a href="/health">/health</a> (health check)</li>
          <li>/mcp (MCP endpoint — use POST, not browser GET)</li>
        </ul>
      </body>
    </html>
    """

@app.get("/hello", response_class=HTMLResponse)
def hello_page():
    # Plain HTML response in browser
    return "<h1>Hello Surya</h1>"

@app.get("/health")
def health():
    return {"status": "ok"}
