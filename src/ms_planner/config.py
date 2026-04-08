from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    tenant_id: str
    client_id: str
    client_secret: str
    graph_base_url: str = "https://graph.microsoft.com/v1.0"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
