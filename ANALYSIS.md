# AI Loan Repayment Optimizer - Project Analysis

⚠️ **NOTE**: See [CURRENT_STATUS.md](CURRENT_STATUS.md) for investigation findings and what's working vs not working.

## 📋 Project Overview

This is an **Intelligent Agent** for optimal debt repayment planning using:
- **A* Search** for finding optimal payment allocation sequences
- **Constraint Satisfaction Problem (CSP)** solving with AC-3 algorithm
- **Advanced Heuristics** for informed search acceleration

**Current Status**: Functional but A* is suboptimal ($352.64 worse than Snowball on test case)

---

## 🏗️ Architecture

### 1. **Core Components**

#### `models.py` - State Representation
- **Loan Class**: Represents a single debt obligation
  - Tracks principal balance, interest rate (with intro/standard rates)
  - `apply_interest()`: Simulates monthly interest accrual
  - `get_heuristic_interest()`: Estimates remaining interest assuming min payments (admissible heuristic $h(n)$)

- **State Class**: Represents the search space node
  - Stores: month, active loans, cumulative interest paid ($g(n)$), and payment history
  - Calculates $f(n) = g(n) + h(n)$ for A* prioritization
  - `is_goal()`: Checks if all loans are paid off
  - `get_id()`: Creates unique state hash for memoization (prevents cycles)

#### `solver.py` - Constraint Satisfaction Engine  
- **ConstraintSolver Class**: Handles monthly payment allocation decisions
  - **Variables**: Each active loan (payment amount to allocate)
  - **Domains**: Discretized payment options
    - Minimum Payment only
    - Minimum + Extra (up to available budget in steps)
  - **Constraints**:
    - Total payments ≤ Monthly budget
    - Cash flow ≤ Emergency floor
  - **AC-3 Algorithm**: Enforces arc consistency to prune invalid combinations
    - Eliminates payment options that violate constraints
    - Reduces branching factor significantly

#### `optimizer.py` - Search Engine
- **AStarOptimizer Class**: Main optimization engine
  - Uses priority queue (min-heap) sorted by $f(n)$
  - Tracks explored states to avoid cycles
  - Handles dynamic debt injections (unexpected bills at specified months)
  - Returns optimal sequence when goal state is reached

---

## 🧪 Test Execution Results

### Input Scenario
```
Loans:
  - Credit Card: $5,000 @ 18.0% APR (min: $150/month)
  - Car Loan: $15,000 @ 6.5% APR (min: $350/month)
  - Student Loan: $20,000 @ 4.5% APR (min: $200/month)

Total Debt: $40,000

Budget Constraints:
  - Available for repayment: $1,000/month
  - Current cash: $2,000
  - Emergency floor: $500
  - Min payments total: $700/month
  - Extra budget available: $300/month

Dynamic Events:
  - Month 3: Medical bill ($2,000, no interest, min $100/month)
```

### Results

| Strategy | Months to Payoff | Total Interest | Time |
|----------|-----------------|-----------------|------|
| **Debt Snowball** (Greedy) | 48 months | $5,026.10 | - |
| **A* Optimal** | 48 months | $5,378.74 | 0.03s |

---

## ⚠️ Key Observations

### 1. **Unexpected Result: A* Interest is Higher**
The A* algorithm found a 48-month solution, but with **$352.64 MORE interest** than Snowball!  

This is counterintuitive because A* should guarantee optimality. Possible causes:

**A) Heuristic Issues**
- The heuristic $h(n)$ is computed by: "Assume we pay min payments for all remaining months"
- For loans with high interest rates, this might be overestimating remaining costs
- If $h(n)$ overestimates, then A* is no longer guaranteed to be optimal

**B) State Space Explosion**
- With $1,000 monthly budget discretized across 3-4 loans, the branching factor is high
- The search frontier grows exponentially
- A* might be exploring/returning non-optimal states due to incomplete exploration within time constraints

**C) Termination Condition**
- A* returns the **first goal state reached** (line: `if current.is_goal(): return current`)
- If states are explored in suboptimal order, the first goal might not be cheapest
- This is correct for admissible heuristics, but suggests the heuristic might be non-admissible

---

## 🔍 Deep Dive: Debt Snowball Performance

**Why did Snowball outperform A*?**

Snowball strategy is greedy and simple:
1. Pay minimum on all loans
2. Put ALL extra budget ($300/month) toward smallest balance first
3. This directly targets high-interest debt (Credit Card at 18%) early

In this case:
- Credit Card ($5k @ 18%) gets aggressive payoff first
- High-interest debt is eliminated quickly, reducing future interest accrual
- The medical bill injection in month 3 creates complexity that affects search

---

## 🤖 AI Concepts Implemented

### A* Search Properties
- **Completeness**: ✓ (will find a solution if one exists)
- **Optimality**: ❓ (Results suggest heuristic may be inadmissible)
- **Time Complexity**: Depends on branching factor and search depth
- **Space Complexity**: Stores frontier and explored states

### CSP Components
- **Variables**: Loan payment amounts
- **Domain Reduction**: AC-3 prunes invalid combinations
- **Arc Consistency**: Enforces constraints before branching

---

## 💡 Issues & Recommendations

### Current Issues:
1. **A* not outperforming Snowball** - suggests optimization inefficiency
2. **High memory usage potential** - unbounded frontier growth
3. **Limited to 48-month horizon** - might miss better long-term strategies
4. **Discrete granularity** - $100 step size limits precision

### Potential Improvements:
1. **Admissible Heuristic Verification** - Ensure $h(n)$ never overestimates
2. **Iterative Deepening** - Limit search depth, increase gradually
3. **Better State Memoization** - Current precision (2 decimals) might lose information
4. **Parallel Search** - Explore multiple branches simultaneously
5. **Hybrid Approach** - Combine Snowball (fast approximate) with local A* refinement

---

## 📊 Execution Flow

```
User Input (Loans, Budget, Constraints, Injections)
              ↓
Initialize AStarOptimizer
              ↓
        ┌─────┴─────┐
        ↓           ↓
   Snowball    A* Search
   (Greedy)    (Optimal)
        ↓           ↓
        └─────┬─────┘
              ↓
        Compare Results
              ↓
    Display Optimal Schedule
```

---

## 🎯 Conclusion

This is a well-architected AI project implementing:
- ✓ Informed search (A* with heuristic)
- ✓ Constraint satisfaction (AC-3 algorithm)  
- ✓ State-space search optimization
- ✓ Real-world problem modeling

However, the current results suggest the heuristic function may not be fully admissible, causing A* to underperform compared to the simpler Snowball greedy algorithm. The 0.03s runtime shows the algorithm is efficient, but correctness should be the priority.

The project successfully demonstrates core AI curriculum concepts from Russell & Norvig's "Artificial Intelligence: A Modern Approach."
