#!/usr/bin/env python3
"""
Verify if Month 46 goal is truly complete payoff
"""

from core.models import Loan, State
from core.solver import ConstraintSolver
from copy import deepcopy
import heapq

loans = [
    Loan("CC", 5000, 18.0, 150),
    Loan("Car", 15000, 6.5, 350),
    Loan("Student", 20000, 4.5, 200),
]

budget = 1000
floor = 500
cash = 2000
injections = {3: Loan("Medical", 2000, 0, 100)}  # ADD INJECTION!

# Implement A* and capture the goal state
start_state = State(0, deepcopy(loans), 0.0)
frontier = [start_state]
explored = {}
goal_state = None

while frontier:
    current = heapq.heappop(frontier)
    
    if current.is_goal():
        goal_state = current
        break
    
    state_id = current.get_id()
    if state_id in explored and explored[state_id] <= current.g_cost:
        continue
    explored[state_id] = current.g_cost
    
    active_loans = deepcopy(current.loans)
    # HANDLE INJECTIONS
    if current.month in injections:
        inj_loan = injections[current.month]
        if not any(l.name == inj_loan.name for l in active_loans):
            active_loans.append(deepcopy(inj_loan))
    
    solver = ConstraintSolver(
        active_loans,
        budget,
        floor,
        cash + (budget * current.month),
        granularity=100
    )
    allocations = solver.get_valid_allocations()
    
    for alloc in allocations:
        next_loans = deepcopy(active_loans)
        interest_paid = 0
        
        for l in next_loans:
            interest_paid += l.apply_interest()
            payment = alloc.get(l.name, 0)
            l.principal = max(0, l.principal - payment)
        
        next_state = State(
            current.month + 1,
            next_loans,
            current.g_cost + interest_paid,
            current.history + [(current.month, alloc)]
        )
        heapq.heappush(frontier, next_state)

print("=" * 80)
print("GOAL STATE VERIFICATION")
print("=" * 80)
print()

if goal_state:
    print(f"Goal found at Month {goal_state.month}")
    print(f"Total interest paid: ${goal_state.g_cost:.2f}")
    print()
    print("Loan balances at goal:")
    for loan in goal_state.loans:
        print(f"  {loan.name}: ${loan.principal:.4f}")
    print()
    
    # Check: is it truly all zeros?
    all_paid = all(l.principal <= 0.01 for l in goal_state.loans)
    print(f"All loans paid off (balance <= $0.01)? {all_paid}")
    print()
    
    # Show payment schedule
    print("Payment schedule (first 12 and around month 40-46):")
    for month, alloc in goal_state.history[:12]:
        total = sum(alloc.values())
        breakdown = ", ".join([f"{k}:${v:.0f}" for k, v in sorted(alloc.items())])
        print(f"  Month {month}: {breakdown} (total: ${total:.0f})")
    
    if len(goal_state.history) > 12:
        print("  ...")
        for month, alloc in goal_state.history[-6:]:
            total = sum(alloc.values())
            breakdown = ", ".join([f"{k}:${v:.0f}" for k, v in sorted(alloc.items())])
            print(f"  Month {month}: {breakdown} (total: ${total:.0f})")
else:
    print("No goal found")
