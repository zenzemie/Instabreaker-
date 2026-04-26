import random
from typing import Dict

class StealthManager:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
        ]
        
    def get_random_user_agent(self) -> str:
        return random.choice(self.user_agents)

    def get_headers(self, target_username: str = None) -> Dict[str, str]:
        ua = self.get_random_user_agent()
        headers = {
            "User-Agent": ua,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"https://www.instagram.com/{target_username}/" if target_username else "https://www.instagram.com/",
            "Origin": "https://www.instagram.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Connection": "keep-alive",
        }
        
        # Add Sec-Ch-Ua headers if it's a Chrome User Agent
        if "Chrome" in ua:
            headers.update({
                "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                "sec-ch-ua-mobile": "?0" if "Windows" in ua or "Macintosh" in ua or "Linux" in ua else "?1",
                "sec-ch-ua-platform": '"Windows"' if "Windows" in ua else '"macOS"' if "Macintosh" in ua else '"Linux"' if "Linux" in ua else '"iOS"'
            })
            
        return headers

    def get_impersonate(self) -> str:
        """Returns a string for curl_cffi impersonate option"""
        return random.choice(["chrome110", "chrome120", "safari15_5", "edge101"])
