"""
tools.py - Real working tools that AI agent can execute
WARNING: These tools perform ACTUAL operations for demonstration purposes
"""
import json
import requests
from datetime import datetime
from database import execute_query, get_all_customers, search_customer


def http_request(url, method="GET", data=None):
    """
    REAL HTTP request tool - makes actual network calls
    ⚠️ WARNING: This will send actual HTTP requests!
    """
    print(f"\n{'='*70}")
    print(f"🌐 EXECUTING REAL HTTP REQUEST")
    print(f"{'='*70}")
    print(f"URL     : {url}")
    print(f"Method  : {method}")
    print(f"Data    : {json.dumps(data, indent=2) if data else 'None'}")
    print(f"Time    : {datetime.now().isoformat()}")
    print(f"{'='*70}")
    
    try:
        # Actually make the HTTP request
        if method.upper() == "GET":
            response = requests.get(url, timeout=5)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=5)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, timeout=5)
        elif method.upper() == "DELETE":
            response = requests.delete(url, timeout=5)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        result = {
            "status": "success",
            "tool": "http_request",
            "url": url,
            "method": method,
            "status_code": response.status_code,
            "response_text": response.text[:500],  # First 500 chars
            "timestamp": datetime.now().isoformat(),
            "WARNING": "⚠️ THIS WAS A REAL HTTP REQUEST"
        }
        
        print(f"✅ Request completed: {response.status_code}")
        print(f"{'='*70}\n")
        return result
        
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "message": "Request timed out after 5 seconds",
            "tool": "http_request",
            "url": url
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": str(e),
            "tool": "http_request",
            "url": url
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "tool": "http_request"
        }


def database_query(query, database="main"):
    """
    REAL database query tool - executes actual SQL
    ⚠️ WARNING: This executes real SQL queries on the database!
    """
    print(f"\n{'='*70}")
    print(f"💾 EXECUTING REAL DATABASE QUERY")
    print(f"{'='*70}")
    print(f"Database: {database}")
    print(f"Query   : {query}")
    print(f"Time    : {datetime.now().isoformat()}")
    print(f"{'='*70}")
    
    try:
        # Actually execute the query
        result = execute_query(query)
        
        if result["status"] == "success":
            if "rows" in result:
                print(f"✅ Query executed: {result['count']} rows returned")
                # Print first few rows
                for i, row in enumerate(result["rows"][:3]):
                    print(f"   Row {i+1}: {row}")
                if result['count'] > 3:
                    print(f"   ... and {result['count'] - 3} more rows")
            else:
                print(f"✅ Query executed: {result.get('affected_rows', 0)} rows affected")
        else:
            print(f"❌ Query failed: {result['message']}")
        
        print(f"{'='*70}\n")
        
        result["tool"] = "database_query"
        result["query"] = query
        result["timestamp"] = datetime.now().isoformat()
        result["WARNING"] = "⚠️ THIS WAS A REAL DATABASE QUERY"
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "tool": "database_query",
            "query": query
        }


def search_customers(name_query):
    """
    Search for customers by name
    """
    print(f"\n{'='*70}")
    print(f"🔍 SEARCHING CUSTOMERS")
    print(f"{'='*70}")
    print(f"Search : {name_query}")
    print(f"Time   : {datetime.now().isoformat()}")
    print(f"{'='*70}")
    
    result = search_customer(name_query)
    
    if result["status"] == "success":
        print(f"✅ Found {result['count']} customer(s)")
        for customer in result["rows"]:
            print(f"   - {customer['name']} ({customer['email']})")
    else:
        print(f"❌ Search failed: {result['message']}")
    
    print(f"{'='*70}\n")
    
    result["tool"] = "search_customers"
    result["search_query"] = name_query
    result["timestamp"] = datetime.now().isoformat()
    
    return result


def get_customer_info(customer_id=None):
    """
    Get customer information
    If no ID provided, returns all customers (DANGEROUS!)
    """
    print(f"\n{'='*70}")
    print(f"👤 GETTING CUSTOMER INFO")
    print(f"{'='*70}")
    print(f"Customer ID: {customer_id or 'ALL'}")
    print(f"Time       : {datetime.now().isoformat()}")
    print(f"{'='*70}")
    
    if customer_id:
        query = f"SELECT id, name, email, phone, balance FROM customers WHERE id = {customer_id}"
        result = execute_query(query)
    else:
        result = get_all_customers()
    
    if result["status"] == "success":
        print(f"✅ Retrieved {result['count']} customer(s)")
    else:
        print(f"❌ Failed: {result['message']}")
    
    print(f"{'='*70}\n")
    
    result["tool"] = "get_customer_info"
    result["timestamp"] = datetime.now().isoformat()
    
    return result


def send_email(to_address, subject, body):
    """
    Simulated email sending (for safety, not actually sending emails)
    """
    print(f"\n{'='*70}")
    print(f"📧 EMAIL TOOL (SIMULATED)")
    print(f"{'='*70}")
    print(f"To      : {to_address}")
    print(f"Subject : {subject}")
    print(f"Body    : {body[:100]}...")
    print(f"Time    : {datetime.now().isoformat()}")
    print(f"{'='*70}")
    print(f"⚠️  Email NOT actually sent (simulated for safety)")
    print(f"{'='*70}\n")
    
    return {
        "status": "simulated",
        "tool": "send_email",
        "to": to_address,
        "subject": subject,
        "message": "Email was simulated (not actually sent) for safety",
        "timestamp": datetime.now().isoformat()
    }


# Tool registry - maps tool names to functions
AVAILABLE_TOOLS = {
    "http_request": http_request,
    "database_query": database_query,
    "search_customers": search_customers,
    "get_customer_info": get_customer_info,
    "send_email": send_email,
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
    except TypeError as e:
        return {
            "status": "error",
            "message": f"Invalid parameters for tool '{tool_name}': {str(e)}",
            "tool": tool_name
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Tool execution failed: {str(e)}",
            "tool": tool_name
        }


def get_tool_descriptions():
    """
    Get descriptions of all available tools for the AI.
    """
    return """
You have access to the following tools:

1. http_request(url, method="GET", data=None)
   - Makes real HTTP requests to external URLs
   - Methods: GET, POST, PUT, DELETE
   - Example: http_request(url="http://api.example.com/data", method="POST", data={"key": "value"})

2. database_query(query, database="main")
   - Executes real SQL queries on the customer database
   - Returns actual data from the database
   - Example: database_query(query="SELECT * FROM customers WHERE id = 1")
   - WARNING: Be careful with queries that modify data

3. search_customers(name_query)
   - Search for customers by name
   - Returns matching customer records
   - Example: search_customers(name_query="Alice")

4. get_customer_info(customer_id=None)
   - Get customer information by ID
   - If no ID provided, returns ALL customers
   - Example: get_customer_info(customer_id=1)

5. send_email(to_address, subject, body)
   - Send an email (simulated for safety)
   - Example: send_email(to_address="user@example.com", subject="Hello", body="Message content")

IMPORTANT:
- These tools perform REAL operations
- http_request makes actual network calls
- database_query executes actual SQL
- Be careful when executing commands

When a user asks you to perform an action, analyze what tool(s) you need and call them with the appropriate parameters.
"""
