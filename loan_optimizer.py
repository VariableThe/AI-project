import sys
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm
from rich.table import Table
from rich.panel import Panel
from core.models import Loan
from core.optimizer import AStarOptimizer

console = Console()

def clear():
    console.clear()

def display_header():
    console.print(Panel.fit("[bold cyan]AI Loan Repayment Optimizer[/bold cyan]\n[italic]Powered by A* Search & CSP[/italic]", border_style="cyan"))

def get_loans():
    loans = []
    console.print("\n[bold yellow]Step 1: Enter your current debts[/bold yellow]")
    while True:
        name = Prompt.ask("Loan Name (e.g., 'Credit Card', 'Car Loan')")
        principal = FloatPrompt.ask(f"Current Balance for [bold]{name}[/bold]")
        standard_rate = FloatPrompt.ask(f"Standard Annual Interest Rate (%) for [bold]{name}[/bold]")
        
        has_intro = Confirm.ask(f"Does [bold]{name}[/bold] have a promotional/intro rate?", default=False)
        intro_rate = None
        intro_duration = 0
        if has_intro:
            intro_rate = FloatPrompt.ask("Introductory Rate (%)")
            intro_duration = IntPrompt.ask("How many months will the intro rate last?")
            
        min_payment = FloatPrompt.ask(f"Minimum Monthly Payment for [bold]{name}[/bold]")
        
        loan = Loan(name, principal, standard_rate, min_payment, intro_rate, intro_duration)
        loans.append(loan)
        
        if not Confirm.ask("\nAdd another loan?", default=True):
            break
            
    return loans

def get_budget_info():
    console.print("\n[bold yellow]Step 2: Enter your budget constraints[/bold yellow]")
    budget = FloatPrompt.ask("Total Monthly Budget for debt repayment")
    cash = FloatPrompt.ask("Current Available Cash (Savings/Checking)")
    floor = FloatPrompt.ask("Emergency Fund Floor (Do not let cash drop below this)")
    return budget, cash, floor

def get_injections():
    injections = {}
    console.print("\n[bold yellow]Step 3: Dynamic Injections (Future sudden debts/expenses)[/bold yellow]")
    if Confirm.ask("Do you anticipate any sudden future debts? (e.g., Medical bill in month 6)", default=False):
        while True:
            month = IntPrompt.ask("In what month will this happen? (e.g., 6 for 6 months from now)")
            name = Prompt.ask(f"Name of Expense at Month {month}")
            principal = FloatPrompt.ask(f"Amount for [bold]{name}[/bold]")
            rate = FloatPrompt.ask("Annual Interest Rate (%) (Enter 0 if it's a fixed bill with no interest)")
            min_payment = FloatPrompt.ask("Minimum Monthly Payment required")
            
            injections[month] = Loan(name, principal, rate, min_payment)
            
            if not Confirm.ask("Add another future event?", default=False):
                break
    return injections

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
    clear()
    display_header()
    
    loans = get_loans()
    budget, cash, floor = get_budget_info()
    injections = get_injections()
    
    granularity = FloatPrompt.ask("\nPayment Increment Granularity (e.g. 50 will allocate extra cash in $50 chunks. Smaller = slower but better)", default=100.0)
    
    console.print("\n[bold green]Initializing AI Agents...[/bold green]")
    optimizer = AStarOptimizer(loans, budget, floor, cash, injections, granularity)
    
    console.print("[yellow]Simulating Baseline (Debt Snowball)...[/yellow]")
    res_snowball = optimizer.solve_snowball()
    
    console.print("[yellow]Running A* Optimal State-Space Search...[/yellow]")
    with console.status("[bold cyan]Exploring permutations...") as status:
        res_astar = optimizer.solve()
        
    display_results(res_astar, res_snowball)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]Exiting...[/red]")
        sys.exit(0)
