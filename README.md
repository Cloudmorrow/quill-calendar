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
| Datamodels | uses the foundational `calendar` (a space: personal, shared or public) and `event` (in a calendar), domain *Calendars* |
| Screens | one calendar: a month and the day's list on the phone, a week and a month on the web app, a month and the day in the terminal, `cm calendar list --from --to` and `add`, and to your assistant |
| Jobs | none |
| Datasets | `yours`: a personal calendar for each person, named after them; `everybody`: one public calendar for the server |
| Actions | **Copy to next week** on an event — on its sheet, `cm calendar copy-to-next-week`, and to your assistant |
| Services, webhooks, APIs | none |

Its code is [`quill.py`](quill.py): the one action, run in the sandbox as whoever presses it. Everything else is declared in [`quill.toml`](quill.toml).

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
