import os

from app.streamlit_app import load_environment


def test_load_environment_supports_powershell_env_syntax(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text('$env:GROQ_API_KEY = "test-key"\n', encoding="utf-8")

    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    assert load_environment(dotenv_path=env_file) == "test-key"
    assert os.environ["GROQ_API_KEY"] == "test-key"
