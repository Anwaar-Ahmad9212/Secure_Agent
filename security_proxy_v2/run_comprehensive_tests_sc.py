"""
run_comprehensive_tests.py - Complete Test Runner (FIXED)

Runs all comprehensive test cases and generates detailed report.
FIXED: JSON serialization error for set/datetime types
"""

import requests
import json
import time
from datetime import datetime
from comprehensive_test_cases import ALL_TEST_CASES, TEST_STATS


BASE_URL = "http://localhost:5001"


def convert_to_json_serializable(obj):
    """Convert non-JSON-serializable types to JSON-compatible types."""
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    else:
        return obj


class ComprehensiveTestRunner:
    """Run comprehensive test suite."""
    
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
    
    def test_prompt(self, test_case: dict) -> dict:
        """Test a single prompt."""
        try:
            start = time.time()
            response = requests.post(
                f"{BASE_URL}/validate",
                json={"prompt": test_case['prompt']},
                timeout=10
            )
            elapsed_ms = (time.time() - start) * 1000
            
            data = response.json()
            actual_action = data.get('action', 'unknown')
            
            passed = actual_action == test_case['expected']
            
            result = {
                'test_case': test_case,
                'actual_action': actual_action,
                'categorical_results': data.get('categorical_results', {}),
                'triggered_layers': data.get('triggered_layers', []),
                'signals': data.get('signals', {}),
                'threats': data.get('threats', []),
                'passed': passed,
                'response_time_ms': elapsed_ms,
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            return {
                'test_case': test_case,
                'error': str(e),
                'passed': False,
                'timestamp': datetime.now().isoformat()
            }
    
    def print_result(self, result: dict):
        """Print test result."""
        test = result['test_case']
        status = "✅" if result['passed'] else "❌"
        
        if result.get('error'):
            print(f"{status} {test['category']:40s} | ERROR: {result['error']}")
        else:
            actual = result['actual_action']
            expected = test['expected']
            
            print(f"{status} {test['category']:40s} | "
                  f"Expected: {expected:6s} | Got: {actual:6s}")
    
    def run_all_tests(self):
        """Run all comprehensive tests."""
        print("\n" + "="*90)
        print("🧪 COMPREHENSIVE TEST SUITE")
        print("="*90)
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Tests: {TEST_STATS['total_tests']}")
        print(f"Expected: Block={TEST_STATS['expected_blocks']}, "
              f"Alert={TEST_STATS['expected_alerts']}, "
              f"Allow={TEST_STATS['expected_allows']}")
        print("="*90 + "\n")
        
        # Check server
        try:
            requests.get(f"{BASE_URL}/health", timeout=2)
            print("✅ Server is running\n")
        except:
            print("❌ Server is NOT running!")
            print("   Start with: python security_proxy_v2_scoreless.py\n")
            return
        
        # Run tests by category
        categories = [
            ("SQL Injection", lambda t: "SQL Injection" in t['category']),
            ("Data Exfiltration", lambda t: "Data Exfiltration" in t['category']),
            ("Jailbreak", lambda t: "Jailbreak" in t['category']),
            ("Code Injection", lambda t: "Code Injection" in t['category']),
            ("Business", lambda t: "Business" in t['category'] and "Mixed" not in t['category']),
            ("Educational", lambda t: "Educational" in t['category'] and "Mixed" not in t['category']),
            ("Mixed Intent", lambda t: "Mixed" in t['category']),
            ("Real-World Hacks", lambda t: "Real Hack" in t['category']),
            ("Normal Queries", lambda t: "Normal" in t['category']),
            ("Edge Cases", lambda t: "Edge Case" in t['category']),
        ]
        
        for cat_name, cat_filter in categories:
            cat_tests = [t for t in ALL_TEST_CASES if cat_filter(t)]
            if not cat_tests:
                continue
            
            print(f"\n📋 Category: {cat_name}")
            print("-" * 90)
            
            for test in cat_tests:
                result = self.test_prompt(test)
                self.results.append(result)
                self.print_result(result)
        
        # Print summary
        self._print_summary()
        
        # Save results
        self._save_results()
    
    def _print_summary(self):
        """Print test summary."""
        print("\n" + "="*90)
        print("📊 TEST SUMMARY")
        print("="*90)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {passed/total*100:.1f}%")
        
        # Response time stats
        times = [r['response_time_ms'] for r in self.results if r.get('response_time_ms')]
        if times:
            print(f"\nResponse Times:")
            print(f"  Min: {min(times):.1f}ms")
            print(f"  Max: {max(times):.1f}ms")
            print(f"  Avg: {sum(times)/len(times):.1f}ms")
        
        # Layer performance
        print(f"\nLayer Contributions:")
        all_triggered = []
        for result in self.results:
            layers = result.get('triggered_layers', [])
            all_triggered.extend(layers)
        
        if all_triggered:
            from collections import Counter
            layer_counts = Counter(all_triggered)
            for layer, count in layer_counts.most_common():
                print(f"  {layer:20s}: triggered {count:3d} times")
        
        # Failed tests breakdown
        if failed > 0:
            print(f"\n❌ Failed Tests ({failed}):")
            for result in self.results:
                if not result['passed']:
                    test = result['test_case']
                    actual = result.get('actual_action', 'error')
                    print(f"  • {test['category']}")
                    print(f"    Expected: {test['expected']}, Got: {actual}")
        
        print("\n" + "="*90 + "\n")
    
    def _save_results(self):
        """Save results to JSON (with proper serialization)."""
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_results_{timestamp}.json"
        
        output = {
            'test_run': {
                'timestamp': self.start_time.isoformat(),
                'total_tests': len(self.results),
                'passed': sum(1 for r in self.results if r['passed']),
                'failed': sum(1 for r in self.results if not r['passed']),
            },
            'results': self.results
        }
        
        # CRITICAL FIX: Convert all non-serializable types
        output = convert_to_json_serializable(output)
        
        try:
            with open(filename, 'w') as f:
                json.dump(output, f, indent=2)
            print(f"💾 Results saved to: {filename}\n")
        except Exception as e:
            print(f"❌ Error saving results: {e}")
            # Try to save without formatting
            try:
                with open(filename, 'w') as f:
                    json.dump(output, f)
                print(f"💾 Results saved (unformatted) to: {filename}\n")
            except Exception as e2:
                print(f"❌ Could not save results: {e2}\n")


def main():
    """Run comprehensive tests."""
    runner = ComprehensiveTestRunner()
    runner.run_all_tests()


if __name__ == "__main__":
    main()