from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel, Field

class ClientConfig(BaseModel):
    api_url: str = Field("http://localhost:8000", description="Base API URL")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    timeout: float = Field(30.0, description="Request timeout in seconds")
    max_retries: int = Field(3, description="Maximum retry attempts")
    retry_delay: float = Field(1.0, description="Initial retry delay in seconds")

def load_config(config_path: Path = Path("config.yml")) -> ClientConfig:
    """Load configuration from YAML file."""
    if not config_path.exists():
        return ClientConfig()
    
    with open(config_path) as f:
        config_data = yaml.safe_load(f) or {}
        return ClientConfig(**config_data) 