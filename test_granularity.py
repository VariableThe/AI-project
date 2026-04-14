#!/usr/bin/env python3
"""
Test with finer granularity to see if A* can find better solutions
"""

from core.models import Loan
from core.optimizer import AStarOptimizer

print("=" * 80)
print("TESTING WITH FINER PAYMENT GRANULARITY")
print("=" * 80)

loans = [
    Loan("CC", 5000, 18.0, 150),
    Loan("Car", 15000, 6.5, 350),
    Loan("Student", 20000, 4.5, 200),
]

budget = 1000
cash = 2000
floor = 500
injections = {3: Loan("Medical", 2000, 0, 100)}

print("\nTesting with different granularities...\n")

for granularity in [500, 250, 100, 50]:
    print(f"Granularity: ${granularity}/month increments")
    
    loans_copy = [
        Loan("CC", 5000, 18.0, 150),
        Loan("Car", 15000, 6.5, 350),
        Loan("Student", 20000, 4.5, 200),
    ]
    
    optimizer = AStarOptimizer(loans_copy, budget, floor, cash, injections, granularity=granularity)
    
    import time
    start = time.time()
    res_snowball = optimizer.solve_snowball()
    snowball_time = time.time() - start
    
    start = time.time()
    res_astar = optimizer.solve()
    astar_time = time.time() - start
    
    print(f"  Snowball:     {res_snowball.month} months, ${res_snowball.g_cost:.2f} interest ({snowball_time:.3f}s)")
    print(f"  A* Optimal:   {res_astar.month} months, ${res_astar.g_cost:.2f} interest ({astar_time:.3f}s)")
    
    if res_astar.g_cost < res_snowball.g_cost:
        savings = res_snowball.g_cost - res_astar.g_cost
        print(f"  ✓ A* beats Snowball by ${savings:.2f}!")
    elif res_astar.g_cost > res_snowball.g_cost:
        diff = res_astar.g_cost - res_snowball.g_cost
        print(f"  ✗ A* loses to Snowball by ${diff:.2f}")
    else:
        print(f"  = Results are equal")
    
    print()

print("=" * 80)
print("Note: Finer granularity = more payment options = slower search but better solutions")
