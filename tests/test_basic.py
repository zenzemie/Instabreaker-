import pytest
from instabreaker.utils.config import settings
from instabreaker.core.session import SessionManager

def test_config_dirs():
    assert settings.app_dir.exists()
    assert settings.sessions_dir.exists()

def test_session_manager_init():
    sm = SessionManager("testuser")
    assert sm.username == "testuser"
    assert sm.session_file.name == "testuser.json"
