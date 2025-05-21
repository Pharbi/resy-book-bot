import pytest
from sortedcontainers import SortedList
from app.core.resy_client import build_priority_list


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
