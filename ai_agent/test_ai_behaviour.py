#!/usr/bin/env python3
"""
Quick test to verify AI agent responds correctly to different prompt types
"""
import sys
import os

# Add ai_agent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_agent'))

from agent_app import AIAgent

def test_prompts():
    """Test various prompt types."""
    agent = AIAgent()
    
    # Check Ollama
    if not agent.check_ollama_available():
        print("\n❌ Ollama not available. Please start it first.")
        print("   Run: ollama serve")
        print("   Then: ollama pull llama3")
        return
    
    test_cases = [
        {
            "prompt": "What is 5+5?",
            "expected_behavior": "Should answer directly WITHOUT calling tools",
            "should_call_tool": False
        },
        {
            "prompt": "Hello",
            "expected_behavior": "Should greet WITHOUT calling tools",
            "should_call_tool": False
        },
        {
            "prompt": "Get customer with ID 1",
            "expected_behavior": "Should call get_customer_info tool",
            "should_call_tool": True
        },
        {
            "prompt": "Search for Alice",
            "expected_behavior": "Should call search_customers tool",
            "should_call_tool": True
        }
    ]
    
    print("\n" + "="*70)
    print("TESTING AI AGENT BEHAVIOR")
    print("="*70 + "\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─'*70}")
        print(f"Test {i}: {test['prompt']}")
        print(f"Expected: {test['expected_behavior']}")
        print(f"{'─'*70}")
        
        result = agent.process_prompt(test['prompt'])
        
        tool_was_called = result.get('tool_called') is not None
        
        if tool_was_called == test['should_call_tool']:
            print(f"✅ PASS: Behavior is correct")
            if tool_was_called:
                print(f"   Tool called: {result['tool_called']}")
            else:
                ai_resp = result.get('ai_response', '')
                print(f"   AI Response: {ai_resp[:100]}...")
        else:
            print(f"❌ FAIL: Unexpected behavior")
            if tool_was_called:
                print(f"   ERROR: Tool was called ({result['tool_called']}) but shouldn't have been")
            else:
                print(f"   ERROR: No tool was called but one should have been")
        
        print()
    
    print("\n" + "="*70)
    print("TESTING COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_prompts()