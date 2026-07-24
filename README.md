# National League Calendar

Automatically generated `.ics` calendars for Swiss National League (ice hockey) games, built from the [nationalleague.ch](https://www.nationalleague.ch) API.

A [scheduled workflow](.github/workflows/schedule.yml) runs once a day and regenerates the calendars, committing the updated `.ics` files back to this repository so you can subscribe to them directly from your own calendar app (Google Calendar, Apple Calendar, Outlook, etc.) via their raw GitHub URLs.

## How it works

- Only games from the **2026-2027 season onward** are included (older exhibition games from previous seasons are skipped).
- Exhibition/friendly games are kept, but clearly tagged as `Exhibition` in the event title and description.
- A separate calendar is generated for every team that plays at least one regular-season game. Teams that only ever appear in an exhibition match (e.g. a foreign club playing a single friendly) don't get their own calendar, but their games are still visible in the calendar of their National League opponent and in the combined "all games" calendar below.
- Each team's calendar includes **all** of that team's games — regular season and exhibition alike.
- Re-running the workflow updates existing events in place (score, time, or venue changes are reflected) and never duplicates or loses events, even if the source API's data changes shape or order between runs.

## Subscribing to a calendar

Use "Add calendar from URL" (or equivalent) in your calendar app, pointing to the relevant link below.

### All games

| Calendar                  | Link                                                                                     |
| ------------------------- | ---------------------------------------------------------------------------------------- |
| All National League games | `https://raw.githubusercontent.com/dafo90/nationalleague-calendar/master/output/all.ics` |

### Team calendars

| Team               | Link                                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------------------- |
| EHC Biel-Bienne    | `https://raw.githubusercontent.com/dafo90/nationalleague-calendar/master/output/ehc-biel-bienne.ics`    |
| EHC Kloten         | `https://raw.githubusercontent.com/dafo90/nationalleague-calendar/master/output/ehc-kloten.ics`         |
| EV Zug             | `https://raw.githubusercontent.com/dafo90/nationalleague-calendar/master/output/ev-zug.ics`             |
| Fribourg-Gottéron  | `https://raw.githubusercontent.com/dafo90/nationalleague-calendar/master/output/fribourg-gotteron.ics`  |
| Genève-Servette HC | `https://raw.githubusercontent.com/dafo90/nationalleague-calendar/master/output/geneve-servette-hc.ics` |
| HC Ajoie           | `https://raw.githubusercontent.com/dafo90/nationalleague-calendar/master/output/hc-ajoie.ics`           |
| HC Ambri-Piotta    | `https://raw.githubusercontent.com/dafo90/nationalleague-calendar/master/output/hc-ambri-piotta.ics`    |
| HC Davos           | `https://raw.githubusercontent.com/dafo90/nationalleague-calendar/master/output/hc-davos.ics`           |
| HC Lugano          | `https://raw.githubusercontent.com/dafo90/nationalleague-calendar/master/output/hc-lugano.ics`          |
| Lausanne HC        | `https://raw.githubusercontent.com/dafo90/nationalleague-calendar/master/output/lausanne-hc.ics`        |
| SC Bern            | `https://raw.githubusercontent.com/dafo90/nationalleague-calendar/master/output/sc-bern.ics`            |
| SCL Tigers         | `https://raw.githubusercontent.com/dafo90/nationalleague-calendar/master/output/scl-tigers.ics`         |
| SCRJ Lakers        | `https://raw.githubusercontent.com/dafo90/nationalleague-calendar/master/output/scrj-lakers.ics`        |
| ZSC Lions          | `https://raw.githubusercontent.com/dafo90/nationalleague-calendar/master/output/zsc-lions.ics`          |

> **Note:** filenames are derived automatically from each team's current name on nationalleague.ch (lowercased, accents stripped, spaces/punctuation replaced with `-`). If a team is renamed or a new team is promoted to the league, its filename will follow the same pattern and a new row can be added here.

## Running it yourself

```bash
pip install -r requirements.txt
python3 generate_ics.py
```

This writes/updates the `.ics` files inside the `output/` directory. The script is safe to re-run repeatedly and merges new data into whatever's already on disk, so make sure `output/` persists between runs (e.g. via a Git commit in CI) rather than being recreated from scratch each time. Since the calendar links above point straight at the raw file content on GitHub, no separate publishing step is required — once the workflow commits an updated `output/` folder, the links above serve the new content automatically (allow a few minutes for GitHub's CDN cache to catch up).