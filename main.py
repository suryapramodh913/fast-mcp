import os
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastmcp import FastMCP
from middleware import ToolCallLoggerMiddleware

# Configure logging to see middleware output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

mcp = FastMCP("fast-mcp")

# Add the custom middleware to run logic before tool calls
mcp.add_middleware(ToolCallLoggerMiddleware())

PUBLIC_DIR = Path(__file__).parent / "public"
WIDGET_PATH = PUBLIC_DIR / "products-widget-v1.html"

# Bump this when HTML changes to avoid caching
UI_URI = "ui://widget/products-widget-v1.html"
UI_MIME = "text/html;profile=mcp-app"


# ---------- Helpers (mocked demo data) ----------
def _mock_location_from_custom_api(user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Replace this with a real call to your custom location API.
    In production, you'd do a requests.get(...) to your internal service,
    validate auth, and normalize the response.
    """
    return {
        "userId": user_id or "demo-user",
        "locationId": "TN-NASH-001",
        "city": "Nashville",
        "state": "TN",
        "zip": "37201",
        "lat": 36.1627,
        "lon": -86.7816,
        "source": "mock-custom-location-api",
    }

def _mock_products(query: str, location: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Replace with real “products near location” logic
    return [
        {
            "id": "sku-1001",
            "name": f"{query.title()} — Heavy Duty",
            "price": 19.99,
            "availability": "In Stock",
            "store": location["locationId"],
            "distanceMiles": 2.3,
        },
        {
            "id": "sku-1002",
            "name": f"{query.title()} — Value Pack",
            "price": 12.49,
            "availability": "Limited Stock",
            "store": location["locationId"],
            "distanceMiles": 4.8,
        },
        {
            "id": "sku-1003",
            "name": f"{query.title()} — Premium",
            "price": 29.0,
            "availability": "Pickup Tomorrow",
            "store": location["locationId"],
            "distanceMiles": 6.1,
        },
    ]


# ---------- UI Resource ----------
@mcp.resource(
    UI_URI,
    name="ProductsWidget",
    description="Products widget UI",
    mime_type=UI_MIME,
)
def products_widget_resource() -> str:
    if not WIDGET_PATH.exists():
        return "<h3>Missing public/products-widget-v1.html</h3>"
    return WIDGET_PATH.read_text(encoding="utf-8")


# ---------- Tools ----------
@mcp.tool(
    name="get_meta",
    description="Return MCP UI/tool metadata that clients can use for rendering or debugging.",
)
def get_meta(ctx: Context) -> Dict[str, Any]:
    user_location = None

    try:
        user_location = ctx.meta.get("openai/userLocation")
    except Exception:
        user_location = None

    return {
        "openai/userLocation": user_location,
        "app": {"name": "fast-mcp"},
        "ui": {
            "productsWidget": {
                "resourceUri": UI_URI,
                "mimeType": UI_MIME,
            }
        },
    }

@mcp.tool(
    name="resolve_location",
    description="Resolve the current user's location via custom API (server-side).",
)
def resolve_location(user_id: str = "demo-user") -> Dict[str, Any]:
    loc = _mock_location_from_custom_api(user_id=user_id)
    # Return as plain JSON (no UI meta needed)
    return loc

@mcp.tool(
    name="find_products",
    description="Find products near a location.",
)
def find_products(
    query: str,
    locationId: str,
    lat: float,
    lon: float,
    radiusMiles: int = 25,
) -> Dict[str, Any]:
    location = {
        "locationId": locationId,
        "lat": lat,
        "lon": lon,
        "radiusMiles": radiusMiles,
    }
    # Real implementation: call your catalog/search service(s)
    products = _mock_products(query=query, location={"locationId": locationId, "lat": lat, "lon": lon})
    return {
        "structuredContent": {
            "query": query,
            "location": location,
            "products": products,
            "message": f"Found {len(products)} results near {locationId}.",
        },
        "_meta": {},
        "content": [{"type": "text", "text": f"Found {len(products)} products near {locationId}"}],
    }

@mcp.tool(
    name="show_products_widget",
    description="Render products widget in ChatGPT Apps UI.",
    meta={"ui": {"resourceUri": UI_URI}},
)
def show_products_widget() -> Dict[str, Any]:
    # This tool is just to show the UI
    return {
        "structuredContent": {
            "message": "Products widget ready. Search using the UI.",
        },
        "_meta": {"ui": {"resourceUri": UI_URI}},
        "content": [{"type": "text", "text": "Products widget ready."}],
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    mcp.run(transport="http", host="0.0.0.0", port=port)
