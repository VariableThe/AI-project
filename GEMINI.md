# Loan Repayment Optimizer: AI Subject Integration

## 1. Context & Subject Material Analysis
The project environment contains a series of lecture slides and textbooks covering a standard CS curriculum for Artificial Intelligence (based on Russell & Norvig). Key integrated topics include:
- **Intelligent Agents:** Implementation of a goal-directed agent with a clear utility function (minimizing interest).
- **Solving Problems by Searching:** Use of $A^*$ Search to explore the state space of monthly balances.
- **Informed Search & Heuristics:** Design of an admissible heuristic $h(n)$ to estimate remaining interest.
- **Constraint Satisfaction Problems (CSP):** Modeling monthly budget allocation as a CSP.
- **Constraint Propagation:** Using the **AC-3 algorithm** to prune the search space of possible payment combinations.
- **Logical Agents & Knowledge Representation:** Structuring the loan state and "Dynamic Injection" events as part of the agent's world knowledge.

## 2. The Prompt Objective
Design and implement a **Loan Repayment Optimizer** that:
1. Supports initial debts and dynamic debt entry (e.g., a new loan at Month 6).
2. Uses **A* Search** to find the globally optimal repayment sequence.
3. Defines **Path Cost $g(n)$** as cumulative interest paid.
4. Defines **Heuristic $h(n)$** as estimated remaining interest.
5. Employs **CSP & AC-3** to enforce constraints like budget limits and emergency fund floors.

## 3. Implementation Details

### A* Search Engine (`AStarOptimizer`)
- **State Space:** Each node represents a `(month, balance_tuple)`.
- **Transitions:** At each month, the agent chooses an allocation of the monthly budget among active loans.
- **Optimality:** By using $A^*$, the agent guarantees the sequence that minimizes the total interest paid across all loans, including those injected mid-simulation.

### CSP Solver (`ConstraintSolver`)
- **Variables:** The loans active in a given month.
- **Domain:** Possible payment amounts (Min Payment vs. Min Payment + Extra).
- **Constraints:** 
    - $\sum \text{Payments} \leq \text{Monthly Budget}$
    - $\text{Total Budget} \leq \text{Available Cash} - \text{Emergency Fund Floor}$
- **AC-3 Integration:** Before expanding nodes in $A^*$, the `ConstraintSolver` runs AC-3 to prune allocations that would violate the budget or cash flow limits.

### Dynamic Injection Mechanism
- The system checks the `injections` dictionary at every step. If the current month matches an injection key, a new `Loan` object is instantiated and added to the state's active loan list, forcing the $A^*$ search to re-evaluate the optimal path forward.

## 4. How to Run
```bash
python3 loan_optimizer.py
```
This will execute a simulation where a "Medical Bill" is added at Month 6, and the agent finds the new optimal path to zero balance.
