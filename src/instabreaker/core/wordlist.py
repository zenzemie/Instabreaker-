import itertools
from typing import List, Optional
from openai import OpenAI
from ..utils.config import settings

class WordlistGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def generate_from_template(self, name: str, birth_year: Optional[str] = None, keywords: List[str] = None) -> List[str]:
        """Generate common password patterns without AI."""
        keywords = keywords or []
        bases = [name.lower(), name.capitalize()]
        if birth_year:
            bases.append(birth_year)
            bases.append(birth_year[-2:])
        
        for kw in keywords:
            bases.append(kw.lower())
            bases.append(kw.capitalize())
            
        suffixes = ["", "123", "!", "123!", "2023", "2024", "2025", "2026"]
        
        results = set()
        for base in bases:
            for suffix in suffixes:
                results.add(f"{base}{suffix}")
        
        return list(results)

    async def generate_with_ai(self, profile_info: str) -> List[str]:
        """Generate personalized passwords using AI."""
        if not self.client:
            raise ValueError("OpenAI API key is required for AI generation.")

        prompt = f"""
        Based on the following Instagram profile info, generate a list of 50 potential passwords 
        that this person might use. Focus on combinations of names, dates, interests, and common patterns.
        Return only the passwords, one per line.
        
        Profile Info:
        {profile_info}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.choices[0].message.content
        return [line.strip() for line in content.splitlines() if line.strip()]
