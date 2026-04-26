import openai
from typing import List
from ..utils.config import settings

class AIEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.openai_api_key
        if self.api_key:
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None

    async def generate_wordlist(self, profile_data: dict, count: int = 100) -> List[str]:
        if not self.client:
            raise ValueError("OpenAI API key not set")

        prompt = f"""
        Analyze the following Instagram profile data and generate a list of {count} potential passwords 
        that this user might use. Focus on combinations of their name, bio info, common patterns, 
        and leetspeak variations.
        
        Profile Data:
        Username: {profile_data.get('username')}
        Full Name: {profile_data.get('full_name')}
        Bio: {profile_data.get('bio')}
        
        Output only the passwords, one per line, no other text.
        """

        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert security researcher and social engineer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )

        content = response.choices[0].message.content
        passwords = [p.strip() for p in content.split("\n") if p.strip()]
        return passwords
