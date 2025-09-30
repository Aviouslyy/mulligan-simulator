"""
Database management CLI for the mulligan simulator.
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from .db_service import DatabaseService
from .database import create_tables, drop_tables
from .db_init import initialize_database, get_database_info, check_database_connection, check_tables_exist


@click.group()
def db():
    """Database management commands."""
    pass


@db.command()
@click.option('--force', is_flag=True, help='Force recreate all tables')
def init(force):
    """Initialize the database tables."""
    console = Console()
    
    try:
        success = initialize_database(force_recreate=force)
        if success:
            console.print("✅ Database initialization completed successfully!")
        else:
            console.print("❌ Database initialization failed!")
    except Exception as e:
        console.print(f"❌ Error initializing database: {e}")


@db.command()
def status():
    """Check database status and information."""
    console = Console()
    
    try:
        info = get_database_info()
        
        status_panel = Panel(
            f"[bold green]Database URL:[/bold green] {info['database_url']}\n"
            f"[bold blue]Connection Status:[/bold blue] {info['connection_status']}\n"
            f"[bold yellow]Tables Exist:[/bold yellow] {info['tables_exist']}\n"
            f"[bold magenta]Existing Tables:[/bold magenta] {', '.join(info['existing_tables'])}",
            title="Database Status",
            border_style="green" if info['tables_exist'] else "red"
        )
        console.print(status_panel)
        
        if 'error' in info:
            console.print(f"[red]Error: {info['error']}[/red]")
            
    except Exception as e:
        console.print(f"❌ Error checking database status: {e}")


@db.command()
def check():
    """Check if database is ready."""
    console = Console()
    
    try:
        if check_database_connection() and check_tables_exist():
            console.print("✅ Database is ready")
        else:
            console.print("❌ Database is not ready")
    except Exception as e:
        console.print(f"❌ Error checking database: {e}")


@db.command()
def drop():
    """Drop all database tables."""
    console = Console()
    
    try:
        console.print("🗑️  Dropping database tables...")
        drop_tables()
        console.print("✅ Database tables dropped successfully!")
    except Exception as e:
        console.print(f"❌ Error dropping tables: {e}")


@db.command()
@click.option('--limit', '-l', default=10, help='Number of runs to show')
def list_runs(limit):
    """List recent simulation runs."""
    console = Console()
    
    try:
        db_service = DatabaseService()
        runs = db_service.get_simulation_runs(limit=limit)
        
        if not runs:
            console.print("📭 No simulation runs found.")
            return
        
        table = Table(title="Recent Simulation Runs")
        table.add_column("ID", style="cyan", width=8)
        table.add_column("Created", style="magenta", width=20)
        table.add_column("Deck Name", style="green", width=30)
        table.add_column("Hands", style="yellow", width=8)
        table.add_column("Source", style="blue", width=30)
        
        for run in runs:
            table.add_row(
                run['id'][:8] + "...",
                run['created_at'].strftime("%Y-%m-%d %H:%M"),
                run['deck_name'] or "Unknown",
                str(run['total_hands']),
                run['deck_source'][:30] + "..." if len(run['deck_source']) > 30 else run['deck_source']
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Error listing runs: {e}")
    finally:
        if 'db_service' in locals():
            db_service.close()


@db.command()
@click.argument('run_id')
def show_run(run_id):
    """Show details of a specific simulation run."""
    console = Console()
    
    try:
        db_service = DatabaseService()
        run_data = db_service.get_simulation_run(run_id)
        
        if not run_data:
            console.print(f"❌ Simulation run {run_id} not found.")
            return
        
        # Show run details
        details_panel = Panel(
            f"[bold green]Deck:[/bold green] {run_data['deck_name']}\n"
            f"[bold blue]Source:[/bold blue] {run_data['deck_source']}\n"
            f"[bold yellow]Total Hands:[/bold yellow] {run_data['total_hands']}\n"
            f"[bold magenta]Created:[/bold magenta] {run_data['created_at']}\n"
            f"[bold cyan]User:[/bold cyan] {run_data['user_name'] or 'Unknown'}",
            title=f"Simulation Run {run_id[:8]}...",
            border_style="green"
        )
        console.print(details_panel)
        
        # Show hand results
        if run_data['hand_results']:
            table = Table(title="Hand Results")
            table.add_column("Hand", style="cyan", width=6)
            table.add_column("Cards", style="yellow", width=6)
            table.add_column("Play/Draw", style="green", width=10)
            table.add_column("Mulligan", style="magenta", width=8)
            table.add_column("Decision", style="red", width=10)
            
            for hand in run_data['hand_results']:
                table.add_row(
                    str(hand['hand_number']),
                    str(hand['cards_in_hand']),
                    hand['play_or_draw'],
                    f"#{hand['mulligan_number']}",
                    hand['user_decision']
                )
            
            console.print(table)
        
    except Exception as e:
        console.print(f"❌ Error showing run: {e}")
    finally:
        if 'db_service' in locals():
            db_service.close()


@db.command()
@click.argument('run_id')
def stats(run_id):
    """Show statistics for a simulation run."""
    console = Console()
    
    try:
        db_service = DatabaseService()
        stats_data = db_service.get_simulation_stats(run_id)
        
        if not stats_data:
            console.print(f"❌ No statistics found for run {run_id}.")
            return
        
        stats_panel = Panel(
            f"[bold green]Total Hands:[/bold green] {stats_data['total_hands']}\n"
            f"[bold blue]Kept:[/bold blue] {stats_data['keep_count']} ({stats_data['keep_rate']:.1%})\n"
            f"[bold red]Mulliganed:[/bold red] {stats_data['mulligan_count']} ({1-stats_data['keep_rate']:.1%})\n"
            f"[bold yellow]Play:[/bold yellow] {stats_data['play_count']} ({stats_data['play_rate']:.1%})\n"
            f"[bold magenta]Draw:[/bold magenta] {stats_data['draw_count']} ({1-stats_data['play_rate']:.1%})",
            title=f"Statistics for Run {run_id[:8]}...",
            border_style="blue"
        )
        console.print(stats_panel)
        
        # Show mulligan distribution
        if stats_data['mulligan_distribution']:
            mulligan_table = Table(title="Mulligan Distribution")
            mulligan_table.add_column("Mulligan #", style="cyan")
            mulligan_table.add_column("Count", style="yellow")
            mulligan_table.add_column("Percentage", style="green")
            
            total = stats_data['total_hands']
            for mulligan_num, count in sorted(stats_data['mulligan_distribution'].items()):
                percentage = count / total if total > 0 else 0
                mulligan_table.add_row(
                    str(mulligan_num),
                    str(count),
                    f"{percentage:.1%}"
                )
            
            console.print(mulligan_table)
        
    except Exception as e:
        console.print(f"❌ Error showing stats: {e}")
    finally:
        if 'db_service' in locals():
            db_service.close()


if __name__ == '__main__':
    db()
