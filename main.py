import os
from pathlib import Path
from fastmcp import FastMCP
from starlette.responses import HTMLResponse, JSONResponse

mcp = FastMCP("fast-mcp")

PUBLIC_DIR = Path(__file__).parent / "public"
WIDGET_PATH = PUBLIC_DIR / "hello-widget.html"

UI_URI = "ui://hello-widget"
UI_MIME = "text/html;profile=mcp-app"


# ✅ Plain Python helper (NOT a tool)
def hello_message(name: str) -> str:
    return f"Hello, {name}!"


# -------------------------
# Tool 1: plain hello
# -------------------------
@mcp.tool
def hello(name: str) -> str:
    return hello_message(name)


# -------------------------
# UI Resource: widget HTML for Apps SDK
# -------------------------
@mcp.resource(
    UI_URI,
    name="HelloWidget",
    description="A tiny widget that displays a greeting.",
    mime_type=UI_MIME,
)
def hello_widget_resource() -> str:
    if not WIDGET_PATH.exists():
        return "<h3>Missing public/hello-widget.html</h3>"
    return WIDGET_PATH.read_text(encoding="utf-8")


# -------------------------
# Tool 2: triggers widget render
# -------------------------
@mcp.tool(
    name="show_hello_widget",
    description="Show the hello widget inside ChatGPT Apps UI.",
    meta={"ui": {"resourceUri": UI_URI}},
)
def show_hello_widget(name: str = "Surya") -> dict:
    message = hello_message(name)  # ✅ use helper, NOT hello()
    return {
        "structuredContent": {"message": message},
        "content": [{"type": "text", "text": message}],
        "_meta": {"ui": {"resourceUri": UI_URI}},
    }


# Optional routes (browser checks)
@mcp.custom_route("/health", methods=["GET"])
async def health(_request):
    return JSONResponse({"status": "ok"})

@mcp.custom_route("/hello", methods=["GET"])
async def hello_html(_request):
    return HTMLResponse("<h1>Hello Surya</h1>")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    mcp.run(transport="http", host="0.0.0.0", port=port)
