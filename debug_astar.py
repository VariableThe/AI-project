#!/usr/bin/env python3
"""
Debug A* search with detailed output
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
print("DEBUGGING A* EXPLORATION")
print("=" * 80)
print()

# Manual A* implementation with debugging
start_state = State(0, deepcopy(loans), 0.0)
frontier = [start_state]
explored = {}
best_goal = None
goal_count = 0
state_count = 0

print(f"Initial state: g={start_state.g_cost:.2f}, h={start_state.h_cost:.2f}, f={start_state.f_cost:.2f}")
print()

while frontier and state_count < 500:  # Limit iterations for debugging
    current = heapq.heappop(frontier)
    state_count += 1
    
    # Check if goal
    if current.is_goal():
        goal_count += 1
        print(f"GOAL #{goal_count} at state {state_count}: Month {current.month}, Interest ${current.g_cost:.2f}")
        
        if best_goal is None or current.g_cost < best_goal.g_cost:
            old_cost = best_goal.g_cost if best_goal else None
            print(f"  → New best goal! (was: {old_cost})")
            best_goal = current
        else:
            print(f"  → Not better than current best (${best_goal.g_cost:.2f})")
        
        # Pruning check
        if best_goal is not None and current.f_cost >= best_goal.g_cost:
            print(f"  → Would be pruned: f({current.f_cost:.2f}) >= best_g({best_goal.g_cost:.2f})")
        print()
        
        # Stop after finding a few goals to see pattern
        if goal_count >= 5:
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
    
    # Show first state's allocations in detail
    if state_count == 1:
        print(f"State 0 allocations ({len(allocations)} options):")
        for i, alloc in enumerate(allocations[:5]):
            total = sum(alloc.values())
            breakdown = ", ".join([f"{k}:${v:.0f}" for k, v in sorted(alloc.items())])
            print(f"  [{i}] {breakdown} (total: ${total:.0f})")
        if len(allocations) > 5:
            print(f"  ... + {len(allocations) - 5} more")
        print()
    
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

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"States explored: {state_count}")
print(f"Goals found: {goal_count}")
if best_goal:
    print(f"Best goal: Month {best_goal.month}, Interest ${best_goal.g_cost:.2f}")
    print(f"First few payments of best goal:")
    for month, alloc in best_goal.history[:5]:
        breakdown = ", ".join([f"{k}:${v:.0f}" for k, v in sorted(alloc.items())])
        print(f"  Month {month}: {breakdown}")
