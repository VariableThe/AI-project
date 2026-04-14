#!/usr/bin/env python3
"""
Check the full payoff timeline to see where the crossover happens
"""
from core.models import Loan
from core.optimizer import AStarOptimizer
from copy import deepcopy

loans = [
    Loan("CC", 5000, 18.0, 150),
    Loan("Car", 15000, 6.5, 350),
    Loan("Student", 20000, 4.5, 200),
]

budget = 1000
cash = 2000
floor = 500
injections = {3: Loan("Medical", 2000, 0, 100)}

optimizer = AStarOptimizer(loans, budget, floor, cash, injections, granularity=100)

res_snowball = optimizer.solve_snowball()
res_astar = optimizer.solve()

print("=" * 80)
print("FULL PAYOFF TIMELINE COMPARISON")
print("=" * 80)
print(f"\nSnowball: {res_snowball.month} months, ${res_snowball.g_cost:.2f} total interest")
print(f"A*:       {res_astar.month} months, ${res_astar.g_cost:.2f} total interest")
print(f"Difference: ${res_astar.g_cost - res_snowball.g_cost:.2f} (A* is WORSE)")

# Show last 20 months of allocations
print("\n" + "=" * 80)
print("FINAL MONTHS (Snowball months 29-48):")
print("=" * 80)

print(f"\n{'Mon':<4} {'Algorithm':<12} {'CC':<8} {'Car':<8} {'Stu':<8} {'Med':<8} {'Total':<8} {'Cum Interest':<15}")
print("-" * 90)

def calc_interest_month(loans_list, alloc, injections_dict, month, initial_loans):
    """Calculate interest for a specific month"""
    active_loans = deepcopy(initial_loans)
    
    for m in range(month + 1):
        if m in injections_dict:
            inj = injections_dict[m]
            if not any(l.name == inj.name for l in active_loans):
                active_loans.append(deepcopy(inj))
        
        active_loans = [l for l in active_loans if l.principal > 0]
        
        for l in active_loans:
            l.apply_interest()
            if m < len(loans_list):
                payment = loans_list[m][1].get(l.name, 0)
                l.principal = max(0, l.principal - payment)
    
    return active_loans

initial_loans = [Loan("CC", 5000, 18.0, 150), Loan("Car", 15000, 6.5, 350), Loan("Student", 20000, 4.5, 200)]

start_month = max(0, len(res_snowball.history) - 20)
for month in range(start_month, len(res_snowball.history)):
    snow_alloc = res_snowball.history[month][1]
    astar_alloc = res_astar.history[month][1] if month < len(res_astar.history) else {}
    
    print(f"{month:<4} {'Snowball':<12} ${snow_alloc.get('CC', 0):>6.0f} ${snow_alloc.get('Car', 0):>6.0f} ${snow_alloc.get('Student', 0):>6.0f} ${snow_alloc.get('Medical', 0):>6.0f} ${sum(snow_alloc.values()):>6.0f}", end="")
    print(f" {res_snowball.history[month][1]}")

print("\n\n" + "=" * 80)
print("KEY INSIGHT:")
print("=" * 80)
print("""
Both algorithms reach payoff at month 48, but with different cumulative interest.

The difference suggests that:
1. A*'s early advantage (better strategy in months 3-14) gets reversed
2. Snowball's conservative approach pays off in the long run
3. Paying the medical bill aggressively (Snowball) freesup budget later
4. A*'s focus on CC comes at expense of clearing Medical, affecting future months

This is a case where greedy local optimization (Snowball) beats
global search without perfect foresight (A*'s limited heuristic).
""")
