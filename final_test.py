#!/usr/bin/env python3
"""
Final verification test with reasonable granularity.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from core.models import Loan
from core.optimizer import AStarOptimizer


def final_test():
    """Run a final verification test."""
    print("Running Final Verification Test")

    # Create a scenario where A* should beat Snowball
    loans = [
        Loan("Expensive Debt", 3000, 18.0, 30),  # High interest
        Loan("Cheap Debt", 3000, 4.0, 30),  # Low interest
    ]

    # Use reasonable granularity to keep search space manageable
    optimizer = AStarOptimizer(
        loans, budget=150, emergency_floor=0, initial_cash=5000, granularity=25.0
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
        if interest_diff < -0.5:  # Meaningfully better
            print(
                f"  A* saved ${abs(interest_diff):.2f} in interest compared to Snowball!"
            )
            print("  This confirms the heuristic fix is working correctly.")
        elif interest_diff < 0:
            print(
                f"  A* saved ${abs(interest_diff):.2f} in interest compared to Snowball."
            )
        return True
    else:
        print("✗ FAIL: A* solution is worse than Snowball")
        print("  The heuristic may still not be working correctly.")
        return False


if __name__ == "__main__":
    success = final_test()
    sys.exit(0 if success else 1)
