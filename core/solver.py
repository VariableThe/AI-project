from collections import deque
from copy import deepcopy


class ConstraintSolver:
    def __init__(
        self, loans, monthly_budget, emergency_floor, current_cash, granularity=100
    ):
        self.loans = [l for l in loans if l.principal > 0]
        self.budget = monthly_budget
        self.emergency_floor = emergency_floor
        self.current_cash = current_cash
        self.granularity = granularity
        self.domains = {}

    def setup_domains(self):
        total_min_required = sum(l.min_payment for l in self.loans)
        # Maximum we can spend on debt this month = cash on hand + budget income - emergency reserve
        max_debt_payment = min(self.budget, self.current_cash + self.budget - self.emergency_floor)
        # Extra available beyond minimum payments
        available_extra = max(0, max_debt_payment - total_min_required)

        for l in self.loans:
            options = [l.min_payment]
            if available_extra > 0:
                rate = (
                    l.intro_rate if l.age_months < l.intro_duration else l.standard_rate
                )
                max_useful_extra = l.principal + (l.principal * rate) - l.min_payment
                actual_max_extra = min(available_extra, max_useful_extra)

                if actual_max_extra > 0:
                    options.append(l.min_payment + actual_max_extra)

            self.domains[l.name] = options

    def ac3(self):
        if not self.domains:
            return True
        queue = deque(
            [(xi, xj) for xi in self.domains for xj in self.domains if xi != xj]
        )

        while queue:
            xi, xj = queue.popleft()
            if self.revise(xi, xj):
                if not self.domains[xi]:
                    return False
                for xk in self.domains:
                    if xk != xi and xk != xj:
                        queue.append((xk, xi))
        return True

    def revise(self, xi, xj):
        revised = False
        new_domain = []
        other_mins = sum(
            min(self.domains[k]) for k in self.domains if k != xi and k != xj
        )

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
        if not self.ac3():
            return []

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
        
        if allocations:
            max_payment = max(sum(a.values()) for a in allocations)
            allocations = [a for a in allocations if sum(a.values()) == max_payment]
            
        return allocations
