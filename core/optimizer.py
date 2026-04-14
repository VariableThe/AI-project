import heapq
from copy import deepcopy
from core.models import State
from core.solver import ConstraintSolver

class AStarOptimizer:
    def __init__(self, initial_loans, budget, emergency_floor, initial_cash, injections=None, granularity=100):
        self.initial_loans = initial_loans
        self.budget = budget
        self.emergency_floor = emergency_floor
        self.initial_cash = initial_cash
        self.injections = injections or {}
        self.granularity = granularity

    def solve(self):
        start_state = State(0, deepcopy(self.initial_loans), 0.0)
        frontier = [start_state]
        explored = {}
        best_goal = None

        while frontier:
            current = heapq.heappop(frontier)

            # If we found a goal and frontier is exhausted of better options, return
            if best_goal is not None and current.f_cost >= best_goal.g_cost:
                return best_goal

            # Check if goal
            if current.is_goal():
                if best_goal is None or current.g_cost < best_goal.g_cost:
                    best_goal = current
                continue

            state_id = current.get_id()
            if state_id in explored and explored[state_id] <= current.g_cost:
                continue
            explored[state_id] = current.g_cost

            active_loans = deepcopy(current.loans)
            if current.month in self.injections:
                inj_loan = self.injections[current.month]
                if not any(l.name == inj_loan.name for l in active_loans):
                    active_loans.append(deepcopy(inj_loan))

            solver = ConstraintSolver(
                active_loans, 
                self.budget, 
                self.emergency_floor, 
                self.initial_cash + (self.budget * current.month),
                granularity=self.granularity
            )
            allocations = solver.get_valid_allocations()

            for alloc in allocations:
                next_loans = deepcopy(active_loans)
                interest_paid_this_step = 0
                
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

        return best_goal

    def solve_snowball(self):
        active_loans = deepcopy(self.initial_loans)
        month = 0
        total_interest = 0
        history = []
        
        while not all(l.principal <= 0 for l in active_loans):
            if month in self.injections:
                inj_loan = self.injections[month]
                if not any(l.name == inj_loan.name for l in active_loans):
                    active_loans.append(deepcopy(inj_loan))
                    
            active_loans = [l for l in active_loans if l.principal > 0]
            if not active_loans:
                break
                
            interest_this_month = 0
            allocation = {}
            for l in active_loans:
                interest_this_month += l.apply_interest()
                allocation[l.name] = l.min_payment
            
            total_interest += interest_this_month
            
            total_min = sum(l.min_payment for l in active_loans)
            extra_budget = self.budget - total_min
            
            smallest_loan = min(active_loans, key=lambda x: x.principal)
            
            rate = smallest_loan.intro_rate if smallest_loan.age_months <= smallest_loan.intro_duration else smallest_loan.standard_rate
            max_to_pay = smallest_loan.principal + (smallest_loan.principal * rate)
            
            can_pay_extra = min(extra_budget, max_to_pay - smallest_loan.min_payment)
            if can_pay_extra > 0:
                allocation[smallest_loan.name] += can_pay_extra
                
            for l in active_loans:
                l.principal = max(0, l.principal - allocation[l.name])
                
            history.append((month, allocation))
            month += 1
            
            if month > 1200:
                return None
                
        return State(month, active_loans, total_interest, history)
