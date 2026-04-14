#!/usr/bin/env python3
"""
Speed-optimized test with smaller numbers to finish quickly.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from core.models import Loan
from core.optimizer import AStarOptimizer


def speed_test():
    """Run a speed-optimized test."""
    print("Running Speed-Optimized Test")

    # Small loans that will resolve quickly
    loans = [
        Loan("High Interest", 1000, 12.0, 20),  # $1000 at 12% annual (1% monthly)
        Loan("Low Interest", 1000, 3.0, 20),  # $1000 at 3% annual (0.25% monthly)
    ]

    # Reasonable budget for extra payments
    optimizer = AStarOptimizer(
        loans, budget=100, emergency_floor=0, initial_cash=5000, granularity=25.0
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

    # A* should be better than or equal to Snowball
    if interest_diff <= 0.01:  # Allow small floating point tolerance
        print("✓ PASS: A* solution is optimal (<= Snowball interest)")
        if interest_diff < -0.1:  # Meaningfully better
            print(
                f"  A* saved ${abs(interest_diff):.2f} in interest compared to Snowball!"
            )
        return True
    else:
        print("✗ FAIL: A* solution is worse than Snowball")
        return False


if __name__ == "__main__":
    success = speed_test()
    sys.exit(0 if success else 1)
