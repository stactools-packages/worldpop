import json
from typing import Any, Union
from stactools.worldpop.constants import API_URL
import requests
import os
from urllib.parse import urlparse


def get_metadata(url: str) -> Union[dict[str, Any], None]:
    """Return dictionary from JSON file at given path."""
    scheme = urlparse(url).scheme
    if scheme == "http" or scheme == "https":
        response = requests.get(url)
        assert response.status_code == 200, f"API URL not found: {url}"
        return response.json()
    else:
        assert os.path.exists(url), f"File path not found: {url}"
        with open(url) as f:
            return json.load(f)


def get_iso3_list(dataset: str, subset:str) -> Union[list[str], None]:
    """Return a list of ISO3 country codes contained in a dataset/subset."""
    url = f"{API_URL}/{dataset}/{subset}"
    response = requests.get(url)
    assert response.status_code == 200, f"API URL not found: {url}"
    data = response.json()["data"]
    return [v["iso3"] for v in data.values()]
