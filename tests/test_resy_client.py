import importlib.util
import logging
import os
import sys
import types
import pytest
from sortedcontainers import SortedList


def load_core_modules():
    original_app = sys.modules.pop("app", None)
    original_core = sys.modules.pop("app.core", None)
    fake_app = types.ModuleType("app")
    core_pkg = types.ModuleType("app.core")
    sys.modules["app"] = fake_app
    sys.modules["app.core"] = core_pkg

    spec = importlib.util.spec_from_file_location(
        "app.core.resy_api_wrapper",
        os.path.join("backend", "app", "core", "resy_api_wrapper.py"),
    )
    resy_api_wrapper_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(resy_api_wrapper_mod)
    sys.modules["app.core.resy_api_wrapper"] = resy_api_wrapper_mod
    core_pkg.resy_api_wrapper = resy_api_wrapper_mod
    core_pkg.ResyApiWrapper = resy_api_wrapper_mod.ResyApiWrapper

    spec = importlib.util.spec_from_file_location(
        "app.core.resy_client",
        os.path.join("backend", "app", "core", "resy_client.py"),
    )
    resy_client_mod = importlib.util.module_from_spec(spec)
    resy_client_mod.__package__ = "app.core"
    spec.loader.exec_module(resy_client_mod)
    sys.modules["app.core.resy_client"] = resy_client_mod
    originals = {"app": original_app, "app.core": original_core}
    return resy_client_mod, originals



@pytest.fixture(scope="module", autouse=True)
def core_modules_fixture():
    mod, originals = load_core_modules()
    global ResyClient, build_priority_list
    ResyClient = mod.ResyClient
    build_priority_list = mod.build_priority_list
    yield
    for name in [
        "app.core.resy_client",
        "app.core.resy_api_wrapper",
    ]:
        sys.modules.pop(name, None)
    if originals["app"] is not None:
        sys.modules["app"] = originals["app"]
    else:
        sys.modules.pop("app", None)
    if originals["app.core"] is not None:
        sys.modules["app.core"] = originals["app.core"]
    else:
        sys.modules.pop("app.core", None)


class DummyResp:
    def __init__(self, status, data=None):
        self.status_code = status
        self._data = data or {}
        self.text = ""

    def json(self):
        return self._data


class DummyAPI:
    def __init__(self, responses=None):
        self.responses = responses or {}
        self.token = None

    def set_resy_token(self, token):
        self.token = token

    def get_venue_details(self, venue_id):
        return self.responses.get('venue_details', DummyResp(404))

    def find_venue(self, query):
        return self.responses.get('find_venue', DummyResp(404))

def test_build_priority_list_selects_preceding_slots():
    slots = SortedList(
        [
            ("2023-03-04 18:00", "t1"),
            ("2023-03-04 18:30", "t2"),
            ("2023-03-04 19:00", "t3"),
        ],
        key=lambda s: s[0],
    )
    res_times = ["2023-03-04 18:15", "2023-03-04 19:15"]
    result = build_priority_list(slots, res_times)
    assert result == [("2023-03-04 18:00", "t1"), ("2023-03-04 19:00", "t3")]


def test_build_priority_list_exact_match():
    slots = SortedList(
        [
            ("2023-03-04 18:00", "t1"),
            ("2023-03-04 18:30", "t2"),
        ],
        key=lambda s: s[0],
    )
    res_times = ["2023-03-04 18:30"]
    result = build_priority_list(slots, res_times)
    assert result == [("2023-03-04 18:30", "t2")]


def test_get_venue_details_success():
    data = {
        "id": {"resy": "1"},
        "name": "Place",
        "links": {"web": "http://example.com"},
        "location": {"neighborhood": "Hood", "latitude": 1.0, "longitude": 2.0},
    }
    api = DummyAPI({"venue_details": DummyResp(200, data)})
    client = ResyClient(api, logging.getLogger("test"))
    details = client.get_venue_details("1")
    assert details == {
        "id": "1",
        "name": "Place",
        "website": "http://example.com",
        "neighborhood": "Hood",
        "lat": 1.0,
        "lon": 2.0,
    }


def test_get_venue_details_failure():
    api = DummyAPI({"venue_details": DummyResp(500)})
    client = ResyClient(api, logging.getLogger("test"))
    assert client.get_venue_details("1") is None


def test_find_venue_sets_primary():
    json_data = {
        "results": {
            "venues": [
                {
                    "venue": {
                        "location": {
                            "geo": {"lat": 1.234, "lon": 2.345},
                            "neighborhood": "N",
                        },
                        "name": "Test",
                        "id": {"resy": "42"},
                    },
                }
            ]
        }
    }
    api = DummyAPI({"find_venue": DummyResp(200, json_data)})
    client = ResyClient(api, logging.getLogger("test"))
    query = {"lat": 1.234, "long": 2.345}
    result = client.find_venue("uid", query)
    assert result["primary"] == {"id": "42", "name": "Test", "neighborhood": "N"}
    assert result["search"][0]["lat"] == 1.234

