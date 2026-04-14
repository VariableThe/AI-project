#!/usr/bin/env python3
"""
Edge case tests for the A* loan optimizer with updated heuristic.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from core.models import Loan
from core.optimizer import AStarOptimizer


def test_case(
    name, loans, budget, cash, floor, injections=None, expected_behavior=None
):
    """Run a test case and return results."""
    print(f"\n{'=' * 60}")
    print(f"Testing: {name}")
    print(f"{'=' * 60}")

    granularity = 50.0  # Smaller granularity for better precision in tests
    injections = injections or {}

    try:
        optimizer = AStarOptimizer(loans, budget, floor, cash, injections, granularity)

        # Run Snowball baseline
        print("Running Debt Snowball baseline...")
        res_snowball = optimizer.solve_snowball()

        # Run A* optimization
        print("Running A* Optimal Search...")
        res_astar = optimizer.solve()

        # Display results
        print(f"\nResults:")
        print(
            f"Snowball - Interest: ${res_snowball.g_cost:.2f}, Months: {res_snowball.month}"
            if res_snowball
            else "Snowball: No solution"
        )
        print(
            f"A*       - Interest: ${res_astar.g_cost:.2f}, Months: {res_astar.month}"
            if res_astar
            else "A*: No solution"
        )

        if res_astar and res_snowball:
            interest_diff = res_astar.g_cost - res_snowball.g_cost
            print(f"Interest Difference (A* - Snowball): ${interest_diff:.2f}")

            # Check if A* is better than or equal to Snowball (should be <= 0 for optimal)
            if interest_diff <= 0.01:  # Allow small floating point tolerance
                print("✓ PASS: A* solution is optimal (<= Snowball interest)")
                return True
            else:
                print("✗ FAIL: A* solution is worse than Snowball")
                return False
        elif res_astar and not res_snowball:
            print("✓ PASS: A* found solution when Snowball failed")
            return True
        elif not res_astar and res_snowball:
            print("! INFO: Snowball found solution but A* did not (may indicate issue)")
            return False
        else:
            print("! INFO: Neither algorithm found solution")
            return False

    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


def run_all_tests():
    """Run all edge case tests."""
    print("Running Edge Case Tests for A* Loan Optimizer")
    print("Note: Testing that A* finds solutions with interest <= Snowball baseline")

    passed = 0
    total = 0

    # Test 1: Zero interest loan
    total += 1
    loans = [Loan("Zero Interest Loan", 1000, 0.0, 50)]  # 0% interest
    if test_case("Zero Interest Loan", loans, budget=200, cash=1000, floor=100):
        passed += 1

    # Test 2: High interest loan
    total += 1
    loans = [Loan("High Interest Loan", 1000, 24.0, 50)]  # 24% interest
    if test_case("High Interest Loan", loans, budget=200, cash=1000, floor=100):
        passed += 1

    # Test 3: Introductory rate expiration
    total += 1
    loans = [
        Loan("Intro Rate Loan", 1000, 12.0, 50, intro_rate=0.0, intro_duration=6)
    ]  # 0% for 6 months, then 12%
    if test_case(
        "Introductory Rate Expiration", loans, budget=200, cash=1000, floor=100
    ):
        passed += 1

    # Test 4: Budget equals minimum payments (no extra payment possible)
    total += 1
    loans = [Loan("Tight Budget Loan", 1000, 5.0, 100)]  # Min payment = budget
    if test_case("Budget Equals Minimum", loans, budget=100, cash=1000, floor=100):
        passed += 1

    # Test 5: Budget significantly higher than minimum payments
    total += 1
    loans = [
        Loan("Generous Budget Loan", 1000, 5.0, 20)
    ]  # Min payment much less than budget
    if test_case("High Budget Loan", loans, budget=200, cash=1000, floor=100):
        passed += 1

    # Test 6: Emergency fund constraint active
    total += 1
    loans = [Loan("Emergency Constraint Loan", 500, 5.0, 50)]
    if test_case(
        "Emergency Fund Active", loans, budget=100, cash=200, floor=150
    ):  # Cash-floor = 50 < budget
        passed += 1

    # Test 7: Dynamic injection scenario
    total += 1
    loans = [Loan("Initial Loan", 1000, 5.0, 50)]
    injections = {3: Loan("Sudden Expense", 500, 0.0, 25)}  # Injection at month 3
    if test_case(
        "Dynamic Injection",
        loans,
        budget=200,
        cash=1000,
        floor=100,
        injections=injections,
    ):
        passed += 1

    # Test 8: Multiple loans with different characteristics
    total += 1
    loans = [
        Loan("Credit Card", 2000, 18.0, 50),
        Loan("Car Loan", 10000, 5.0, 200),
        Loan("Personal Loan", 5000, 8.0, 100),
    ]
    if test_case("Multiple Loans", loans, budget=500, cash=20000, floor=1000):
        passed += 1

    # Test 9: Already paid off loans (edge case)
    total += 1
    loans = [Loan("Paid Off Loan", 0.0, 5.0, 0)]  # Zero principal
    if test_case("Already Paid Off", loans, budget=100, cash=1000, floor=100):
        passed += 1

    # Test 10: Very small balances
    total += 1
    loans = [Loan("Small Balance Loan", 10.0, 5.0, 5)]  # Very small balance
    if test_case("Very Small Balance", loans, budget=50, cash=1000, floor=100):
        passed += 1

    # Summary
    print(f"\n{'=' * 60}")
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    print(f"{'=' * 60}")

    if passed == total:
        print("🎉 All tests passed! The A* heuristic appears to be working correctly.")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please review the results above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
