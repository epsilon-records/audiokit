from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional

class ClientConfig(BaseModel):
    server_url: str = Field("http://localhost:8000", 
                          description="AI server base URL")
    api_key: Optional[str] = Field(None, 
                                 description="API key for authentication")
    timeout: int = Field(30, 
                       description="Default request timeout in seconds")
    version: str = Field("0.1.0",
                       description="Client version")
    cache_dir: Path = Field(Path.home() / ".audiokit_cache",
                          description="Cache directory for temporary files")
    retries: int = Field(3, description="Number of retry attempts")
    retry_delay: float = Field(0.5, description="Delay between retries in seconds")
    
    class Config:
        env_prefix = "AUDIOKIT_"
        case_sensitive = False 