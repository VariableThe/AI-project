# Loan Repayment Optimizer (AI-Driven)

An intelligent agent that treats debt repayment as a **State-Space Search Problem** combined with **Constraint Satisfaction**. Using $A^*$ Search and the AC-3 algorithm, this tool finds the mathematically optimal sequence of payments to minimize total interest paid, even with dynamic debt injections.

## 🚀 Key Features

- **Optimal Strategy:** Uses $A^*$ Search to guarantee the globally optimal repayment plan (minimizing cumulative interest).
- **Constraint-Aware:** Employs a **CSP (Constraint Satisfaction Problem)** solver with the **AC-3 algorithm** to prune invalid payment allocations that violate budget or emergency fund constraints.
- **Dynamic Debt Injection:** Supports "mid-simulation" events, such as an unexpected medical bill or new loan appearing at a specific month.
- **Informed Heuristic:** Implements an admissible heuristic $h(n)$ based on estimated remaining interest to accelerate the search process.

## 🧠 AI Integration

This project implements several core concepts from the standard AI curriculum (Russell & Norvig):

1.  **Intelligent Agents:** A goal-directed agent with a utility function focused on interest minimization.
2.  **A* Search:**
    *   **Path Cost $g(n)$:** Cumulative interest paid.
    *   **Heuristic $h(n)$:** Admissible estimation of remaining interest.
    *   **Optimality:** Guarantees the least-cost path to a zero-balance state.
3.  **Constraint Satisfaction (CSP):**
    *   **Variables:** Active loans for the current month.
    *   **Domains:** Discretized payment amounts (Min Payment vs. Min + Extra).
    *   **AC-3 Algorithm:** Prunes the search space by enforcing arc consistency across budget and cash flow constraints.

## 🛠️ Installation & Usage

### Prerequisites
- Python 3.x

### Running the Optimizer
```bash
python3 loan_optimizer.py
```

### Configuration
You can modify the initial conditions in `loan_optimizer.py`:
- **Initial Loans:** Edit the `loans` list with `Loan(name, principal, annual_rate, min_payment)`.
- **Dynamic Injections:** Add unexpected debts to the `injections` dictionary.
- **Budgeting:** Adjust `monthly_budget`, `emergency_floor`, and `initial_cash` in the `AStarOptimizer` initialization.

## 📂 Project Structure

- `loan_optimizer.py`: The main implementation containing the search engine and CSP solver.
- `GEMINI.md`: Detailed subject material integration and project objectives.
- `SCRIPT_EXPLANATION.md`: A technical breakdown of the classes and logic flow.

## 📄 License
This project is designed for educational purposes as part of an AI curriculum.
