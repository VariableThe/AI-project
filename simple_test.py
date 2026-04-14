#!/usr/bin/env python3
"""
Simple test to verify A* works with the updated heuristic.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from core.models import Loan
from core.optimizer import AStarOptimizer


def simple_test():
    """Run a simple test case."""
    print("Running Simple Test")

    # Create a simple loan scenario
    loans = [Loan("Test Loan", 1000, 5.0, 50)]  # $1000 at 5% annual, $50 min payment

    optimizer = AStarOptimizer(
        loans, budget=200, emergency_floor=100, initial_cash=1000, granularity=50.0
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
    success = simple_test()
    sys.exit(0 if success else 1)
