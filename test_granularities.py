#!/usr/bin/env python3
"""
Test A* vs Snowball with different payment granularities
"""

from core.models import Loan
from core.optimizer import AStarOptimizer
from copy import deepcopy
import time

print("=" * 80)
print("TESTING DIFFERENT GRANULARITIES")
print("=" * 80)
print()

test_cases = [
    ("Coarse ($500)", 500),
    ("Medium ($100)", 100),
    ("Fine ($50)", 50),
    ("Very Fine ($10)", 10),
]

for label, granularity in test_cases:
    loans = [
        Loan("CC", 5000, 18.0, 150),
        Loan("Car", 15000, 6.5, 350),
        Loan("Student", 20000, 4.5, 200),
    ]
    
    budget = 1000
    floor = 500
    cash = 2000
    injections = {3: Loan("Medical", 2000, 0, 100)}
    
    optimizer = AStarOptimizer(loans, budget, floor, cash, injections, granularity=granularity)
    
    print(f"{label} (granularity=${granularity})")
    
    start = time.time()
    res_snowball = optimizer.solve_snowball()
    snowball_time = time.time() - start
    
    start = time.time()
    res_astar = optimizer.solve()
    astar_time = time.time() - start
    
    if res_snowball:
        print(f"  Snowball:   {res_snowball.month} mo, ${res_snowball.g_cost:>10.2f} ({snowball_time:.2f}s)")
    else:
        print(f"  Snowball:   Failed")
    
    if res_astar:
        print(f"  A* Optimal: {res_astar.month} mo, ${res_astar.g_cost:>10.2f} ({astar_time:.2f}s)")
        if res_snowball:
            diff = res_astar.g_cost - res_snowball.g_cost
            pct = (diff / res_snowball.g_cost) * 100
            if diff < 0:
                print(f"  ✓ A* BEATS Snowball by ${-diff:.2f} ({-pct:.1f}%)")
            else:
                print(f"  ✗ A* loses to Snowball by ${diff:.2f} ({pct:.1f}%)")
    else:
        print(f"  A* Optimal: Failed")
    
    print()
