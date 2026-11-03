"""Calendar's tests: the real record store and gate, and quill.py, on this machine."""

import datetime as dt

import pytest
from cloudmorrow.quill.testing import Harness

import quill as code


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
    event = q.seed(
        "event",
        calendar=mine.id,
        title="Dentist",
        starts_at="2026-10-01T10:00",
        ends_at="2026-10-01T11:00",
        location="High St",
    )
    result = q.act("copy-to-next-week", event)
    assert result.toast == "Dentist is on 2026-10-08 too"
    ((model, copy_id),) = result.opened
    copy = q.get(model, copy_id)
    assert (copy["starts_at"], copy["ends_at"], copy["location"]) == ("2026-10-08T10:00", "2026-10-08T11:00", "High St")
    assert copy["calendar"] == mine.id


def test_an_all_day_event_stays_all_day(q):
    everybody = calendar(q, "Everybody")
    event = q.seed(
        "event", calendar=everybody.id, title="Holiday", starts_at="2026-10-12", ends_at="2026-10-16", all_day=True
    )
    ((model, copy_id),) = q.act("copy-to-next-week", event).opened
    copy = q.get(model, copy_id)
    assert (copy["starts_at"], copy["ends_at"], copy["all_day"]) == ("2026-10-19", "2026-10-23", True)


def test_nobody_copies_what_they_cannot_see(q):
    event = q.seed("event", calendar=calendar(q, "alice").id, title="Mine", starts_at="2026-10-01")
    assert q.as_user("sam").act("copy-to-next-week", event).refused


# -- calendars from elsewhere ----------------------------------------------------------
FEED = "https://calendar.example/club/basic.ics"

ZONE = """BEGIN:VTIMEZONE
TZID:Europe/Copenhagen
BEGIN:DAYLIGHT
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
TZNAME:CEST
DTSTART:19700329T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
TZNAME:CET
DTSTART:19701025T030000
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
END:STANDARD
END:VTIMEZONE
"""


def ics(*events, name="Bram's club", zone=ZONE):
    body = "".join(f"BEGIN:VEVENT\n{e.strip()}\nEND:VEVENT\n" for e in events)
    return f"BEGIN:VCALENDAR\nVERSION:2.0\nX-WR-CALNAME:{name}\n{zone}{body}END:VCALENDAR\n"


TODAY = dt.date.today()
NEXT = TODAY + dt.timedelta(days=10)
SINCE, UNTIL = TODAY - dt.timedelta(days=365), TODAY + dt.timedelta(days=730)


def compact(day):
    return day.strftime("%Y%m%d")


def test_a_whole_day_event_is_a_date_and_its_end_is_its_last_day():
    feed = code.parse_feed(
        ics("""
UID:a@example
DTSTART;VALUE=DATE:20260101
DTEND;VALUE=DATE:20260103
SUMMARY:New year\\, slowly
DESCRIPTION:Line one\\nLine two
"""),
        since=dt.date(2025, 1, 1),
        until=dt.date(2027, 1, 1),
    )
    assert feed.name == "Bram's club"
    ((key, event),) = feed.events.items()
    assert key == "a@example"
    assert event == {
        "title": "New year, slowly",
        "starts_at": "2026-01-01",
        "ends_at": "2026-01-02",
        "all_day": True,
        "location": "",
        "notes": "Line one\nLine two",
    }


def test_a_moment_in_the_feeds_own_zone_is_kept_in_utc_winter_and_summer_alike():
    feed = code.parse_feed(
        ics(
            """
UID:w@example
DTSTART;TZID=Europe/Copenhagen:20260115T100000
DTEND;TZID=Europe/Copenhagen:20260115T113000
SUMMARY:Winter
LOCATION:The hall
""",
            """
UID:s@example
DTSTART;TZID=Europe/Copenhagen:20260715T100000
SUMMARY:Summer
""",
            """
UID:u@example
DTSTART:20260301T080000Z
DTEND:20260301T090000Z
SUMMARY:Already UTC
""",
            """
UID:f@example
DTSTART:20260301T080000
SUMMARY:On the wall
""",
        ),
        since=dt.date(2025, 1, 1),
        until=dt.date(2027, 1, 1),
    )
    winter, summer, utc, wall = feed.events.values()
    assert (winter["starts_at"], winter["ends_at"], winter["location"]) == (
        "2026-01-15T09:00:00+00:00",
        "2026-01-15T10:30:00+00:00",
        "The hall",
    )
    # Without an end a timed event is an hour, as one typed here would be.
    assert (summer["starts_at"], summer["ends_at"]) == ("2026-07-15T08:00:00+00:00", "2026-07-15T09:00:00+00:00")
    assert utc["starts_at"] == "2026-03-01T08:00:00+00:00"
    assert wall["starts_at"] == "2026-03-01T08:00" and wall["all_day"] is False


