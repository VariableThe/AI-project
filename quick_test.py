#!/usr/bin/env python3
"""
Very quick test to verify basic functionality.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from core.models import Loan
from core.optimizer import AStarOptimizer


def quick_test():
    """Run a very quick test case."""
    print("Running Quick Test")

    # Create a simple loan scenario that should resolve quickly
    loans = [Loan("Quick Loan", 100, 12.0, 25)]  # Small balance, high rate

    # High budget relative to debt for quick resolution
    optimizer = AStarOptimizer(
        loans, budget=100, emergency_floor=0, initial_cash=500, granularity=25.0
    )

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
    success = quick_test()
    sys.exit(0 if success else 1)
