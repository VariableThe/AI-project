import heapq
from collections import deque
from copy import deepcopy

class Loan:
    def __init__(self, name, principal, annual_rate, min_payment):
        self.name = name
        self.principal = float(principal)
        self.rate = (annual_rate / 100.0) / 12.0  # Monthly interest rate
        self.min_payment = float(min_payment)

    def apply_interest(self):
        """Applies monthly interest and returns the amount added."""
        if self.principal <= 0:
            return 0
        interest = self.principal * self.rate
        self.principal += interest
        return interest

    def get_heuristic_interest(self):
        """h(n): Estimated remaining interest assuming only min payments are made."""
        if self.principal <= 0:
            return 0
        
        temp_p = self.principal
        total_interest = 0
        
        # If min payment doesn't cover interest, the loan is infinite (unsolvable state)
        if self.min_payment <= temp_p * self.rate:
            return 1e12 # Large penalty for unsolvable paths
            
        while temp_p > 0.01:
            interest = temp_p * self.rate
            total_interest += interest
            temp_p = temp_p + interest - self.min_payment
            # Safety break for simulation
            if total_interest > 1e6: break 
            
        return total_interest

    def __repr__(self):
        return f"{self.name}(Balance: ${self.principal:.2f})"

class ConstraintSolver:
    """
    CSP & AC-3 implementation to prune the search space of payment allocations.
    Constraints: 
    1. Total Payments <= Monthly Budget
    2. Payment_i >= Min_Payment_i
    3. Cash Flow >= Emergency Fund Floor
    """
    def __init__(self, loans, monthly_budget, emergency_floor, current_cash):
        self.loans = [l for l in loans if l.principal > 0]
        self.budget = monthly_budget
        self.emergency_floor = emergency_floor
        self.current_cash = current_cash
        self.domains = {}

    def setup_domains(self, granularity=50):
        """
        Discretizes the possible payment amounts for each loan.
        For simplicity in search, we consider paying the minimum OR 
        allocating remaining budget to a specific loan.
        """
        total_min_required = sum(l.min_payment for l in self.loans)
        # Check cash flow constraint
        available_extra = min(
            self.budget - total_min_required,
            self.current_cash - self.emergency_floor - total_min_required
        )
        available_extra = max(0, available_extra)

        for l in self.loans:
            # Domain options: Minimum payment or Minimum + all extra budget
            # (In a more complex version, we could use granular steps)
            options = [l.min_payment]
            if available_extra > 0:
                # Can't pay more than the balance + interest
                max_pay = min(l.min_payment + available_extra, l.principal + (l.principal * l.rate))
                if max_pay > l.min_payment:
                    options.append(max_pay)
            self.domains[l.name] = options

    def ac3(self):
        """Standard AC-3 to ensure Arc Consistency."""
        if not self.domains: return True
        queue = deque([(xi, xj) for xi in self.domains for xj in self.domains if xi != xj])
        
        while queue:
            xi, xj = queue.popleft()
            if self.revise(xi, xj):
                if not self.domains[xi]: return False
                for xk in self.domains:
                    if xk != xi and xk != xj:
                        queue.append((xk, xi))
        return True

    def revise(self, xi, xj):
        revised = False
        new_domain = []
        # Constraint: Sum of all min/max choices must be <= Budget
        other_mins = sum(min(self.domains[k]) for k in self.domains if k != xi and k != xj)
        
        for x in self.domains[xi]:
            satisfies = False
            for y in self.domains[xj]:
                if x + y + other_mins <= self.budget:
                    satisfies = True
                    break
            if satisfies:
                new_domain.append(x)
            else:
                revised = True
        self.domains[xi] = new_domain
        return revised

    def get_valid_allocations(self):
        self.setup_domains()
        if not self.ac3(): return []
        
        # Simple backtracking to find valid combinations from consistent domains
        allocations = []
        loan_names = list(self.domains.keys())
        
        def find_combinations(idx, current_map):
            if idx == len(loan_names):
                if sum(current_map.values()) <= self.budget:
                    allocations.append(deepcopy(current_map))
                return
            
            name = loan_names[idx]
            for val in self.domains[name]:
                current_map[name] = val
                find_combinations(idx + 1, current_map)
        
        find_combinations(0, {})
        return allocations

