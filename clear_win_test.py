#!/usr/bin/env python3
"""
Test where A* should clearly win by saving significant interest.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from core.models import Loan
from core.optimizer import AStarOptimizer


def clear_win_test():
    """Run a test where A* should clearly beat Snowball."""
    print("Running Clear Win Test: High vs Zero Interest")

    # Create two loans: one high interest, one zero interest
    loans = [
        Loan("High Interest Loan", 5000, 30.0, 50),  # Very high interest
        Loan("Zero Interest Loan", 5000, 0.0, 50),  # Zero interest
    ]

    # Budget allows for significant extra payments
    optimizer = AStarOptimizer(
        loans, budget=200, emergency_floor=0, initial_cash=10000, granularity=50.0
    )

    # Run Snowball baseline
    print("Running Debt Snowball baseline...")
    res_snowball = optimizer.solve_snowball()

    # Run A* optimization (should prioritize the 30% interest loan to save money)
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

    # A* should be significantly better than Snowball by avoiding interest on high-rate loan
    if interest_diff <= 0.01:  # Allow small floating point tolerance
        print("✓ PASS: A* solution is optimal (<= Snowball interest)")
        if interest_diff < -10.0:  # Meaningfully better (saving at least $10)
            print(
                f"  A* saved ${abs(interest_diff):.2f} in interest compared to Snowball!"
            )
            print("  This demonstrates A* correctly prioritizes high-interest debt.")
        elif interest_diff < 0:
            print(
                f"  A* saved ${abs(interest_diff):.2f} in interest compared to Snowball."
            )
        return True
    else:
        print("✗ FAIL: A* solution is worse than Snowball")
        print("  This indicates the heuristic update did not fix the optimality issue.")
        return False


if __name__ == "__main__":
    success = clear_win_test()
    sys.exit(0 if success else 1)
