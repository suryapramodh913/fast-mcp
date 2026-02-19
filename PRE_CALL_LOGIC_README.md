# Pre-MCP Call Logic Implementation

This repository demonstrates how to run custom logic **before MCP tool calls** on both the client side and server side.

## Overview

The implementation provides three layers of pre-call logic:

1. **🌐 Browser-Side** - Runs in the web UI before processing tool results
2. **💻 Client-Side (Python)** - Runs before sending requests to the MCP server  
3. **🖥️ Server-Side** - Runs on the server before executing the tool

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Browser   │────▶│  Client Wrapper  │────▶│ Server Middleware│
│  Pre-Logic  │     │   Pre-Logic      │     │   Pre-Logic      │
└─────────────┘     └──────────────────┘     └──────────────────┘
                                                       │
                                                       ▼
                                              ┌────────────────┐
                                              │  Tool Execution│
                                              └────────────────┘
```

## Files

- **`middleware.py`** - Server-side middleware for pre-call logic
- **`client_wrapper.py`** - Client-side wrapper for pre-call logic
- **`public/hello-widget.html`** - Browser-side pre-call logic example
- **`example_usage.py`** - Complete example demonstrating all three layers
- **`main.py`** - Server with middleware enabled
- **`server.py`** - Another server with middleware enabled

## Usage

### 1. Server-Side Pre-Call Logic

Add middleware to your FastMCP server to run logic before tool execution:

```python
from fastmcp import FastMCP
from middleware import ToolCallLoggerMiddleware

mcp = FastMCP("my-server")

# Add middleware to run logic before tool calls
mcp.add_middleware(ToolCallLoggerMiddleware())

@mcp.tool
def hello(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
```

**Server-side middleware can:**
- ✅ Authenticate/authorize requests
- ✅ Validate inputs
- ✅ Rate limit requests
- ✅ Log all tool calls
- ✅ Transform arguments
- ✅ Collect metrics

### 2. Client-Side Pre-Call Logic (Python)

Use the client wrapper when making programmatic calls:

```python
from client_wrapper import MCPClientWrapper
from fastmcp import Client

# Create wrapper
wrapper = MCPClientWrapper()

# Add custom pre-call logic
@wrapper.before_tool_call
def validate_inputs(tool_name: str, arguments: dict) -> dict:
    print(f"Calling {tool_name} with {arguments}")
    # Add metadata, validate, transform, etc.
    return arguments

# Make calls with pre-processing
async with Client.stdio("python3", "server.py") as client:
    result = await wrapper.call_tool(client, "hello", {"name": "World"})
```

### 3. Browser-Side Pre-Call Logic

The widget in `public/hello-widget.html` shows browser-side pre-processing:

```javascript
function preProcessToolResult(toolResult) {
    console.log("🚀 [PRE-CALL BROWSER LOGIC] Processing tool result");
    
    // Add your custom browser-side logic here:
    // - Validate data
    // - Log analytics
    // - Transform data
    // - Show loading states
    
    return toolResult;
}
```

## Creating Custom Middleware

Extend the `Middleware` base class and override the `on_call_tool` method:

```python
from typing import Any
from fastmcp.server.middleware.middleware import Middleware, MiddlewareContext, CallNext
from mcp.types import CallToolRequestParams

class CustomMiddleware(Middleware):
    async def on_call_tool(
        self,
        context: MiddlewareContext[CallToolRequestParams],
        call_next: CallNext[CallToolRequestParams, Any],
    ) -> Any:
        # PRE-processing logic
        tool_name = context.message.name
        arguments = context.message.arguments
        
        print(f"Before calling {tool_name}")
        
        # Execute the tool
        result = await call_next(context)
        
        # POST-processing logic
        print(f"After calling {tool_name}")
        
        return result
```

## Running the Example

```bash
# Install dependencies
pip install fastmcp

# Run the example (shows configuration)
python3 example_usage.py

# Or test with the actual servers
python3 main.py      # Server on port 8000
python3 server.py    # Server on port 8000
```

## Use Cases

### Authentication Example
```python
class AuthMiddleware(Middleware):
    async def on_call_tool(self, context, call_next):
        # Check authentication
        user = context.fastmcp_context.get("user")
        if not user:
            raise PermissionError("Not authenticated")
        
        return await call_next(context)
```

### Rate Limiting Example
```python
from datetime import datetime, timedelta

class RateLimitMiddleware(Middleware):
    def __init__(self):
        self.calls = {}
    
    async def on_call_tool(self, context, call_next):
        tool_name = context.message.name
        now = datetime.now()
        
        # Check rate limit
        if tool_name in self.calls:
            last_call = self.calls[tool_name]
            if now - last_call < timedelta(seconds=1):
                raise Exception("Rate limit exceeded")
        
        self.calls[tool_name] = now
        return await call_next(context)
```

### Input Validation Example
```python
class ValidationMiddleware(Middleware):
    async def on_call_tool(self, context, call_next):
        arguments = context.message.arguments
        
        # Validate inputs
        if "name" in arguments and len(arguments["name"]) > 100:
            raise ValueError("Name too long")
        
        return await call_next(context)
```

## Testing

Check the syntax of all files:
```bash
python3 -m py_compile middleware.py client_wrapper.py main.py server.py example_usage.py
```

## Benefits

✅ **Security** - Validate and sanitize inputs before execution  
✅ **Observability** - Log all tool calls for monitoring  
✅ **Control** - Rate limiting and access control  
✅ **Flexibility** - Transform data before/after execution  
✅ **Debugging** - Easier to trace and debug issues  
✅ **Analytics** - Track usage patterns  

## License

This code is part of the fast-mcp repository.
