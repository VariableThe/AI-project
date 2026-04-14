# Loan Repayment Optimizer: Script Explanation

This document provides a technical breakdown of the logic implemented in `loan_optimizer.py`. The script is designed as an **Intelligent Agent** that treats debt repayment as a **State-Space Search Problem** combined with **Constraint Satisfaction**.

---

## 1. The `Loan` Class (The Environment State)
Each `Loan` object tracks its own balance, interest rate, and minimum payment.
- **`apply_interest()`**: This simulates the passage of time. Before any payments are made, the interest is added to the principal.
- **`get_heuristic_interest()` ($h(n)$)**: This is the "Informed Search" component. It estimates the remaining interest by calculating just one month's interest based on current balances and rates. This value is **admissible** (it never over-estimates the true minimum future cost since extra payments can only reduce future interest), allowing $A^*$ to find the optimal solution efficiently.

## 2. The `ConstraintSolver` Class (CSP & AC-3)
At every month, the agent must decide how to distribute the budget. This is a **Constraint Satisfaction Problem**.
- **Variables**: Each active loan.
- **Domains**: The possible payment amounts. To keep the search space manageable, we discretize the domain: either the **Minimum Payment** or the **Minimum + All Available Extra Budget**.
- **Constraints**:
    - **Budget Constraint**: Total payments $\leq$ Monthly Budget.
    - **Cash Flow Constraint**: Total payments must not drop the user's cash below the **Emergency Fund Floor**.
- **`ac3()` Algorithm**: Before the search branches, AC-3 ensures "Arc Consistency." If paying the maximum on Loan A makes it impossible to even pay the minimum on Loan B within the budget, that "maximum" option is pruned from Loan A's domain. This drastically reduces the branching factor.

## 3. The `State` Class (Search Nodes)
A `State` represents the world at a specific month.
- **$g(n)$ (Path Cost)**: The total cumulative interest paid from Month 0 to now.
- **$h(n)$ (Heuristic)**: The estimated remaining interest (calculated via the `Loan` class).
- **$f(n) = g(n) + h(n)$**: The total estimated cost of the path. $A^*$ always expands the node with the lowest $f(n)$.
- **Memoization**: The `get_id()` method creates a unique hash of the balances, allowing the optimizer to skip "Explored" states (avoiding cycles or redundant paths).

## 4. The `AStarOptimizer` Class (The Engine)
This is the "Brain" of the system.
- **The Frontier**: A priority queue that stores `State` objects, sorted by $f(n)$.
- **Dynamic Injections**: At the start of each "month" in the simulation, the engine checks the `injections` dictionary. If a new debt (like a Medical Bill) is scheduled for that month, it is "injected" into the current state's loan list.
- **Branching**:
    1. It takes the best state from the frontier.
    2. It runs the `ConstraintSolver` to find all **valid** payment allocations for that month.
    3. For each valid allocation, it creates a "Successor State," applies the payments, and pushes it back into the frontier.

## 5. Execution Flow
1. **Initialize**: Set up initial loans and the "Medical Bill" injection at Month 6.
2. **Search**: The agent explores different payment sequences.
3. **Optimize**: Because $A^*$ is used, the first time the agent reaches a state where all balances are $\$0$, it is mathematically guaranteed to be the sequence that paid the **least amount of total interest**.
4. **Output**: The script prints the month-by-month allocation plan.
