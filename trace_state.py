#!/usr/bin/env python3
"""
Check what's happening with month counts
"""

from core.models import Loan

# Recreate the exact first goal found in the debug
loans_at_goal = [
    Loan("CC", 5000, 18.0, 150),
    Loan("Car", 15000, 6.5, 350),
    Loan("Student", 20000, 4.5, 200),
]

# Simulate months 0-45 with the payments from the debug output
payments_history = [
    # Month 0-2: Same pattern
    {"CC": 450, "Car": 350, "Student": 200},
    {"CC": 450, "Car": 350, "Student": 200},
    {"CC": 450, "Car": 350, "Student": 200},
    # Month 3: Medical bill injected, changes payments
    {"CC": 350, "Car": 350, "Student": 300},
    # Month 4: Another different month  
    {"CC": 150, "Car": 350, "Student": 500},
]

print("Simulating payments to understand the state evolution...\n")

for month in range(min(5, len(payments_history))):
    print(f"\nMonth {month} START:")
    for l in loans_at_goal:
        print(f"  {l.name}: ${l.principal:.2f}")
    
    # Apply interest
    for l in loans_at_goal:
        interest = l.apply_interest()
        print(f"  {l.name} +interest: ${interest:.2f}")
    
    # Apply payment
    alloc = payments_history[month]
    for l in loans_at_goal:
        payment = alloc.get(l.name, 0)
        l.principal = max(0, l.principal - payment)
        print(f"  {l.name} -payment: ${payment:.2f} → ${l.principal:.2f}")

print(f"\n\nAfter {min(5, len(payments_history))} months simulated:")
for l in loans_at_goal:
    print(f"  {l.name}: ${l.principal:.2f}")

# Now check: if we reach all zeros, is that a goal?
print(f"\nAll paid off? {all(l.principal <= 0.01 for l in loans_at_goal)}")
