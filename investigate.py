#!/usr/bin/env python3
"""
Investigation: Why is A* performing worse than Snowball?
Analyzing the heuristic function admissibility
"""

from core.models import Loan
from core.optimizer import AStarOptimizer

print("=" * 70)
print("HEURISTIC ADMISSIBILITY INVESTIGATION")
print("=" * 70)

# Create test loans
cc = Loan("CC", 5000, 18.0, 150)
car = Loan("Car", 15000, 6.5, 350)
student = Loan("Student", 20000, 4.5, 200)

print("\n1. Testing Heuristic Function (estimated remaining interest)")
print("-" * 70)

# Simulate the heuristic for each loan
loans = [cc, car, student]
for loan in loans:
    h_est = loan.get_heuristic_interest()
    print(f"\n{loan.name}:")
    print(f"  Principal: ${loan.principal:.2f}")
    print(f"  APR: {loan.standard_rate * 12 * 100:.2f}%")
    print(f"  Min Payment: ${loan.min_payment:.2f}")
    print(f"  Estimated remaining interest: ${h_est:.2f}")
    
    # Calculate actual minimum payment payoff time
    temp_p = loan.principal
    months = 0
    actual_interest = 0
    while temp_p > 0.01 and months < 300:
        interest = temp_p * loan.standard_rate
        actual_interest += interest
        temp_p = temp_p + interest - loan.min_payment
        months += 1
    
    print(f"  Actual payoff (min payments): {months} months, ${actual_interest:.2f} interest")
    print(f"  Heuristic error: ${abs(h_est - actual_interest):.2f}")
    if h_est > actual_interest:
        print(f"  ⚠️  OVERESTIMATE - Heuristic is NOT ADMISSIBLE")
    else:
        print(f"  ✓ UNDERESTIMATE - Heuristic is admissible")

print("\n" + "=" * 70)
print("2. Comparing A* vs Snowball - Detailed Trace")
print("=" * 70)

loans = [
    Loan("CC", 5000, 18.0, 150),
    Loan("Car", 15000, 6.5, 350),
    Loan("Student", 20000, 4.5, 200),
]

optimizer = AStarOptimizer(loans, 1000, 500, 2000, {}, granularity=100)

print("\nA* SEARCH TRACE (first 10 states explored):")
# We'll manually trace the A* algorithm
from copy import deepcopy
import heapq
from core.models import State
from core.solver import ConstraintSolver

start_state = State(0, deepcopy(loans), 0.0)
frontier = [start_state]
explored = {}
state_count = 0

while frontier and state_count < 10:
    current = heapq.heappop(frontier)
    state_id = current.get_id()
    
    print(f"\nState #{state_count}: Month {current.month}")
    print(f"  Loans: {[f'{l.name}(${l.principal:.0f})' for l in current.loans if l.principal > 0]}")
    print(f"  g(n)={current.g_cost:.2f}, h(n)={current.h_cost:.2f}, f(n)={current.f_cost:.2f}")
    
    if current.is_goal():
        print(f"  *** GOAL REACHED ***")
        break
        
    if state_id in explored and explored[state_id] <= current.g_cost:
        print(f"  [Skip: Already explored]")
        continue
    explored[state_id] = current.g_cost
    
    # Generate successors
    active_loans = deepcopy(current.loans)
    solver = ConstraintSolver(active_loans, 1000, 500, 2000 + (1000 * current.month), granularity=100)
    allocations = solver.get_valid_allocations()
    
    added = 0
    for alloc in allocations[:2]:  # Show first 2 allocations
        next_loans = deepcopy(active_loans)
        interest_paid = 0
        for l in next_loans:
            interest_paid += l.apply_interest()
            payment = alloc.get(l.name, 0)
            l.principal = max(0, l.principal - payment)
        
        next_state = State(current.month + 1, next_loans, current.g_cost + interest_paid, current.history + [(current.month, alloc)])
        heapq.heappush(frontier, next_state)
        added += 1
    
    print(f"  Generated {added}+ successors, frontier size: {len(frontier)}")
    state_count += 1

print("\n" + "=" * 70)
print("ANALYSIS SUMMARY")
print("=" * 70)
print("""
Key Findings:
1. The heuristic might be OVERESTIMATING remaining costs
2. This makes A* expand more states than necessary
3. A* might return first goal found, not cheapest goal
4. Snowball's greedy approach works well for high-interest debt

Recommended Fix:
- Verify heuristic admissibility: h(n) ≤ actual remaining cost
- Modify termination: Keep exploring until goal has lowest f(n)
- Or: Scale down granularity for finer payment allocations
""")
