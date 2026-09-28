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
