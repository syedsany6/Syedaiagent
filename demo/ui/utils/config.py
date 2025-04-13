import tomllib
from pathlib import Path

from utils import constants


def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).resolve().parent.parent

PROJECT_ROOT = get_project_root()

class Config:

    address = []

    def __init__(self):
        self._load_initial_config()

    @staticmethod
    def _get_config_path() -> Path:
        root = PROJECT_ROOT
        config_path = root / "config" / "config.toml"
        if config_path.exists():
            return config_path
        raise FileNotFoundError("No configuration file found in config directory")

    def _load_initial_config(self):
        config_path = Config._get_config_path()
        with config_path.open("rb") as f:
            raw_config = tomllib.load(f)
        base_remote_agent_addresses = raw_config.get(constants.REMOTE_AGENT_ADDRESSES_KEY, {})
        self.address = list(base_remote_agent_addresses.values())

    @property
    def remote_agent_addresses(self) -> list[str]:
        return self.address

config = Config()

if __name__ == '__main__':
    print(config.remote_agent_addresses)