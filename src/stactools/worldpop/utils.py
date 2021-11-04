import json
import os
from datetime import datetime
from typing import Any, List
from urllib.parse import urlparse

import requests
from pystac.collection import Collection

from stactools.worldpop.constants import API_URL


def get_metadata(url: str) -> Any:
    """Return dictionary from JSON file at given path."""
    scheme = urlparse(url).scheme
    if scheme == "http" or scheme == "https":
        response = requests.get(url)
        if response.status_code != 200:
            raise AssertionError(f"API URL not found: {url}")
        return response.json()
    else:
        if not os.path.exists(url):
            raise AssertionError(f"File path not found: {url}")
        with open(url) as f:
            return json.load(f)


def get_iso3_list(project: str, category: str) -> List[str]:
    """Return a list of ISO3 country codes contained in a dataset/subset."""
    url = f"{API_URL}/{project}/{category}"
    response = requests.get(url)
    if response.status_code != 200:
        raise AssertionError(f"{response.status_code} code from API: {url}")
    data = response.json()["data"]
    return list(sorted(set([d["iso3"] for d in data])))


def get_popyears(collection: Collection) -> List[str]:
    """Return a list of years making up the temporale extent of a collection."""
    startstop: Any = collection.extent.temporal.intervals[0]
    start, stop_ = startstop
    if start is None:
        raise AssertionError("Collection's temporal extent starts at None")
    stop = stop_.year if stop_ is not None else datetime.now().year - 1
    return [str(y) for y in range(int(start.year), int(stop) + 1)]
