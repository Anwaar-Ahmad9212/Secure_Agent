"""
Tools available to the AI agent.
These are simulated tools that demonstrate what could be executed.
"""

import json
from datetime import datetime


def http_request(url, method="GET", data=None):
    """
    Simulated HTTP request tool.
    In a real system, this would make actual HTTP requests.
    """
    print(f"\n{'='*60}")
    print(f"🚨 TOOL EXECUTION: HTTP Request")
    print(f"{'='*60}")
    print(f"URL: {url}")
    print(f"Method: {method}")
    print(f"Data: {json.dumps(data, indent=2) if data else 'None'}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    # Simulate response
    result = {
        "status": "executed",
        "tool": "http_request",
        "url": url,
        "method": method,
        "data": data,
        "timestamp": datetime.now().isoformat(),
        "simulated": True,
        "message": "⚠️ This is a simulated request. In production, this would send actual HTTP traffic."
    }
    
    return result


def file_operation(operation, path, content=None):
    """
    Simulated file operation tool.
    In a real system, this would perform actual file operations.
    """
    print(f"\n{'='*60}")
    print(f"🚨 TOOL EXECUTION: File Operation")
    print(f"{'='*60}")
    print(f"Operation: {operation}")
    print(f"Path: {path}")
    print(f"Content: {content[:100] if content else 'None'}...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    result = {
        "status": "executed",
        "tool": "file_operation",
        "operation": operation,
        "path": path,
        "timestamp": datetime.now().isoformat(),
        "simulated": True,
        "message": "⚠️ This is a simulated operation. In production, this would modify actual files."
    }
    
    return result


def database_query(query, database="main"):
    """
    Simulated database query tool.
    In a real system, this would execute actual database queries.
    """
    print(f"\n{'='*60}")
    print(f"🚨 TOOL EXECUTION: Database Query")
    print(f"{'='*60}")
    print(f"Database: {database}")
    print(f"Query: {query}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    result = {
        "status": "executed",
        "tool": "database_query",
        "database": database,
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "simulated": True,
        "message": "⚠️ This is a simulated query. In production, this would access actual databases."
    }
    
    return result


# Tool registry
AVAILABLE_TOOLS = {
    "http_request": http_request,
    "file_operation": file_operation,
    "database_query": database_query
}


def execute_tool(tool_name, **kwargs):
    """
    Execute a tool by name with given parameters.
    """
    if tool_name not in AVAILABLE_TOOLS:
        return {
            "status": "error",
            "message": f"Tool '{tool_name}' not found",
            "available_tools": list(AVAILABLE_TOOLS.keys())
        }
    
    tool_function = AVAILABLE_TOOLS[tool_name]
    
    try:
        result = tool_function(**kwargs)
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "tool": tool_name
        }


def get_tool_description():
    """
    Get a description of all available tools for the AI agent.
    """
    return """
Available Tools:

1. http_request(url, method="GET", data=None)
   - Makes HTTP requests to external URLs
   - Use for sending data, fetching information, webhook calls
   
2. file_operation(operation, path, content=None)
   - Performs file operations (read, write, delete)
   - Use for file management tasks
   
3. database_query(query, database="main")
   - Executes database queries
   - Use for data retrieval or modification

When you need to perform an action, call the appropriate tool with the required parameters.
"""
