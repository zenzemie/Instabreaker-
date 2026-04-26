import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional

class ProfileScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    async def scrape_profile(self, username: str) -> Dict[str, Any]:
        url = f"https://www.instagram.com/{username}/"
        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True) as client:
            response = await client.get(url)
            if response.status_code != 200:
                return {}

            soup = BeautifulSoup(response.text, "html.parser")
            
            # Instagram often hides data in JSON-LD or meta tags
            description = soup.find("meta", property="og:description")
            title = soup.find("meta", property="og:title")
            
            profile_data = {
                "username": username,
                "full_name": "",
                "bio": "",
                "follower_count": "",
                "following_count": ""
            }

            if title:
                # Format: "Full Name (@username) • Instagram photos and videos"
                title_text = title.get("content", "")
                if "(" in title_text:
                    profile_data["full_name"] = title_text.split("(")[0].strip()

            if description:
                # Format: "Followers, Following, Posts - See Instagram photos and videos from Full Name (@username)"
                desc_text = description.get("content", "")
                profile_data["bio"] = desc_text
                
            return profile_data
