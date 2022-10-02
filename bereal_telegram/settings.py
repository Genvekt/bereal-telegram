import dataclasses
import environ
from dataclasses import dataclass, fields
from dotenv import load_dotenv


@dataclass
class Settings:
    TELEGRAM_TOKEN: str
    DEVELOPER_CHAT_ID: int


def load_settings(prefix: str = 'BEREAL_') -> Settings:
    """
    Loads each field in Settings from env with specified prefix

    Args:
        prefix (str, optional): prefix to add to each env name.
            Defaults to 'BEREAL_'.
    Returns:
        Settings object with loaded from env fields
    Rises:
        environ.compat.ImproperlyConfigured: If env without default value
            is missing.
    """
    load_dotenv()
    env = environ.Env()
    params = dict()
    for field in fields(Settings):
        env_name = prefix + field.name
        if field.default == dataclasses.MISSING:
            params[field.name] = env.get_value(env_name, field.type)
        else:
            params[field.name] = env.get_value(env_name, field.type, field.default)
    return Settings(**params)