#!/usr/bin/env python3
"""
Compare what decisions A* and Snowball make at each month
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

print("=" * 80)
print("DECISION TRACE: A* vs Snowball")
print("=" * 80)

# Run both
res_snowball = optimizer.solve_snowball()
res_astar = optimizer.solve()

print("\nMonth 3 Analysis (Medical Bill Injection):")
print("-" * 80)

# Get allocations at month 3
snow_month3 = res_snowball.history[3][1] if len(res_snowball.history) > 3 else {}
astar_month3 = res_astar.history[3][1] if len(res_astar.history) > 3 else {}

print(f"\nMonth 3 allocations:")
print(f"  Snowball: CC=${snow_month3.get('CC', 0):.0f}  Car=${snow_month3.get('Car', 0):.0f}  Student=${snow_month3.get('Student', 0):.0f}  Medical=${snow_month3.get('Medical', 0):.0f}")
print(f"  A*:       CC=${astar_month3.get('CC', 0):.0f}  Car=${astar_month3.get('Car', 0):.0f}  Student=${astar_month3.get('Student', 0):.0f}  Medical=${astar_month3.get('Medical', 0):.0f}")

# Show first 10 months side-by-side
print("\n" + "=" * 80)
print("First 10 Months Detailed Comparison")
print("=" * 80)

print(f"\n{'Mon':<4} {'Algorithm':<12} {'CC Pmt':<8} {'Car Pmt':<8} {'Stu Pmt':<8} {'Med Pmt':<8} {'Total':<8}")
print("-" * 80)

for month in range(min(10, len(res_snowball.history), len(res_astar.history))):
    snow_alloc = res_snowball.history[month][1]
    astar_alloc = res_astar.history[month][1]
    
    print(f"{month:<4} {'Snowball':<12} ${snow_alloc.get('CC', 0):>6.0f} ${snow_alloc.get('Car', 0):>6.0f} ${snow_alloc.get('Student', 0):>6.0f} ${snow_alloc.get('Medical', 0):>6.0f} ${sum(snow_alloc.values()):>6.0f}")
    print(f"{'':<4} {'A*':<12} ${astar_alloc.get('CC', 0):>6.0f} ${astar_alloc.get('Car', 0):>6.0f} ${astar_alloc.get('Student', 0):>6.0f} ${astar_alloc.get('Medical', 0):>6.0f} ${sum(astar_alloc.values()):>6.0f}")
    print()

# Calculate cumulative interest by month
print("\n" + "=" * 80)
print("Cumulative Interest Over Time")
print("=" * 80)

def calc_cumulative_interest(history, initial_loans, injections_dict):
    active_loans = deepcopy(initial_loans)
    cumulative = 0
    monthly = []
    for month, alloc in history:
        if month in injections_dict:
            inj = injections_dict[month]
            if not any(l.name == inj.name for l in active_loans):
                active_loans.append(deepcopy(inj))
        
        # Clean up zero-balance loans
        active_loans = [l for l in active_loans if l.principal > 0]
        
        month_interest = 0
        for l in active_loans:
            month_interest += l.apply_interest()
            payment = alloc.get(l.name, 0)
            l.principal = max(0, l.principal - payment)
        cumulative += month_interest
        monthly.append(cumulative)
    return monthly

snow_cumulative = calc_cumulative_interest(res_snowball.history, [Loan("CC", 5000, 18.0, 150), Loan("Car", 15000, 6.5, 350), Loan("Student", 20000, 4.5, 200)], injections)
astar_cumulative = calc_cumulative_interest(res_astar.history, [Loan("CC", 5000, 18.0, 150), Loan("Car", 15000, 6.5, 350), Loan("Student", 20000, 4.5, 200)], injections)

print(f"\n{'Month':<8} {'Snowball':<15} {'A*':<15} {'Difference':<15}")
print("-" * 55)
for m in range(min(15, len(snow_cumulative), len(astar_cumulative))):
    diff = astar_cumulative[m] - snow_cumulative[m]
    print(f"{m:<8} ${snow_cumulative[m]:>13.2f} ${astar_cumulative[m]:>13.2f} ${diff:>13.2f}")
