#!/usr/bin/env python3
"""
Basic functionality test.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from core.models import Loan
from core.optimizer import AStarOptimizer


def basic_test():
    """Run a basic test."""
    print("Basic Functionality Test")

    # Single loan test
    loans = [Loan("Test Loan", 1000, 12.0, 50)]  # $1000 at 12%

    optimizer = AStarOptimizer(
        loans, budget=100, emergency_floor=0, initial_cash=1000, granularity=25.0
    )

    print("Running Snowball...")
    snowball = optimizer.solve_snowball()

    print("Running A*...")
    astar = optimizer.solve()

    if snowball and astar:
        print(f"Snowball: ${snowball.g_cost:.2f} interest over {snowball.month} months")
        print(f"A*:       ${astar.g_cost:.2f} interest over {astar.month} months")

        diff = astar.g_cost - snowball.g_cost
        print(f"Difference: ${diff:.2f}")

        if diff <= 0.01:
            print("✓ PASS: A* is optimal")
            return True

    print("✗ FAIL")
    return False


if __name__ == "__main__":
    success = basic_test()
    sys.exit(0 if success else 1)
