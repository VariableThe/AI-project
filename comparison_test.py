#!/usr/bin/env python3
"""
Test case where A* should outperform Snowball significantly.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from core.models import Loan
from core.optimizer import AStarOptimizer


def comparison_test():
    """Run a test where A* should beat Snowball."""
    print("Running Comparison Test (High vs Low Interest Loans)")

    # Create two loans: one high interest, one low interest
    loans = [
        Loan("High Interest Loan", 5000, 15.0, 50),  # $5000 at 15% - expensive
        Loan("Low Interest Loan", 5000, 3.0, 50),  # $5000 at 3%  - cheap
    ]

    # Budget allows significant extra payments
    optimizer = AStarOptimizer(
        loans, budget=300, emergency_floor=0, initial_cash=10000, granularity=25.0
    )

    # Run Snowball baseline (will pay lowest balance first - equal balances, so order may vary)
    print("Running Debt Snowball baseline...")
    res_snowball = optimizer.solve_snowball()

    # Run A* optimization (should prioritize high interest loan)
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
        if interest_diff < -0.01:  # Significantly better
            print(
                f"  A* saved ${abs(interest_diff):.2f} in interest compared to Snowball!"
            )
        return True
    else:
        print("✗ FAIL: A* solution is worse than Snowball")
        return False


if __name__ == "__main__":
    success = comparison_test()
    sys.exit(0 if success else 1)
