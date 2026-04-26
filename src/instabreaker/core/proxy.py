import asyncio
import httpx
from typing import List, Optional
import random

class ProxyManager:
    def __init__(self, proxies: Optional[List[str]] = None):
        self.proxies = proxies or []
        self.active_proxies = self.proxies.copy()
        
    async def check_proxy(self, proxy: str) -> bool:
        try:
            async with httpx.AsyncClient(proxies={"all://": proxy}, timeout=5.0) as client:
                response = await client.get("https://www.instagram.com", follow_redirects=True)
                return response.status_code == 200
        except Exception:
            return False

    async def refresh_proxies(self):
        # In a real scenario, this could scrape public proxy lists
        # For now, we just check the ones we have
        valid_proxies = []
        tasks = [self.check_proxy(p) for p in self.proxies]
        results = await asyncio.gather(*tasks)
        
        for proxy, is_valid in zip(self.proxies, results):
            if is_valid:
                valid_proxies.append(proxy)
        
        self.active_proxies = valid_proxies

    def get_proxy(self) -> Optional[str]:
        if not self.active_proxies:
            return None
        return random.choice(self.active_proxies)

    def remove_proxy(self, proxy: str):
        if proxy in self.active_proxies:
            self.active_proxies.remove(proxy)
