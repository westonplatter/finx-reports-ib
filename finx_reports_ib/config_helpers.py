import json
from typing import Dict

from dotenv import dotenv_values


def get_config(file_name: str) -> Dict:
    """
    Returns `file_name` lines as Dict.

    Uses dotenv

    Args:
        file_name (str): env file name. Default = .env

    Returns:
        Dict:
    """
    return dotenv_values(file_name)


def get_ib_json(configs: Dict) -> Dict:
    """
    Returns the json parsed value for the IB_JSON env var.

    This should be a json string

    Args:
        configs (Dict): env file contents

    Returns:
        dict: IB_JSON parsed as json
    """
    return json.loads(configs["IB_JSON"])


def get_discord_webhook_url(configs: Dict) -> str:
    """
    Returns the discord portfolios webhook

    Args:
        configs (Dict): env file contents

    Returns:
        str: discord webhook url
    """
    return configs["PORTFOLIOS_DISCORD_WEBHOOK_URL"]
