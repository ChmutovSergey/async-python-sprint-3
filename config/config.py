from pydantic import BaseSettings


class DBSettings(BaseSettings):
    name: str = "async_python_sprint_3"
    url: str = f"sqlite+aiosqlite:///{name}.db"


class ApiSettings(BaseSettings):
    host: str = "localhost"
    port: int = 8080


class ServerSettings(BaseSettings):
    host: str = "localhost"
    port: int = 8888
    count_last_message: int = 20


class Settings(BaseSettings):
    db = DBSettings()
    api = ApiSettings()
    server = ServerSettings()


settings = Settings()
