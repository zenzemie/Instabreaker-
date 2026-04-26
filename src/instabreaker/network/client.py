import time
import random
from typing import Optional, Dict, Any
from curl_cffi.requests import AsyncSession
from ..core.stealth import StealthManager
from ..utils.config import settings

class AsyncInstagramClient:
    def __init__(self, proxy: str | None = None):
        self.proxy = proxy
        self.stealth = StealthManager()
        self.session = AsyncSession(
            impersonate=self.stealth.get_impersonate(),
            proxies={"http": proxy, "https": proxy} if proxy else None,
            timeout=settings.default_timeout,
        )
        self.session.headers.update(self.stealth.get_headers())

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # AsyncSession doesn't have aclose() in all versions, 
        # but it's good practice if it exists or just let it GC.
        pass

    async def get_csrf_token(self) -> str | None:
        try:
            response = await self.session.get("https://www.instagram.com/accounts/login/")
            return response.cookies.get("csrftoken")
        except Exception:
            return None

    async def login_attempt(self, username: str, password: str) -> Any:
        csrf_token = await self.get_csrf_token()
        if not csrf_token:
            csrf_token = self.session.cookies.get("csrftoken")
            
        headers = self.stealth.get_headers(username)
        if csrf_token:
            headers["X-CSRFToken"] = csrf_token
        
        timestamp = int(time.time())
        # IG uses a specific password encryption format in browsers
        # #PWD_INSTAGRAM_BROWSER:0:TIMESTAMP:PASSWORD
        data = {
            "username": username,
            "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{timestamp}:{password}",
            "queryParams": "{}",
            "optIntoOneTap": "false"
        }
        
        url = "https://www.instagram.com/accounts/login/ajax/"
        
        return await self.session.post(
            url,
            data=data,
            headers=headers
        )
