import os

import requests

BASE_URL = "https://api.open.fec.gov/v1"


class FECClient:
    """Thin wrapper around the OpenFEC API.

    Without a key it falls back to DEMO_KEY, which is rate limited.
    Get a free key at https://api.data.gov/signup/ and set FEC_API_KEY.
    """

    def __init__(self, api_key=None, session=None):
        self.api_key = api_key or os.environ.get("FEC_API_KEY", "DEMO_KEY")
        self.session = session or requests.Session()

    def get(self, path, **params):
        params["api_key"] = self.api_key
        url = f"{BASE_URL}/{path.strip('/')}/"
        resp = self.session.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def paginate(self, path, max_pages=5, **params):
        """Numbered pages, 100 rows each."""
        page = 1
        while page <= max_pages:
            data = self.get(path, page=page, per_page=100, **params)
            yield from data.get("results", [])
            if page >= data.get("pagination", {}).get("pages", 1):
                break
            page += 1

    def keyset_paginate(self, path, max_pages=5, **params):
        """For endpoints like Schedule B that page with last_indexes."""
        for _ in range(max_pages):
            data = self.get(path, **params)
            results = data.get("results", [])
            yield from results
            last = (data.get("pagination") or {}).get("last_indexes")
            if not results or not last:
                break
            params.update(last)
