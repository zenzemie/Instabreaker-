import json
from pathlib import Path
from typing import Dict, Any
import httpx
from ..utils.config import settings

class SessionManager:
    def __init__(self, username: str):
        self.username = username
        self.session_file = settings.sessions_dir / f"{username}.json"

    def save_session(self, cookies: httpx.Cookies):
        session_data = {
            "username": self.username,
            "cookies": cookies.get_dict()
        }
        with open(self.session_file, "w") as f:
            json.dump(session_data, f, indent=4)

    def load_session(self) -> Dict[str, str] | None:
        if not self.session_file.exists():
            return None
        try:
            with open(self.session_file, "r") as f:
                data = json.load(f)
                return data.get("cookies")
        except Exception:
            return None

    @staticmethod
    def list_sessions() -> list[str]:
        return [p.stem for p in settings.sessions_dir.glob("*.json")]

    def delete_session(self):
        if self.session_file.exists():
            self.session_file.unlink()