def test_a_recurring_event_is_every_time_it_happens_in_the_window_each_findable_again():
    first = dt.date(2026, 1, 5)  # a Monday
    feed = code.parse_feed(
        ics(
            f"""
UID:r@example
DTSTART;TZID=Europe/Copenhagen:{compact(first)}T180000
DTEND;TZID=Europe/Copenhagen:{compact(first)}T193000
RRULE:FREQ=WEEKLY;BYDAY=MO,WE;COUNT=6
EXDATE;TZID=Europe/Copenhagen:20260112T180000
SUMMARY:Training
""",
            """
UID:r@example
RECURRENCE-ID;TZID=Europe/Copenhagen:20260114T180000
DTSTART;TZID=Europe/Copenhagen:20260115T180000
DTEND;TZID=Europe/Copenhagen:20260115T190000
SUMMARY:Training (moved)
""",
            """
UID:r@example
RECURRENCE-ID;TZID=Europe/Copenhagen:20260119T180000
STATUS:CANCELLED
SUMMARY:Training
""",
        ),
        since=dt.date(2025, 6, 1),
        until=dt.date(2027, 1, 1),
    )
    keys = list(feed.events)
    # Six by COUNT: 5, 7, 12, 14, 19, 21 January — the 12th left out, the
    # 14th moved to the 15th, the 19th cancelled.
    assert keys == [
        "r@example@20260105T170000",
        "r@example@20260107T170000",
        "r@example@20260114T170000",
        "r@example@20260121T170000",
    ]
    moved = feed.events["r@example@20260114T170000"]
    assert (moved["title"], moved["starts_at"], moved["ends_at"]) == (
        "Training (moved)",
        "2026-01-15T17:00:00+00:00",
        "2026-01-15T18:00:00+00:00",
    )
    assert feed.events["r@example@20260121T170000"]["title"] == "Training"


def test_monthly_yearly_and_until_rules_land_on_the_right_days():
    window = dict(since=dt.date(2026, 1, 1), until=dt.date(2026, 12, 31))
    last_fridays = code.occurrences(dt.date(2026, 1, 30), {"FREQ": "MONTHLY", "BYDAY": "-1FR"}, **window)
    assert last_fridays[:3] == [dt.date(2026, 1, 30), dt.date(2026, 2, 27), dt.date(2026, 3, 27)]
    birthdays = code.occurrences(dt.date(1990, 6, 14), {"FREQ": "YEARLY"}, **window)
    assert birthdays == [dt.date(2026, 6, 14)]
    fortnightly = code.occurrences(
        dt.datetime(2026, 3, 2, 9, 0), {"FREQ": "WEEKLY", "INTERVAL": "2", "UNTIL": "20260401T000000Z"}, **window
    )
    assert fortnightly == [dt.datetime(2026, 3, 2, 9), dt.datetime(2026, 3, 16, 9), dt.datetime(2026, 3, 30, 9)]
    # The window cuts, and a daily rule with no end stops at its far edge.
    daily = code.occurrences(dt.date(2020, 1, 1), {"FREQ": "DAILY"}, **window)
    assert (daily[0], daily[-1], len(daily)) == (dt.date(2026, 1, 1), dt.date(2026, 12, 31), 365)
    # COUNT counts from the start, not from the window: five days in 2020 are none in 2026.
    assert code.occurrences(dt.date(2020, 1, 1), {"FREQ": "DAILY", "COUNT": "5"}, **window) == []


def test_lines_are_unfolded_and_parameters_may_hold_colons():
    lines = code.unfold('DESCRIPTION:A long\r\n  line\r\nX;P="a:b":v\r\n')
    assert lines == ["DESCRIPTION:A long line", 'X;P="a:b":v']
    assert code.split_line(lines[1]) == ("X", {"P": "a:b"}, "v")


def club(q, *events, **more):
    q.fetch.add(FEED, text=ics(*events, **more), headers={"Content-Type": "text/calendar"})


MATCH = f"""
UID:m1@example
DTSTART;VALUE=DATE:{compact(NEXT)}
DTEND;VALUE=DATE:{compact(NEXT + dt.timedelta(days=1))}
SUMMARY:Away match
"""
TRAINING = f"""
UID:t1@example
DTSTART:{compact(TODAY)}T170000Z
DTEND:{compact(TODAY)}T183000Z
SUMMARY:Training
LOCATION:The pitch
"""


def subscribed(q):
    return next(c for c in q.list("calendar") if c.get("calendar.url"))


def test_subscribing_makes_a_calendar_of_your_own_read_from_the_feed(q):
    club(q, MATCH, TRAINING)
    result = q.act("subscribe", url="webcal://calendar.example/club/basic.ics")
    assert result.ok, result.error
    assert result.toast == "Bram's club: 2 events, read again every hour"
    feed = subscribed(q)
    assert (feed["name"], feed["calendar.url"], feed.scope, feed.owner) == ("Bram's club", FEED, "personal", "alice")
    assert feed["colour"] == "green"  # cyan and violet are taken
    assert feed["calendar.refreshed"][:4] == str(TODAY)[:4] and not feed.get("calendar.trouble")
    events = {e["calendar.uid"]: e for e in q.list("event", calendar=feed.id)}
    assert events["m1@example"]["starts_at"] == str(NEXT) and events["m1@example"]["all_day"] is True
    assert events["t1@example"]["location"] == "The pitch"
    assert q.fetch.sent[-1]["headers"]["Accept"].startswith("text/calendar")


