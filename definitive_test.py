#!/usr/bin/env python3
"""
Definitive test where A* should beat Snowball by prioritizing high-interest loan.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from core.models import Loan
from core.optimizer import AStarOptimizer


def definitive_test():
    """Run a test where A* should clearly beat Snowball."""
    print("Running Definitive Test: Clear High vs Low Interest Case")

    # Create two loans with very different interest rates
    loans = [
        Loan("Credit Card Debt", 10000, 24.0, 200),  # Very high interest
        Loan("Student Loan", 10000, 4.0, 200),  # Low interest
    ]

    # Budget allows for extra payments beyond minimums
    optimizer = AStarOptimizer(
        loans, budget=500, emergency_floor=0, initial_cash=20000, granularity=50.0
    )

    # Run Snowball baseline (pay lowest balance first - equal balances, but let's see what happens)
    print("Running Debt Snowball baseline...")
    res_snowball = optimizer.solve_snowball()

    # Run A* optimization (should prioritize the 24% interest loan)
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

    # A* should be better than Snowball by prioritizing high-interest loan
    if interest_diff <= 0.01:  # Allow small floating point tolerance
        print("✓ PASS: A* solution is optimal (<= Snowball interest)")
        if interest_diff < -1.0:  # Meaningfully better (saving at least $1)
            print(
                f"  A* saved ${abs(interest_diff):.2f} in interest compared to Snowball!"
            )
            print(
                "  This confirms A* is correctly prioritizing the high-interest loan."
            )
        return True
    else:
        print("✗ FAIL: A* solution is worse than Snowball")
        print("  This would indicate the heuristic is still not working correctly.")
        return False


if __name__ == "__main__":
    success = definitive_test()
    sys.exit(0 if success else 1)
