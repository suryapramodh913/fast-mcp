import os
from pathlib import Path

from fastmcp import FastMCP
from starlette.responses import HTMLResponse, JSONResponse

mcp = FastMCP("fast-mcp")

PUBLIC_DIR = Path(__file__).parent / "public"
WIDGET_PATH = PUBLIC_DIR / "hello-widget.html"

UI_URI = "ui://hello-widget"
UI_MIME = "text/html;profile=mcp-app"

@mcp.tool
def hello(name: str) -> str:
    return f"Hello, {name}!"

# ✅ 1) Register the widget as an MCP Resource (NOT just a web route)
@mcp.resource(
    UI_URI,
    name="HelloWidget",
    description="A small HTML widget to display the hello message.",
    mime_type=UI_MIME
)
def hello_widget_resource() -> str:
    if not WIDGET_PATH.exists():
        return "<h3>Missing public/hello-widget.html</h3>"
    return WIDGET_PATH.read_text(encoding="utf-8")

# ✅ 2) Tool that instructs ChatGPT to render the widget
@mcp.tool(
    name="show_hello_widget",
    description="Render the hello widget inside ChatGPT.",
    meta={"ui": {"resourceUri": UI_URI}},
)
def show_hello_widget(name: str = "Surya") -> dict:
    message = hello(name)
    return {
        "structuredContent": {"message": message},
        "_meta": {"ui": {"resourceUri": UI_URI}},
        "content": [{"type": "text", "text": message}],
    }

# Keep your browser endpoints if you want
@mcp.custom_route("/hello", methods=["GET"])
async def hello_html(_request):
    return HTMLResponse("<h1>Hello Surya</h1>")

@mcp.custom_route("/health", methods=["GET"])
async def health(_request):
    return JSONResponse({"status": "ok"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    mcp.run(transport="http", host="0.0.0.0", port=port)