class State:
    def __init__(self, month, loans, g_cost, history=None):
        self.month = month
        self.loans = loans
        self.g_cost = g_cost  # Cumulative interest paid (Path Cost)
        # Calculate Heuristic h(n)
        self.h_cost = sum(l.get_heuristic_interest() for l in loans)
        self.f_cost = self.g_cost + self.h_cost
        self.history = history or []

    def is_goal(self):
        return all(l.principal <= 0.01 for l in self.loans)

    def __lt__(self, other):
        return self.f_cost < other.f_cost

    def get_id(self):
        # State representation for memoization
        return (self.month, tuple(sorted([(l.name, round(l.principal, 0)) for l in self.loans])))

class AStarOptimizer:
    def __init__(self, initial_loans, budget, emergency_floor, initial_cash, injections=None):
        self.initial_loans = initial_loans
        self.budget = budget
        self.emergency_floor = emergency_floor
        self.initial_cash = initial_cash
        self.injections = injections or {}

    def solve(self):
        start_state = State(0, deepcopy(self.initial_loans), 0.0)
        frontier = [start_state]
        explored = {}

        print(f"Starting A* Search (Budget: ${self.budget}/mo)...")

        while frontier:
            current = heapq.heappop(frontier)

            if current.is_goal():
                return current

            state_id = current.get_id()
            if state_id in explored and explored[state_id] <= current.g_cost:
                continue
            explored[state_id] = current.g_cost

            # Handle Dynamic Injections
            active_loans = deepcopy(current.loans)
            if current.month in self.injections:
                inj_loan = self.injections[current.month]
                # Check if already injected
                if not any(l.name == inj_loan.name for l in active_loans):
                    active_loans.append(deepcopy(inj_loan))

            # CSP to find allocations
            solver = ConstraintSolver(
                active_loans, 
                self.budget, 
                self.emergency_floor, 
                self.initial_cash + (self.budget * current.month) # Simplified cash growth
            )
            allocations = solver.get_valid_allocations()

            for alloc in allocations:
                next_loans = deepcopy(active_loans)
                interest_paid_this_step = 0
                
                # Apply Interest then Payment
                for l in next_loans:
                    interest_paid_this_step += l.apply_interest()
                    payment = alloc.get(l.name, 0)
                    l.principal = max(0, l.principal - payment)
                
                new_history = current.history + [(current.month, alloc)]
                next_state = State(
                    current.month + 1, 
                    next_loans, 
                    current.g_cost + interest_paid_this_step,
                    new_history
                )
                heapq.heappush(frontier, next_state)

        return None

if __name__ == "__main__":
    # 1. Setup Initial Loans
    loans = [
        Loan("Credit Card", 5000, 18.0, 150),
        Loan("Car Loan", 12000, 6.0, 300)
    ]

    # 2. Setup Dynamic Injection (Unexpected Medical Bill at Month 6)
    injections = {
        6: Loan("Medical Bill", 3000, 12.0, 100)
    }

    # 3. Initialize Optimizer
    optimizer = AStarOptimizer(
        initial_loans=loans,
        budget=1000,
        emergency_floor=1000,
        initial_cash=5000,
        injections=injections
    )

    result = optimizer.solve()

    if result:
        print("\n=== OPTIMAL REPAYMENT PLAN ===")
        print(f"Total Duration: {result.month} months")
        print(f"Total Interest Paid: ${result.g_cost:.2f}")
        print("\nMonthly Allocation (First 12 months):")
        for month, alloc in result.history[:12]:
            print(f"Month {month}: {alloc}")
        if result.month > 12:
            print("...")
    else:
        print("No solution found.")
