from pathlib import Path
import os



ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


def load_dotenv_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().lstrip("\ufeff")
        os.environ.setdefault(key, value.strip().strip('"').strip("'"))


load_dotenv_file(ENV_FILE)


class Settings:
    def __init__(self) -> None:
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://product_agent:product_agent_dev@localhost:5432/product_agent",
        )
        self.embedding_provider = os.getenv("EMBEDDING_PROVIDER", "hashing")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-v4")
        self.embedding_dimension = int(os.getenv("EMBEDDING_DIMENSION", "1024"))
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.dashscope_api_key = os.getenv("DASHSCOPE_API_KEY", "")
        self.llm_provider = os.getenv("LLM_PROVIDER", "template")
        self.llm_model = os.getenv("LLM_MODEL", "qwen-turbo")
        self.search_proxy = os.getenv("SEARCH_PROXY", "")


settings = Settings()
