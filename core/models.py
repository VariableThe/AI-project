class Loan:
    def __init__(self, name, principal, annual_rate, min_payment, intro_rate=None, intro_duration=0):
        self.name = name
        self.principal = float(principal)
        self.standard_rate = (annual_rate / 100.0) / 12.0
        self.intro_rate = (intro_rate / 100.0) / 12.0 if intro_rate is not None else self.standard_rate
        self.intro_duration = int(intro_duration)
        self.min_payment = float(min_payment)
        self.age_months = 0

    def apply_interest(self):
        if self.principal <= 0:
            return 0
        rate = self.intro_rate if self.age_months < self.intro_duration else self.standard_rate
        interest = self.principal * rate
        self.principal += interest
        self.age_months += 1
        return interest

    def get_heuristic_interest(self):
        if self.principal <= 0:
            return 0
        temp_p = self.principal
        total_interest = 0
        
        temp_age = self.age_months
        rate = self.intro_rate if temp_age < self.intro_duration else self.standard_rate
        if self.min_payment <= temp_p * rate:
            return 1e12 # unsolvable
            
        while temp_p > 0.01:
            rate = self.intro_rate if temp_age < self.intro_duration else self.standard_rate
            interest = temp_p * rate
            total_interest += interest
            temp_p = temp_p + interest - self.min_payment
            temp_age += 1
            if total_interest > 1e6: break 
            
        return total_interest

    def __repr__(self):
        return f"{self.name}(Balance: ${self.principal:.2f})"

class State:
    def __init__(self, month, loans, g_cost, history=None):
        self.month = month
        self.loans = loans
        self.g_cost = g_cost  
        self.h_cost = sum(l.get_heuristic_interest() for l in loans)
        self.f_cost = self.g_cost + self.h_cost
        self.history = history or []

    def is_goal(self):
        return all(l.principal <= 0.01 for l in self.loans)

    def __lt__(self, other):
        return self.f_cost < other.f_cost

    def get_id(self):
        # Hash with 2 decimal places precision to fix collision issue
        return (self.month, tuple(sorted([(l.name, round(l.principal, 2)) for l in self.loans])))