def test_a_name_of_your_own_and_a_feed_that_cannot_be_read(q):
    club(q, MATCH)
    assert q.act("subscribe", url=FEED, name="The club").ok
    assert subscribed(q)["name"] == "The club"
    result = q.act("subscribe", url="https://nowhere.example/x.ics")
    assert not result.ok and "answered 404" in result.error
    q.fetch.add("https://calendar.example/page", text="<html>not a calendar</html>")
    assert "not a calendar" in q.act("subscribe", url="https://calendar.example/page").error
    assert "https://" in q.act("subscribe", url="ftp://calendar.example/x.ics").error


def test_a_refresh_changes_what_changed_takes_off_what_went_and_what_was_put_there_by_hand(q):
    club(q, MATCH, TRAINING)
    assert q.act("subscribe", url=FEED).ok
    feed = subscribed(q)
    stray = q.seed("event", calendar=feed.id, title="Mine", starts_at=str(TODAY))
    club(q, MATCH.replace("Away match", "Home match"))
    result = q.act("refresh", feed)
    assert result.ok and result.toast == "Bram's club: 1 events"
    events = q.list("event", calendar=feed.id)
    assert [(e["title"], e["calendar.uid"]) for e in events] == [("Home match", "m1@example")]
    assert stray.id not in {e.id for e in events}
    # Not subscribed: nothing to refresh.
    mine = calendar(q, "alice")
    assert "not subscribed" in q.act("refresh", mine).error


def test_a_feed_that_stops_answering_keeps_what_was_read_and_says_so(q):
    club(q, MATCH)
    assert q.act("subscribe", url=FEED).ok
    q.fetch.add(FEED, text="gone", status=500)
    result = q.act("refresh", subscribed(q))
    assert not result.ok and "answered 500" in result.error
    feed = subscribed(q)
    assert feed["calendar.trouble"] == "calendar.example answered 500; the 1 events already here are kept"
    club(q, MATCH)
    assert q.act("refresh", feed).ok
    assert not subscribed(q).get("calendar.trouble")
    assert len(q.list("event", calendar=feed.id)) == 1


def test_every_hour_each_persons_own_subscriptions_are_read_again(q):
    club(q, MATCH)
    assert q.act("subscribe", url=FEED).ok
    sam = q.as_user("sam")
    sam.fetch.add("https://other.example/sam.ics", text=ics(TRAINING, name="Sam's"))
    assert sam.act("subscribe", url="https://other.example/sam.ics").ok
    club(q, MATCH, TRAINING)
    q.run_job("refresh")
    assert len(q.list("event", calendar=subscribed(q).id)) == 2
    assert [e["title"] for e in sam.list("event", calendar=subscribed(sam).id)] == ["Training"]
    # Sam's subscription is Sam's: Alice does not see it, and did not touch it.
    assert [c["name"] for c in q.list("calendar") if c.get("calendar.url")] == ["Bram's club"]


def test_changing_the_address_on_the_sheet_reads_the_new_feed_and_clearing_it_takes_the_feed_off(q):
    club(q, MATCH)
    assert q.act("subscribe", url=FEED).ok
    feed = subscribed(q)
    q.fetch.add("https://other.example/new.ics", text=ics(TRAINING, name="New"))
    q.change("calendar", feed.id, {"calendar.url": "https://other.example/new.ics"})
    assert [e["title"] for e in q.list("event", calendar=feed.id)] == ["Training"]
    q.change("calendar", feed.id, {"calendar.url": ""})
    assert q.list("event", calendar=feed.id) == []
    assert not q.get("calendar", feed.id)["calendar.refreshed"]


def test_unsubscribing_takes_the_calendar_and_what_was_on_it_away(q):
    club(q, MATCH)
    assert q.act("subscribe", url=FEED).ok
    feed = subscribed(q)
    assert "not subscribed" in q.act("unsubscribe", calendar(q, "alice")).error
    result = q.act("unsubscribe", feed)
    assert result.ok and result.toast == "Bram's club is gone"
    assert [c["name"] for c in q.list("calendar")] == ["Everybody", "alice"] or sorted(
        c["name"] for c in q.list("calendar")
    ) == ["Everybody", "alice"]
    assert q.list("event") == []


def test_copying_from_a_subscribed_calendar_lands_on_your_own(q):
    club(q, MATCH)
    assert q.act("subscribe", url=FEED).ok
    match = q.list("event", calendar=subscribed(q).id)[0]
    ((model, copy_id),) = q.act("copy-to-next-week", match).opened
    copy = q.get(model, copy_id)
    assert copy["calendar"] == calendar(q, "alice").id
    assert copy["starts_at"] == str(NEXT + dt.timedelta(days=7)) and not copy.get("calendar.uid")
