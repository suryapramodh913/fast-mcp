"""
Example server module for demonstrating pre-call logic.
This is meant to be run as: python3 -m example_usage_server
"""
from example_usage import mcp_server

if __name__ == "__main__":
    # Run the server with stdio transport for client connection
    mcp_server.run(transport="stdio")
