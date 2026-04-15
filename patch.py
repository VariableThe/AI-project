import re

with open("core/solver.py", "r") as f:
    content = f.read()

# Replace max_debt_payment calculation
old_code = """        # Maximum we can spend on debt this month = cash on hand + budget income - emergency reserve
        max_debt_payment = self.current_cash + self.budget - self.emergency_floor
        # Extra available beyond minimum payments
        available_extra = max(0, max_debt_payment - total_min_required)"""

new_code = """        # Maximum we can spend on debt this month = cash on hand + budget income - emergency reserve
        max_debt_payment = min(self.budget, self.current_cash + self.budget - self.emergency_floor)
        # Extra available beyond minimum payments
        available_extra = max(0, max_debt_payment - total_min_required)"""

content = content.replace(old_code, new_code)

with open("core/solver.py", "w") as f:
    f.write(content)
