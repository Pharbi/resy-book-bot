import importlib.util
import logging

spec = importlib.util.spec_from_file_location(
    "resy_api_wrapper", "backend/app/core/resy_api_wrapper.py"
)
rw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rw)


class DummyResp:
    def __init__(self, status, data=None):
        self.status_code = status
        self._data = data or {}

    def json(self):
        return self._data


class DummySession:
    def __init__(self):
        self.headers = {}
        self.post_args = None

    def post(self, url, json=None):
        self.post_args = (url, json)
        return DummyResp(200)


def test_search_availability_builds_payload(monkeypatch):
    session = DummySession()
    monkeypatch.setattr(rw, "create_scraper", lambda: session)
    wrapper = rw.ResyApiWrapper("api.example.com", "key", logging.getLogger("t"))
    wrapper.search_availability({"party_size": 2})
    url, payload = session.post_args
    assert url == "https://api.example.com/graphql"
    assert payload["operationName"] == "SearchAvailability"
    assert payload["variables"]["input"] == {"party_size": 2}

