import os
from pathlib import Path

from fastmcp import FastMCP
from starlette.responses import JSONResponse

mcp = FastMCP("fast-mcp")

PUBLIC_DIR = Path(__file__).parent / "public"
WIDGET_PATH = PUBLIC_DIR / "hello-widget.html"

# IMPORTANT: version this when you change widget HTML to avoid cache issues
UI_URI = "ui://widget/hello-widget-v1.html"
UI_MIME = "text/html;profile=mcp-app"


def hello_message(name: str) -> str:
    return f"Hello, {name}!"


@mcp.tool
def hello(name: str) -> str:
    return hello_message(name)


# ✅ Return a template resource with explicit contents[].mimeType + contents[].uri
@mcp.resource(
    UI_URI,
    name="HelloWidget",
    description="A tiny widget that displays the greeting.",
    mime_type=UI_MIME,
)
def hello_widget_resource():
    html = "<h3>Missing public/hello-widget.html</h3>"
    if WIDGET_PATH.exists():
        html = WIDGET_PATH.read_text(encoding="utf-8")

    return {
        "contents": [
            {
                "uri": UI_URI,
                "mimeType": UI_MIME,
                "text": html,
                "_meta": {
                    "ui": {
                        "prefersBorder": True,
                        # If your widget fetches network resources, add CSP allowlists here.
                        # Keep empty if not needed.
                        "csp": {
                            "resourceDomains": ["https://*.oaistatic.com"]
                        },
                    }
                },
            }
        ]
    }


@mcp.tool(
    name="show_hello_widget",
    description="Show the hello widget inside the ChatGPT App UI.",
    meta={"ui": {"resourceUri": UI_URI}},
)
def show_hello_widget(name: str = "Surya") -> dict:
    message = hello_message(name)
    return {
        "structuredContent": {"message": message},
        "content": [{"type": "text", "text": message}],
        "_meta": {"ui": {"resourceUri": UI_URI}},
    }


@mcp.custom_route("/health", methods=["GET"])
async def health(_request):
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    mcp.run(transport="http", host="0.0.0.0", port=port)
