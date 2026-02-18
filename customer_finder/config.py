import os
from pathlib import Path
from typing import Dict

def load_config() -> Dict[str, str]:
    """加载配置（从环境变量或 .env 文件）"""
    env_file = Path(".env")
    
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.strip() and not line.startswith("#"):
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()
    
    required_keys = ["OPENAI_API_KEY"]
    config = {}
    
    for key in required_keys:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"缺少必需的环境变量: {key}")
        config[key.lower()] = value
    
    # Reddit 配置（可选）
    config["reddit_client_id"] = os.getenv("REDDIT_CLIENT_ID", "")
    config["reddit_client_secret"] = os.getenv("REDDIT_CLIENT_SECRET", "")
    config["reddit_user_agent"] = os.getenv("REDDIT_USER_AGENT", "customer-finder/0.1")
    
    return config