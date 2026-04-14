#!/usr/bin/env python3
"""
Test script to run the loan optimizer with predefined values
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from core.models import Loan
from core.optimizer import AStarOptimizer

console = Console()

def display_results(result_astar, result_snowball):
    console.rule("[bold green]Optimization Results")
    
    table = Table(title="Method Comparison")
    table.add_column("Strategy", style="cyan", no_wrap=True)
    table.add_column("Total Interest Paid", style="magenta")
    table.add_column("Total Months", justify="right", style="green")
    
    table.add_row(
        "Debt Snowball (Smallest Balance First)", 
        f"${result_snowball.g_cost:.2f}" if result_snowball else "N/A", 
        str(result_snowball.month) if result_snowball else "N/A"
    )
    
    if result_astar:
        table.add_row(
            "[bold]A* Optimal Search (AI CSP)[/bold]", 
            f"[bold]${result_astar.g_cost:.2f}[/bold]", 
            f"[bold]{result_astar.month}[/bold]"
        )
        savings = result_snowball.g_cost - result_astar.g_cost if result_snowball else 0
        if savings > 0:
            table.add_row(
                "[bold green]Savings (A* vs Snowball)[/bold green]",
                f"[bold green]${savings:.2f}[/bold green]",
                ""
            )
            
    console.print(table)
    
    if result_astar:
        console.print("\n[bold cyan]Optimal Repayment Schedule (First 12 Months):[/bold cyan]")
        schedule_table = Table(show_header=True, header_style="bold yellow")
        schedule_table.add_column("Month", justify="center")
        
        loans_seen = set()
        for _, alloc in result_astar.history:
            for k in alloc.keys(): loans_seen.add(k)
            
        for k in sorted(list(loans_seen)):
            schedule_table.add_column(k, justify="right")
            
        for month, alloc in result_astar.history[:12]:
            row = [str(month)]
            for k in sorted(list(loans_seen)):
                val = alloc.get(k, 0)
                row.append(f"${val:.2f}" if val > 0 else "$0.00")
            schedule_table.add_row(*row)
            
        console.print(schedule_table)
        if result_astar.month > 12:
            console.print("... [italic]Schedule continues[/italic]")

def main():
    console.print(Panel.fit("[bold cyan]AI Loan Repayment Optimizer - Test Run[/bold cyan]\n[italic]Powered by A* Search & CSP[/italic]", border_style="cyan"))
    
    # Define test loans
    console.print("\n[bold yellow]Scenario: User with multiple debts[/bold yellow]")
    loans = [
        Loan("Credit Card", 5000, 18.0, 150),      # $5k at 18% APR, $150 min payment
        Loan("Car Loan", 15000, 6.5, 350),         # $15k at 6.5% APR, $350 min payment
        Loan("Student Loan", 20000, 4.5, 200),     # $20k at 4.5% APR, $200 min payment
    ]
    
    # Budget constraints
    budget = 1000  # $1000/month available for debt repayment
    cash = 2000    # $2000 in savings
    floor = 500    # Keep at least $500 as emergency fund
    
    # Future dynamic injection: medical bill in month 3
    injections = {
        3: Loan("Medical Bill", 2000, 0, 100)  # $2000 medical bill, no interest, $100 min payment
    }
    
    console.print(f"\n[cyan]Initial Loans:[/cyan]")
    for loan in loans:
        console.print(f"  - {loan.name}: ${loan.principal:.2f} @ {loan.standard_rate*12*100:.1f}% APR (Min payment: ${loan.min_payment:.2f})")
    
    console.print(f"\n[cyan]Budget Constraints:[/cyan]")
    console.print(f"  - Monthly Budget: ${budget:.2f}")
    console.print(f"  - Available Cash: ${cash:.2f}")
    console.print(f"  - Emergency Fund Floor: ${floor:.2f}")
    
    console.print(f"\n[cyan]Dynamic Events:[/cyan]")
    for month, injection in injections.items():
        console.print(f"  - Month {month}: {injection.name} - ${injection.principal:.2f} (Min payment: ${injection.min_payment:.2f})")
    
    console.print("\n[bold green]Initializing AI Agents...[/bold green]")
    optimizer = AStarOptimizer(loans, budget, floor, cash, injections, granularity=100)
    
    console.print("[yellow]Simulating Baseline (Debt Snowball Strategy)...[/yellow]")
    res_snowball = optimizer.solve_snowball()
    
    console.print("[yellow]Running A* Optimal State-Space Search with CSP...[/yellow]")
    with console.status("[bold cyan]Exploring payment allocation permutations...", spinner="dots") as status:
        res_astar = optimizer.solve()
    
    display_results(res_astar, res_snowball)
    
    console.print("\n[bold cyan]Analysis Summary:[/bold cyan]")
    if res_astar:
        console.print(f"✓ A* found optimal solution:")
        console.print(f"  - Months to payoff: {res_astar.month}")
        console.print(f"  - Total interest paid: ${res_astar.g_cost:.2f}")
        if res_snowball:
            savings = res_snowball.g_cost - res_astar.g_cost
            percent_saved = (savings / res_snowball.g_cost * 100) if res_snowball.g_cost > 0 else 0
            console.print(f"  - Savings vs Snowball: ${savings:.2f} ({percent_saved:.1f}%)")
    else:
        console.print("✗ No solution found (budget may be insufficient)")

if __name__ == "__main__":
    main()
