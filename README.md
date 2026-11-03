# Calendar

A Quill for [Cloudmorrow](https://github.com/Cloudmorrow/cloudmorrow): your own
calendar, the ones you share with the people you live or work with, and one
the whole server shares.

- **Yours.** Everybody has exactly one, made the first time they look and
  named after them. Nobody else sees it.
- **Shared.** Anybody can make one and put people in it. There is no
  invitation to accept: they are added, they are told, and they can leave.
- **Everybody's.** One calendar the whole server sees and writes in, and
  nobody can leave.
- **Subscribed.** A calendar somebody else publishes — the club's fixtures,
  the bins, the public holidays — read into a calendar of your own from its
  address, every hour, and read-only.

Every calendar you can see is drawn at once, each event in the colour of
the calendar it is on — a calendar you have to switch between is one that
lets you double-book yourself.

Times are the times on the wall. "The dentist at ten" is stored as
`2026-10-01T10:00`, with no zone, and is at ten on every screen in October
and in June alike. An all-day event is a bare date, and its end is the last
day it is on.

## Using it

A calendar is a **space**, and an event is a record in one, so who may see
what is Cloudmorrow's rule for spaces and nothing of its own. Anyone can
make a shared calendar and put people in it; whoever made it (and an
administrator) can rename, recolour and delete it, and everybody in it can
write in it — a shared calendar you cannot write in is one you are being
*shown*. Being added is told behind the bell and with a push.

**An event is a title and two moments**, plus where it is and notes.
Whoever wrote it may change or delete it, and so may whoever manages the
calendar it is on — a shared calendar with somebody's stale event stuck on
it, and only that somebody able to fix it, is a worse rule. An end is
filled in when none is given — an hour, or the day it is on — and moving
the start on a record sheet keeps how long it is. Every calendar you can
see is drawn at once, each event in its calendar's colour (cyan, violet,
green, amber or rose). An event does not notify anybody: a house calendar
that pinged everybody for every appointment is one nobody reads.

**A calendar from elsewhere** is subscribed to by its address: the `.ics`
link Google Calendar, Outlook, a club's website and the rest hand out (a
`webcal://` one is fine too). *Subscribe to a calendar* is under the
calendar's title on the web and the phone, `ctrl+e` in the terminal, `cm
calendar subscribe url=…` on the command line, and a tool for your
assistant; it reads the feed once, makes a calendar of your own named as
the feed names itself (or as you say), in a colour of its own, and puts
the feed's events on it. From then on it is read again every hour, as you,
and *Refresh now* on its sheet reads it sooner. It is listed apart, under
*Subscribed*, and it is read-only: nothing is put on it from here, and what
is on it opens on a sheet that says it rather than one that changes it —
it is theirs to change, and the next refresh would put it back. *Copy to
next week* on one of its events copies onto your own calendar. The sheet
of a subscribed calendar says where it is read from (change the address
and the new feed is read; clear it and the feed's events go, the calendar
stays), when it was last read, and what went wrong if anything did — then
what was read before is kept. *Unsubscribe* takes it away, events and all.

What is read: every event a year back and two years on, whole days and
moments alike, recurring ones at every time they happen (daily, weekly,
monthly and yearly rules, with their exceptions and moved times), in the
zone the feed says they are in, shown in yours. Nothing is read that is
not the feed: no attachments, no attendees, no alarms.

**Looking, and putting something in:**

#### In the web app

On a phone, a month with a dot per event and the day you tap written out
under it; the add row takes "10:00 Dentist" for a time, or just a title for
a whole day, into the calendar picked beside it. On a computer, a week of
hours with whole-day things along the top, or the month with the events
written in its cells; the switch is beside the month's name. The people
icon is the list of calendars — yours, shared, everybody's — where one is
made (its name, who can see it, who is in it), and a calendar's own sheet
is where it is renamed, recoloured, shared, left and deleted.

#### In the terminal app

The **Calendar** card: the calendars on the left, the month beside them
with a coloured dot per event, the day you are standing on underneath. `n`
makes an event on that day, `e` (or `enter`) opens the one under the
cursor on its record sheet, `del` removes it, `c` makes a calendar, `p` (or
`enter` on a calendar) is who is in it — add, take out, leave — `r` renames
and recolours it, `t` is today, and `[` and `]` are the months. The list on
the left is not a filter: it picks which calendar a new event goes in.

#### On the command line

```
cm calendar list --from 2026-10-01 --to 2026-10-31
cm calendar add "Dentist" starts_at=2026-10-01T10:00       # into your own…
cm calendar add "Dinner" starts_at=2026-10-03T19:00 calendar=House   # …or a shared one
cm calendar copy-to-next-week <event>
cm calendar subscribe url=https://example.org/club.ics name="The club"
cm calendar refresh <calendar>
cm calendar unsubscribe <calendar>
```

---

The month is one call with a range on each moment —
`GET /api/records/event?starts_at__lte=2026-10-31T23:59&ends_at__gte=2026-10-01`
— because ISO sorts the way time does. An administrator can switch the
Quill off like any other: the tab goes and the API answers 403. A server
that had the built-in calendar got the Quill at boot, with its calendars
(and their people) and events moved into records once.

## What it adds to your Cloudmorrow

| | |
| --- | --- |
| Datamodels | uses the foundational `calendar` (a space: personal, shared or public) and `event` (in a calendar), domain *Calendars*; extends `calendar` with `calendar.url` (the feed a subscribed one is read from), `calendar.refreshed` and `calendar.trouble`, and `event` with `calendar.uid` (what the feed calls it) |
| Screens | one calendar: a month and the day's list on the phone, a week and a month on the web app, a month and the day in the terminal, `cm calendar list --from --to` and `add`, and to your assistant; a subscribed calendar is listed apart and read-only on every one of them |
| Jobs | `refresh`: every hour, as each person, their subscribed calendars read again |
| Hooks | the address on a calendar changed: the new feed is read, or, cleared, the feed's events taken off |
| Datasets | `yours`: a personal calendar for each person, named after them; `everybody`: one public calendar for the server |
| Actions | **Copy to next week** on an event; **Subscribe to a calendar** (an address, and a name if you like); **Refresh now** and **Unsubscribe** on a subscribed calendar — on the sheets, as `cm calendar …`, and to your assistant |
| Reaches | any address on the internet, to read the feeds you subscribe to; never a private one |
| Services, webhooks, APIs | none |

Its code is [`quill.py`](quill.py): the actions, the hook and the job, run in the sandbox as whoever presses, changes or holds, and a reader of iCalendar (RFC 5545) small enough to live there. Everything else is declared in [`quill.toml`](quill.toml).

## Working on it

See [CLAUDE.md](CLAUDE.md) and the skills in `.claude/skills/`. In short:

```
uv sync                  # .venv with Cloudmorrow and pytest
cm quill check           # the manifest, as a server would install it
cm quill test            # tests/, against the real record store and gate
cm quill test --sandbox  # the same, with the code in the sandbox
cm quill dev --local     # a throwaway server here, reinstalled as you save
```

## Licence

AGPL-3.0-or-later.
