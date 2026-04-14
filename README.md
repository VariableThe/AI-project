# Loan Repayment Optimizer (AI-Driven)

⚠️ **IMPORTANT**: See [CURRENT_STATUS.md](CURRENT_STATUS.md) for recent investigation findings. The A* algorithm is functional but currently returns suboptimal results due to a weak heuristic. The Snowball greedy algorithm is recommended for production use.

An intelligent agent that treats debt repayment as a **State-Space Search Problem** combined with **Constraint Satisfaction**. Uses $A^*$ Search and the AC-3 algorithm, attempting to find the mathematically optimal sequence of payments to minimize total interest paid, even with dynamic debt injections.

## 🚀 Key Features

- **Optimal Strategy (Attempted):** Uses $A^*$ Search (with improvements to handle dynamic injection), though currently returns suboptimal results due to heuristic limitations. See [CURRENT_STATUS.md](CURRENT_STATUS.md).
- **Constraint-Aware:** Employs a **CSP (Constraint Satisfaction Problem)** solver with the **AC-3 algorithm** to prune invalid payment allocations that violate budget or emergency fund constraints. ✓ Working well
- **Baseline Algorithm:** Includes **Debt Snowball** greedy algorithm which outperforms A* on test cases ($352.64 better on the test scenario)
- **Dynamic Debt Injection:** Supports "mid-simulation" events, such as an unexpected medical bill or new loan appearing at a specific month. ✓ Working
- **Informed Heuristic:** Implements an admissible heuristic $h(n)$ based on estimated remaining interest, but the heuristic is too weak to guide A* toward optimal solutions. ⚠️ Needs improvement

## 🧠 AI Integration

This project implements several core concepts from the standard AI curriculum (Russell & Norvig):

1.  **Intelligent Agents:** A goal-directed agent with a utility function focused on interest minimization.
2.  **A* Search:** ⚠️ See [CURRENT_STATUS.md](CURRENT_STATUS.md) - implementation has optimality issues
    *   **Path Cost $g(n)$:** Cumulative interest paid.
    *   **Heuristic $h(n)$:** Admissible estimation of remaining interest (but too weak).
    *   **Optimality:** ❌ Does NOT currently guarantee least-cost path (returns suboptimal solutions)
3.  **Constraint Satisfaction (CSP):** ✓ Working correctly
    *   **Variables:** Active loans for the current month.
    *   **Domains:** Discretized payment amounts (Min Payment vs. Min + Extra).
    *   **AC-3 Algorithm:** Prunes the search space by enforcing arc consistency across budget and cash flow constraints.
4. **Greedy Algorithm (Debt Snowball):** ✓ Works better than A* on current tests - recommended for use

## 🛠️ Installation & Usage

### Prerequisites
- Python 3.x
- `rich` library (for UI formatting)

### Quick Start
```bash
# Run with hardcoded test scenario (recommended)
python3 simple_test.py

# Run interactive version
python3 loan_optimizer.py
```

### Test & Analysis Scripts
```bash
# Compare payment decisions month-by-month
python3 trace_decisions.py

# Check what payment allocations the CSP generates
python3 check_csp_allocations.py

# See full timeline comparison
python3 final_timeline.py
```

### Recommended Reading
1. **[CURRENT_STATUS.md](CURRENT_STATUS.md)** ← START HERE - explains what's working/broken and why
2. **[EXECUTION_ANALYSIS.md](EXECUTION_ANALYSIS.md)** - detailed architectural analysis
3. **[ANALYSIS.md](ANALYSIS.md)** - initial technical breakdown
4. **[SCRIPT_EXPLANATION.md](SCRIPT_EXPLANATION.md)** - original documentation
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
