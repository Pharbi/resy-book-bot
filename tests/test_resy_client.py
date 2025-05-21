import logging
import pytest
from sortedcontainers import SortedList
from app.core.resy_client import ResyClient, build_priority_list


class DummyResp:
    def __init__(self, status, data=None):
        self.status_code = status
        self._data = data or {}

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
<<<<<<< ours
        "links": {"web": "http://example.com"},
=======
        "links": {"web": "http://example.com"\},
>>>>>>> theirs
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

