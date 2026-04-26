import json
from pathlib import Path
from typing import Dict, Any
from ..utils.config import settings

class SessionManager:
    def __init__(self, username: str):
        self.username = username
        self.session_file = settings.sessions_dir / f"{username}.json"

    def save_session(self, cookies: Any):
        session_data = {
            "username": self.username,
            "cookies": dict(cookies)
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

    def save_checkpoint(self, target: str, last_index: int):
        checkpoint_file = settings.checkpoints_dir / f"{target}.json"
        with open(checkpoint_file, "w") as f:
            json.dump({"last_index": last_index}, f)

    def load_checkpoint(self, target: str) -> int:
        checkpoint_file = settings.checkpoints_dir / f"{target}.json"
        if checkpoint_file.exists():
            try:
                with open(checkpoint_file, "r") as f:
                    data = json.load(f)
                    return data.get("last_index", 0)
            except Exception:
                return 0
        return 0

    def clear_checkpoint(self, target: str):
        checkpoint_file = settings.checkpoints_dir / f"{target}.json"
        if checkpoint_file.exists():
            checkpoint_file.unlink()
