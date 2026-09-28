"""Calendar's tests: the real record store and gate, and quill.py, on this machine."""

import pytest

from cloudmorrow.quill.testing import Harness


@pytest.fixture()
def q():
    with Harness(".") as harness:
        yield harness


def calendar(q, name):
    return next(c for c in q.list("calendar") if c["name"] == name)


def test_everybody_has_their_own_calendar_and_there_is_one_for_everybody(q):
    names = sorted(c["name"] for c in q.list("calendar"))
    assert names == ["Everybody", "alice"]


def test_a_wall_clock_event_is_copied_to_the_same_time_next_week(q):
    mine = calendar(q, "alice")
    event = q.seed("event", calendar=mine.id, title="Dentist", starts_at="2026-10-01T10:00",
                   ends_at="2026-10-01T11:00", location="High St")
    result = q.act("copy-to-next-week", event)
    assert result.toast == "Dentist is on 2026-10-08 too"
    (model, copy_id), = result.opened
    copy = q.get(model, copy_id)
    assert (copy["starts_at"], copy["ends_at"], copy["location"]) == ("2026-10-08T10:00", "2026-10-08T11:00", "High St")
    assert copy["calendar"] == mine.id


def test_an_all_day_event_stays_all_day(q):
    everybody = calendar(q, "Everybody")
    event = q.seed("event", calendar=everybody.id, title="Holiday", starts_at="2026-10-12",
                   ends_at="2026-10-16", all_day=True)
    (model, copy_id), = q.act("copy-to-next-week", event).opened
    copy = q.get(model, copy_id)
    assert (copy["starts_at"], copy["ends_at"], copy["all_day"]) == ("2026-10-19", "2026-10-23", True)


def test_nobody_copies_what_they_cannot_see(q):
    event = q.seed("event", calendar=calendar(q, "alice").id, title="Mine", starts_at="2026-10-01")
    assert q.as_user("sam").act("copy-to-next-week", event).refused
