#!/usr/bin/env python3
import sys
print("Python script starting...", file=sys.stderr)

try:
    from rich.console import Console
    print("Rich imported successfully", file=sys.stderr)
    
    from core.models import Loan
    print("Models imported successfully", file=sys.stderr)
    
    from core.optimizer import AStarOptimizer
    print("Optimizer imported successfully", file=sys.stderr)
    
    console = Console()
    console.print("Creating test loan...")
    
    loan = Loan("Test", 1000, 10, 50)
    print(f"Loan created: {loan}", file=sys.stderr)
    
    console.print("[green]All imports successful![/green]")
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
