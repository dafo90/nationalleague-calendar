# National League Calendar

Automatically generated `.ics` calendars for Swiss National League (ice hockey) games, built from the [nationalleague.ch](https://www.nationalleague.ch) API.

A [scheduled workflow](.github/workflows/schedule.yml) runs once a day and regenerates the calendars, which are then published via GitHub Pages so you can subscribe to them directly from your own calendar app (Google Calendar, Apple Calendar, Outlook, etc.).

## How it works

- Only games from the **2026-2027 season onward** are included (older exhibition games from previous seasons are skipped).
- Exhibition/friendly games are kept, but clearly tagged as `Exhibition` in the event title and description.
- A separate calendar is generated for every team that plays at least one regular-season game. Teams that only ever appear in an exhibition match (e.g. a foreign club playing a single friendly) don't get their own calendar, but their games are still visible in the calendar of their National League opponent and in the combined "all games" calendar below.
- Each team's calendar includes **all** of that team's games — regular season and exhibition alike.
- Re-running the workflow updates existing events in place (score, time, or venue changes are reflected) and never duplicates or loses events, even if the source API's data changes shape or order between runs.

## Subscribing to a calendar

Use "Add calendar from URL" (or equivalent) in your calendar app, pointing to the relevant link below.

### All games

| Calendar                  | Link                                                     |
| ------------------------- | -------------------------------------------------------- |
| All National League games | `https://dafo.github.io/nationalleague-calendar/all.ics` |

### Team calendars

| Team               | Link                                                                    |
| ------------------ | ----------------------------------------------------------------------- |
| EHC Biel-Bienne    | `https://dafo.github.io/nationalleague-calendar/ehc-biel-bienne.ics`    |
| EHC Kloten         | `https://dafo.github.io/nationalleague-calendar/ehc-kloten.ics`         |
| EV Zug             | `https://dafo.github.io/nationalleague-calendar/ev-zug.ics`             |
| Fribourg-Gottéron  | `https://dafo.github.io/nationalleague-calendar/fribourg-gotteron.ics`  |
| Genève-Servette HC | `https://dafo.github.io/nationalleague-calendar/geneve-servette-hc.ics` |
| HC Ajoie           | `https://dafo.github.io/nationalleague-calendar/hc-ajoie.ics`           |
| HC Ambri-Piotta    | `https://dafo.github.io/nationalleague-calendar/hc-ambri-piotta.ics`    |
| HC Davos           | `https://dafo.github.io/nationalleague-calendar/hc-davos.ics`           |
| HC Lugano          | `https://dafo.github.io/nationalleague-calendar/hc-lugano.ics`          |
| Lausanne HC        | `https://dafo.github.io/nationalleague-calendar/lausanne-hc.ics`        |
| SC Bern            | `https://dafo.github.io/nationalleague-calendar/sc-bern.ics`            |
| SCL Tigers         | `https://dafo.github.io/nationalleague-calendar/scl-tigers.ics`         |
| SCRJ Lakers        | `https://dafo.github.io/nationalleague-calendar/scrj-lakers.ics`        |
| ZSC Lions          | `https://dafo.github.io/nationalleague-calendar/zsc-lions.ics`          |

> **Note:** filenames are derived automatically from each team's current name on nationalleague.ch (lowercased, accents stripped, spaces/punctuation replaced with `-`). If a team is renamed or a new team is promoted to the league, its filename will follow the same pattern and a new row can be added here.

## Publishing setup (one-time)

In this repository's **Settings → Pages**, set **Source** to **"GitHub Actions"** (not "Deploy from a branch"). The workflow already uploads the contents of `output/` as the Pages artifact and deploys it on every run, so no further configuration is needed — the first successful workflow run will publish the site.

## Running it yourself

```bash
pip install -r requirements.txt
python3 generate_calendar.py
```

This writes/updates the `.ics` files inside the `output/` directory. The script is safe to re-run repeatedly and merges new data into whatever's already on disk, so make sure `output/` persists between runs (e.g. via a Git commit in CI) rather than being recreated from scratch each time.