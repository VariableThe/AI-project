#!/usr/bin/env python3
"""
Debug test to see what's happening in the search.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from core.models import Loan
from core.optimizer import AStarOptimizer


def debug_test():
    """Run a debug test with verbose output."""
    print("Running Debug Test - Small Problem")

    # Very small problem that should resolve nearly instantly
    loans = [Loan("Debug Loan", 10, 12.0, 5)]  # $10 at 12% annual

    optimizer = AStarOptimizer(
        loans, budget=20, emergency_floor=0, initial_cash=100, granularity=5.0
    )

    print(f"Loan: {loans[0]}")
    print(f"Monthly rate: {loans[0].standard_rate * 100:.2f}%")
    print(f"Interest first month: ${loans[0].principal * loans[0].standard_rate:.2f}")
    print(f"Min payment: ${loans[0].min_payment}")

    # Run Snowball baseline
    print("\nRunning Debt Snowball baseline...")
    res_snowball = optimizer.solve_snowball()

    # Run A* optimization
    print("\nRunning A* Optimal Search...")
    res_astar = optimizer.solve()

    # Display results
    print(f"\nResults:")
    print(
        f"Snowball - Interest: ${res_snowball.g_cost:.2f}, Months: {res_snowball.month}"
    )
    print(f"A*       - Interest: ${res_astar.g_cost:.2f}, Months: {res_astar.month}")

    interest_diff = res_astar.g_cost - res_snowball.g_cost
    print(f"Interest Difference (A* - Snowball): ${interest_diff:.2f}")

    # Check if A* is better than or equal to Snowball
    if interest_diff <= 0.01:  # Allow small floating point tolerance
        print("✓ PASS: A* solution is optimal (<= Snowball interest)")
        return True
    else:
        print("✗ FAIL: A* solution is worse than Snowball")
        return False


if __name__ == "__main__":
    success = debug_test()
    sys.exit(0 if success else 1)
