"""
run_comprehensive_tests.py - Complete Test Runner

Runs all comprehensive test cases and generates detailed report.
"""

import requests
import json
import time
from datetime import datetime
from comprehensive_test_cases import ALL_TEST_CASES, TEST_STATS

BASE_URL = "http://localhost:5001"

gb_test=0;
gb_passed=0;
gb_failed=0;
gb_success_rate=0;

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
            
            return {
                'test_case': test_case,
                'actual_action': actual_action,
                'risk_score': data.get('risk_score', 0),
                'layer_scores': data.get('layer_scores', {}),
                'threats': data.get('threats', []),
                'passed': passed,
                'response_time_ms': elapsed_ms,
                'timestamp': datetime.now().isoformat()
            }
            
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
            risk = result['risk_score']
            actual = result['actual_action']
            expected = test['expected']
            
            print(f"{status} {test['category']:40s} | "
                  f"Expected: {expected:6s} | Got: {actual:6s} | Risk: {risk:5.1f}")
    
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
            print("   Start with: python security_proxy_v2.py\n")
            return
        
        # Run tests by category
        categories = [
            ("SQL Injection", lambda t: "SQL Injection" in t['category']),
            ("Data Exfiltration", lambda t: "Data Exfiltration" in t['category']),
            ("Jailbreak", lambda t: "Jailbreak" in t['category']),
            ("Code Injection", lambda t: "Code Injection" in t['category']),
            ("Business", lambda t: "Business" in t['category']),
            ("Educational", lambda t: "Educational" in t['category']),
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
        gb_total=total; gb_passed=passed; gb_failed=failed; gb_success_rate=passed/total*100
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
        layers = {}
        for result in self.results:
            if result.get('layer_scores'):
                for layer, score in result['layer_scores'].items():
                    if layer not in layers:
                        layers[layer] = []
                    layers[layer].append(score)
        
        for layer, scores in layers.items():
            active = sum(1 for s in scores if s > 0)
            avg = sum(scores) / len(scores)
            print(f"  {layer:20s}: {active:3d}/{len(scores)} active, avg: {avg:.2f}")
        
        # Failed tests
        if failed > 0:
            print(f"\n❌ Failed Tests ({failed}):")
            for result in self.results:
                if not result['passed']:
                    test = result['test_case']
                    actual = result.get('actual_action', 'error')
                    print(f"  • {test['category']}")
                    print(f"    Expected: {test['expected']}, Got: {actual}")
                    if result.get('risk_score'):
                        print(f"    Risk Score: {result['risk_score']:.1f}")
        
        print("\n" + "="*90 + "\n")
    
    def _save_results(self):
        """Save results to JSON."""
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_results_{timestamp}.json"
        
        output = {

            'Total Tests': {gb_test},
            'Passed': {gb_passed } ,
            'Failed': {gb_failed } ,
            'Success Rate': {gb_success_rate},

            'test_run': {
                'timestamp': self.start_time.isoformat(),
                'total_tests': len(self.results),
                'passed': sum(1 for r in self.results if r['passed']),
                'failed': sum(1 for r in self.results if not r['passed']),
            },
            'results': self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"💾 Results saved to: {filename}\n")


def main():
    """Run comprehensive tests."""
    runner = ComprehensiveTestRunner()
    runner.run_all_tests()


if __name__ == "__main__":
    main()
