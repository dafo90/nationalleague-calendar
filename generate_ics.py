#!/usr/bin/env python3

import html
import os
import re
import requests
from datetime import datetime, timedelta, timezone

from icalendar import Calendar, Event
import pytz


API_URL = "https://www.nationalleague.ch/api/games"
OUTPUT_DIR = "output"
TIMEZONE = "Europe/Zurich"
EXHIBITION_TAG = "Exhibition"

# Games before this date are considered part of an older season (e.g.
# exhibition games played during the 2025-2026 season) and are skipped.
# July 1st is used as a season boundary since the regular season always
# starts in September and the previous one always ends well before summer.
SEASON_CUTOFF = datetime(2026, 7, 1, tzinfo=timezone.utc)

# Statuses seen from the API. Anything not in this set is treated
# like "beforeStartOfPlay" (i.e. no score shown yet).
STATUS_FINISHED = "finished"
STATUS_CANCELED = "canceled"


# Team name normalization.
# The API names can change slightly, therefore slugs are generated dynamically.
def slugify(value: str) -> str:
    # Strip accents to their base letter first (e.g. "é" -> "e") so
    # they don't get treated as separators, producing clean slugs
    # like "fribourg-gotteron" instead of "fribourg-gott-ron".
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")

    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def load_games():
    response = requests.get(
        API_URL,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def get_game_datetime_utc(game):
    """Parses the game's date field and returns an aware UTC datetime."""

    date_value = game.get("date")

    if not date_value:
        return None

    if date_value.endswith("Z"):
        parsed = datetime.fromisoformat(
            date_value.replace("Z", "+00:00")
        )
    else:
        parsed = datetime.fromisoformat(
            date_value
        )

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def is_in_tracked_season(game):
    game_dt = get_game_datetime_utc(game)

    if game_dt is None:
        return False

    return game_dt >= SEASON_CUTOFF


def create_calendar():
    calendar = Calendar()

    calendar.add(
        "prodid",
        "-//National League Calendar Generator//"
    )

    calendar.add(
        "version",
        "2.0"
    )

    calendar.add(
        "X-WR-TIMEZONE",
        TIMEZONE
    )

    return calendar


def get_team_name(game, side):
    """side is 'home' or 'away'. Falls back to the short name, then 'Unknown'."""

    name = (
        game.get(f"{side}TeamName")
        or game.get(f"{side}TeamShortName")
        or "Unknown"
    )

    return html.unescape(name)


def get_score(game):
    """
    Returns a human readable score/status suffix, or None if the game
    hasn't been played yet (so no score should be shown at all).
    """

    status = game.get("status") or game.get("baseStatus")

    if status == STATUS_CANCELED:
        return "Annullata"

    if status != STATUS_FINISHED:
        return None

    home_score = game.get("homeTeamResult")
    away_score = game.get("awayTeamResult")

    if home_score is None or away_score is None:
        return None

    score = f"{home_score}-{away_score}"

    if game.get("isShootout"):
        score += " SO"
    elif game.get("isOvertime"):
        score += " OT"

    return score


def create_event(game):

    event = Event()

    game_id = game.get("gameId")

    home = get_team_name(game, "home")
    away = get_team_name(game, "away")

    score = get_score(game)
    is_exhibition = bool(game.get("isExhibition"))

    summary = f"{home} - {away}"

    if score:
        summary += f" ({score})"

    if is_exhibition:
        summary += f" | {EXHIBITION_TAG}"

    # The API has been observed reusing the same gameId for genuinely
    # different matches. Including the team short names in the UID
    # keeps two such colliding games from overwriting each other, while
    # still keeping the UID stable across reschedules of the same match
    # (date/venue changes don't affect it).
    home_slug = slugify(
        game.get("homeTeamShortName") or home
    )
    away_slug = slugify(
        game.get("awayTeamShortName") or away
    )

    event.add(
        "uid",
        f"{game_id}-{home_slug}-{away_slug}@nationalleague.ch"
    )

    event.add(
        "summary",
        summary
    )

    date_value = game.get("date")

    if not date_value:
        raise Exception(
            f"Missing date for game {game_id}"
        )

    if date_value.endswith("Z"):
        start = datetime.fromisoformat(
            date_value.replace("Z", "+00:00")
        )

    else:
        start = datetime.fromisoformat(
            date_value
        )

    local_tz = pytz.timezone(TIMEZONE)

    if start.tzinfo is None:
        # Naive datetime: assume it already represents local time
        # rather than letting astimezone() guess the system timezone.
        start = local_tz.localize(start)
    else:
        start = start.astimezone(local_tz)

    event.add(
        "dtstart",
        start
    )

    event.add(
        "dtend",
        start + timedelta(hours=2)
    )

    venue = game.get("arena") or ""

    event.add(
        "location",
        html.unescape(str(venue))
    )

    description = [
        "National League" if not is_exhibition else f"National League ({EXHIBITION_TAG})",
        "",
        f"Home: {home}",
        f"Away: {away}",
    ]

    if score:
        description.append(
            f"Score: {score}"
        )

    event.add(
        "description",
        "\n".join(description)
    )

    event.add(
        "dtstamp",
        datetime.now(timezone.utc)
    )

    return event


def load_existing_events(path):
    """
    Loads a previously saved .ics file and returns its VEVENT components
    keyed by UID, so new data can be merged on top of it instead of
    replacing it outright.
    """

    if not os.path.exists(path):
        return {}

    with open(path, "rb") as file:
        raw = file.read()

    try:
        existing_calendar = Calendar.from_ical(raw)
    except ValueError:
        # Corrupt or unreadable file: treat as if nothing existed
        # rather than crashing the whole run.
        return {}

    events = {}

    for component in existing_calendar.walk("VEVENT"):
        uid = str(component.get("uid"))
        events[uid] = component

    return events


def save_calendar(calendar, filename):

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    path = os.path.join(
        OUTPUT_DIR,
        filename
    )

    with open(
        path,
        "wb"
    ) as file:

        file.write(
            calendar.to_ical()
        )


def main():

    games = load_games()

    games = [
        game
        for game in games
        if is_in_tracked_season(game)
    ]

    # Teams that only ever show up in exhibition games (e.g. a foreign
    # club playing a single friendly) don't get their own .ics file.
    teams_with_regular_season = set()

    for game in games:
        if not game.get("isExhibition"):
            teams_with_regular_season.add(get_team_name(game, "home"))
            teams_with_regular_season.add(get_team_name(game, "away"))

    # events_by_calendar maps a calendar key ("all" or a team name) to a
    # dict of {uid: VEVENT}, seeded with whatever was already saved on
    # disk so old events are preserved even if the API stops returning
    # them in a later run.
    events_by_calendar = {}

    def get_calendar_events(key, filename):
        if key not in events_by_calendar:
            path = os.path.join(OUTPUT_DIR, filename)
            events_by_calendar[key] = load_existing_events(path)

        return events_by_calendar[key]

    # Make sure the "all" calendar's existing events are loaded too.
    get_calendar_events("all", "all.ics")

    for game in games:

        home = get_team_name(game, "home")
        away = get_team_name(game, "away")

        event = create_event(game)
        uid = str(event.get("uid"))

        events_by_calendar["all"][uid] = event

        for team in [home, away]:
            if team not in teams_with_regular_season:
                continue

            filename = f"{slugify(team)}.ics"
            team_events = get_calendar_events(team, filename)
            team_events[uid] = event

    for key, events in events_by_calendar.items():

        calendar = create_calendar()

        for event in sorted(
            events.values(),
            key=lambda e: e.get("dtstart").dt
        ):
            calendar.add_component(event)

        filename = (
            "all.ics"
            if key == "all"
            else f"{slugify(key)}.ics"
        )

        save_calendar(
            calendar,
            filename
        )


if __name__ == "__main__":
    main()
