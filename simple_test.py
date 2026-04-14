#!/usr/bin/env python3
"""
Simplified test of the loan optimizer
"""
import sys
sys.setrecursionlimit(10000)

from core.models import Loan
from core.optimizer import AStarOptimizer

print("=" * 60)
print("AI LOAN REPAYMENT OPTIMIZER - TEST RUN")
print("=" * 60)

# Define test scenario
loans = [
    Loan("Credit Card", 5000, 18.0, 150),
    Loan("Car Loan", 15000, 6.5, 350), 
    Loan("Student Loan", 20000, 4.5, 200),
]

budget = 1000
cash = 2000
floor = 500
injections = {3: Loan("Medical Bill", 2000, 0, 100)}

print("\nInitial Loans:")
for loan in loans:
    print(f"  - {loan.name}: ${loan.principal:.2f} @ {loan.standard_rate*12*100:.1f}% APR")

print(f"\nBudget: ${budget}/month, Cash: ${cash}, Emergency Floor: ${floor}")
print(f"Injections: Medical Bill ($2000) in Month 3")

print("\n" + "=" * 60)
print("RUNNING OPTIMIZATION")
print("=" * 60)

optimizer = AStarOptimizer(loans, budget, floor, cash, injections, granularity=100)

print("\n[1] Simulating Debt Snowball (baseline)...")
try:
    res_snowball = optimizer.solve_snowball()
    if res_snowball:
        print(f"    Snowball: {res_snowball.month} months, ${res_snowball.g_cost:.2f} interest")
    else:
        print("    Snowball: Failed to find solution")
except Exception as e:
    print(f"    ERROR in Snowball: {e}")
    res_snowball = None

print("\n[2] Running A* Optimal Search...")
import time
start = time.time()
try:
    res_astar = optimizer.solve()
    elapsed = time.time() - start
    if res_astar:
        print(f"    A* Search: {res_astar.month} months, ${res_astar.g_cost:.2f} interest")
        print(f"    Time taken: {elapsed:.2f}s")
        if res_snowball:
            savings = res_snowball.g_cost - res_astar.g_cost
            print(f"    Savings vs Snowball: ${savings:.2f}")
    else:
        print("    A*: Failed to find solution")
        print(f"    Time taken: {elapsed:.2f}s")
except Exception as e:
    elapsed = time.time() - start
    print(f"    ERROR in A*: {e}")
    print(f"    Time taken: {elapsed:.2f}s")
    import traceback
    traceback.print_exc()
    res_astar = None

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
if res_snowball and res_astar:
    print(f"✓ Both strategies found solutions")
    print(f"  Snowball: {res_snowball.month}mo, ${res_snowball.g_cost:.2f} interest")  
    print(f"  A* (Optimal): {res_astar.month}mo, ${res_astar.g_cost:.2f} interest")
    if res_astar.g_cost < res_snowball.g_cost:
        savings = res_snowball.g_cost - res_astar.g_cost
        pct = (savings/res_snowball.g_cost)*100
        print(f"  A* saves ${savings:.2f} ({pct:.1f}%) vs Snowball!")
elif res_snowball:
    print(f"⚠ Only Snowball found solution: {res_snowball.month}mo, ${res_snowball.g_cost:.2f}")
elif res_astar:
    print(f"⚠ Only A* found solution: {res_astar.month}mo, ${res_astar.g_cost:.2f}")
else:
    print(f"✗ No solution found")

print()
