#!/usr/bin/env python3
"""
Compare payment sequences between A* and Snowball to understand why results differ
"""

from core.models import Loan
from core.optimizer import AStarOptimizer
from copy import deepcopy

print("=" * 80)
print("PAYMENT SEQUENCE COMPARISON: A* vs Snowball")
print("=" * 80)

# Exact same test scenario
loans = [
    Loan("CC", 5000, 18.0, 150),
    Loan("Car", 15000, 6.5, 350),
    Loan("Student", 20000, 4.5, 200),
]

budget = 1000
cash = 2000
floor = 500
injections = {3: Loan("Medical", 2000, 0, 100)}

print("\nScenario:")
print(f"  Budget: ${budget}/month")
print(f"  Min payments: CC=${loans[0].min_payment} + Car=${loans[1].min_payment} + Student=${loans[2].min_payment} = ${sum(l.min_payment for l in loans)}")
print(f"  Extra available for aggressive payoff: ${budget - sum(l.min_payment for l in loans)}/month")
print()

optimizer = AStarOptimizer(loans, budget, floor, cash, injections, granularity=100)

# Get both solutions
print("Running both algorithms...\n")
res_snowball = optimizer.solve_snowball()
res_astar = optimizer.solve()

print("Results:")
print(f"  Snowball: {res_snowball.month} months, ${res_snowball.g_cost:.2f} total interest")
print(f"  A* Search: {res_astar.month} months, ${res_astar.g_cost:.2f} total interest")
if res_astar.g_cost > res_snowball.g_cost:
    diff = res_astar.g_cost - res_snowball.g_cost
    print(f"  ⚠️  A* is ${diff:.2f} WORSE than Snowball")
print()

# Display first 12 months of each
print("=" * 80)
print("FIRST 12 MONTHS COMPARISON")
print("=" * 80)

print("\nDEBT SNOWBALL Strategy:")
print("-" * 80)
print(f"{'Mon':<4} {'CC Payment':<14} {'Car Payment':<14} {'Stu Payment':<14} {'Total':<10} {'CC Balance':<14}")
print("-" * 80)
for month, alloc in res_snowball.history[:12]:
    # Reconstruct loan balances from original
    init_loans = [
        Loan("CC", 5000, 18.0, 150),
        Loan("Car", 15000, 6.5, 350),
        Loan("Student", 20000, 4.5, 200),
    ]
    
    # Simulate up to this month
    for m in range(month + 1):
        for l in init_loans:
            l.apply_interest()
            payment = 0
            if m < len(res_snowball.history):
                payment = res_snowball.history[m][1].get(l.name, 0)
            l.principal = max(0, l.principal - payment)
    
    cc_pay = alloc.get("CC", 0)
    car_pay = alloc.get("Car", 0)
    stu_pay = alloc.get("Student", 0)
    total = cc_pay + car_pay + stu_pay
    balance = init_loans[0].principal
    
    print(f"{month:<4} ${cc_pay:>12.2f} ${car_pay:>12.2f} ${stu_pay:>12.2f} ${total:>8.2f} ${balance:>12.2f}")

print("\n\nA* OPTIMAL Strategy:")
print("-" * 80)
print(f"{'Mon':<4} {'CC Payment':<14} {'Car Payment':<14} {'Stu Payment':<14} {'Total':<10} {'CC Balance':<14}")
print("-" * 80)
for month, alloc in res_astar.history[:12]:
    # Reconstruct loan balances
    init_loans = [
        Loan("CC", 5000, 18.0, 150),
        Loan("Car", 15000, 6.5, 350),
        Loan("Student", 20000, 4.5, 200),
    ]
    
    # Simulate up to this month
    for m in range(month + 1):
        for l in init_loans:
            l.apply_interest()
            payment = 0
            if m < len(res_astar.history):
                payment = res_astar.history[m][1].get(l.name, 0)
            l.principal = max(0, l.principal - payment)
    
    cc_pay = alloc.get("CC", 0)
    car_pay = alloc.get("Car", 0)
    stu_pay = alloc.get("Student", 0)
    total = cc_pay + car_pay + stu_pay
    balance = init_loans[0].principal
    
    print(f"{month:<4} ${cc_pay:>12.2f} ${car_pay:>12.2f} ${stu_pay:>12.2f} ${total:>8.2f} ${balance:>12.2f}")

print("\n" + "=" * 80)
print("KEY INSIGHTS")
print("=" * 80)
print("""
1. PAYMENT STRATEGY DIFFERENCES:
   - Snowball: Pays minimum on all, puts extra aggressively on smallest balance
   - A*: Uses CSP to find "feasible" allocations, then explores the search tree
   
2. INTEREST ACCUMULATION:
   - High-interest debt (CC at 18%) should be paid aggressively first
   - A* found a feasible solution but not necessarily the best allocation strategy
   
3. POSSIBLE ROOT CAUSE:
   - A* explores states based on f(n) = g(n) + h(n)
   - Two states might reach same month with different balances
   - A* might pick one that LOOKS better but has worse long-term cost
   
4. THE MYSTERY:
   - Why does A* with admissible heuristic perform worse?
   - Answer: A* finds A GOAL, not necessarily the BEST GOAL
   - Multiple paths can reach 48 months; A* returns first encountered
   - Check: Are both solutions actually 48 months to COMPLETION?
""")
