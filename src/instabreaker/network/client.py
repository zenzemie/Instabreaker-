import httpx
import random
from typing import Any, Dict
from ..utils.config import settings

USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.62 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
]

class AsyncInstagramClient:
    def __init__(self, proxy: str | None = None):
        self.proxy = proxy
        self.client = httpx.AsyncClient(
            http2=True,
            proxies=proxy,
            timeout=settings.default_timeout,
            headers={
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "X-IG-App-ID": "936619743392459",  # Common IG App ID for Web
                "X-ASBD-ID": "129477",
                "X-IG-WWW-Claim": "0",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://www.instagram.com",
                "Referer": "https://www.instagram.com/",
            }
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def get_csrf_token(self) -> str | None:
        try:
            response = await self.client.get("https://www.instagram.com/accounts/login/")
            return response.cookies.get("csrftoken")
        except Exception:
            return None

    async def login_attempt(self, username: str, password: str) -> httpx.Response:
        csrf_token = await self.get_csrf_token()
        if not csrf_token:
            # Try to get it from cookies if already set
            csrf_token = self.client.cookies.get("csrftoken")
            
        headers = {
            "X-CSRFToken": csrf_token if csrf_token else "",
        }
        
        import time
        timestamp = int(time.time())
        
        data = {
            "username": username,
            "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{timestamp}:{password}",
            "queryParams": "{}",
            "optIntoOneTap": "false"
        }
        
        return await self.client.post(
            "https://www.instagram.com/accounts/login/ajax/",
            data=data,
            headers=headers
        )
