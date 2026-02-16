import os
from fastmcp import FastMCP
from starlette.responses import JSONResponse, HTMLResponse

mcp = FastMCP("my-fastmcp-server")

@mcp.tool
def hello(name: str) -> str:
    return f"Hello, {name}!"

# ✅ UI page
@mcp.custom_route("/", methods=["GET"])
async def home(_request):
    return HTMLResponse("""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>FastMCP UI</title>
    <style>
      body { font-family: system-ui, Arial; max-width: 640px; margin: 40px auto; padding: 0 16px; }
      button { padding: 10px 14px; font-size: 16px; cursor: pointer; }
      #out { margin-top: 16px; font-size: 22px; font-weight: 700; }
    </style>
  </head>
  <body>
    <h1>FastMCP UI</h1>
    <button id="btn">Say Hello to Surya</button>
    <div id="out"></div>

    <script>
      document.getElementById("btn").onclick = async () => {
        const r = await fetch("/api/hello?name=Surya");
        const data = await r.json();
        document.getElementById("out").textContent = data.message;
      };
    </script>
  </body>
</html>
""")

# ✅ JSON endpoint used by the UI
@mcp.custom_route("/api/hello", methods=["GET"])
async def api_hello(request):
    name = request.query_params.get("name", "Surya")
    return JSONResponse({"message": hello(name)})

# ✅ Health check endpoint
@mcp.custom_route("/health", methods=["GET"])
async def health(_request):
    return JSONResponse({"status": "ok"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    mcp.run(transport="http", host="0.0.0.0", port=port)
