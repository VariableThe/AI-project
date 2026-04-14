#!/usr/bin/env python3
"""
Full A* search with complete goal tracking
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

print("=" * 80)
print("FULL A* SEARCH - TRACKING ALL GOALS")
print("=" * 80)
print()

# Manual A* implementation
start_state = State(0, deepcopy(loans), 0.0)
frontier = [start_state]
explored = {}
best_goal = None
all_goals = []

state_count = 0
max_month = 0

while frontier:
    current = heapq.heappop(frontier)
    state_count += 1
    max_month = max(max_month, current.month)
    
    # Check if goal
    if current.is_goal():
        all_goals.append((state_count, current.month, current.g_cost))
        print(f"Goal #{len(all_goals)}: State {state_count}, Month {current.month}, Interest ${current.g_cost:.2f}, f={current.f_cost:.2f}")
        
        if best_goal is None or current.g_cost < best_goal.g_cost:
            old_cost = best_goal.g_cost if best_goal else None
            print(f"  ✓ New best! (previous: {old_cost})")
            best_goal = current
        else:
            print(f"  ✗ Not better than ${best_goal.g_cost:.2f}")
        
        # Early termination optimization: if we have found a goal, we can prune branches
        # that have f(n) >= best_goal.g_cost
        # For now, let's limit to finding 10 goals to avoid infinite loops
        if len(all_goals) >= 10:
            print(f"\nStopping after 10 goals found")
            break
        continue
    
    state_id = current.get_id()
    if state_id in explored and explored[state_id] <= current.g_cost:
        continue
    explored[state_id] = current.g_cost
    
    # Pruning check
    if best_goal is not None and current.f_cost >= best_goal.g_cost:
        continue
    
    # Generate successors  
    active_loans = deepcopy(current.loans)
    
    solver = ConstraintSolver(
        active_loans,
        budget,
        floor,
        cash + (budget * current.month),
        granularity=100
    )
    allocations = solver.get_valid_allocations()
    
    # Generate next states
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
    
    # Stop if we've explored too many states
    if state_count >= 5000:
        print(f"\nStopping after 5000 states explored")
        break

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"States explored: {state_count}")
print(f"Max month reached: {max_month}")
print(f"Goals found: {len(all_goals)}")
print()

if all_goals:
    print("All goals found:")
    for i, (state_num, month, interest) in enumerate(all_goals):
        marker = "← BEST" if interest == min(g[2] for g in all_goals) else ""
        print(f"  Goal {i+1}: Month {month}, Interest ${interest:.2f} (state {state_num}) {marker}")
    print()
    print(f"Best goal: Month {best_goal.month}, Interest ${best_goal.g_cost:.2f}")
