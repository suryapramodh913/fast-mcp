import os
import logging
from pathlib import Path
from fastmcp import FastMCP
from middleware import ToolCallLoggerMiddleware

# Configure logging to see middleware output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

mcp = FastMCP("fast-mcp")

# Add the custom middleware to run logic before tool calls
mcp.add_middleware(ToolCallLoggerMiddleware())

PUBLIC_DIR = Path(__file__).parent / "public"
WIDGET_PATH = PUBLIC_DIR / "hello-widget.html"

# Bump version when you change HTML to avoid caching
UI_URI = "ui://widget/hello-widget-v2.html"
UI_MIME = "text/html;profile=mcp-app"


def hello_message(name: str) -> str:
    return f"Hello, {name}!"


@mcp.tool
def hello(name: str) -> str:
    return hello_message(name)


# ✅ IMPORTANT: return HTML STRING only
@mcp.resource(
    UI_URI,
    name="HelloWidget",
    description="Hello widget UI",
    mime_type=UI_MIME,
)
def hello_widget_resource() -> str:
    if not WIDGET_PATH.exists():
        return "<h3>Missing public/hello-widget.html</h3>"
    return WIDGET_PATH.read_text(encoding="utf-8")


@mcp.tool(
    name="show_hello_widget",
    description="Render hello widget in ChatGPT Apps UI.",
    meta={"ui": {"resourceUri": UI_URI}},
)
def show_hello_widget(name: str = "Surya") -> dict:
    message = hello_message(name)
    return {
        "structuredContent": {"message": message},
        "_meta": {"ui": {"resourceUri": UI_URI}},
        "content": [{"type": "text", "text": message}],
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    mcp.run(transport="http", host="0.0.0.0", port=port)
