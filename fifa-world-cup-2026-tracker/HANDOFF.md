# FIFA World Cup 2026 Tracker - Handoff Notes

## Project Summary

This folder contains a standalone website for tracking the FIFA World Cup 2026.

Main file:

- `index.html` - complete HTML, CSS, and JavaScript app in one file.

The app can be opened directly in a browser or served through any local static server.

Example:

```bash
python -m http.server 8765
```

Then open:

```text
http://127.0.0.1:8765/index.html
```

## Current Features

- Tracks all 104 FIFA World Cup 2026 matches.
- Shows all kickoff dates and times in Indian Standard Time.
- Includes the 12 groups, 48 teams, group-stage fixtures, and knockout-stage match slots.
- Lets users enter match scores.
- Lets users mark a match as `Scheduled`, `Live`, or `Finished`.
- Automatically calculates match winners after scores are entered.
- Calculates group standings from finished group-stage matches.
- Tracks best-player awards by match.
- Builds a best-player leaderboard.
- Includes filters for search, stage, status, and group.
- Saves user edits in browser `localStorage`.
- Responsive layout verified for mobile width.

## Recent Changes Made

The original single-page tracker was improved with:

- A more colorful visual design.
- Brighter background treatment and hero styling.
- Gradient primary button and active tab styles.
- More appealing match cards with accent borders and hover depth.
- IST kickoff chips on every match card.
- Real 104-match schedule data using UTC kickoff timestamps, formatted into IST in the browser.
- Updated source note with schedule references.
- Clean project handoff folder created for IDE continuation.

## Data Model

The match schedule is stored in `scheduleRows`.

Each row follows this shape:

```js
[stage, group, utcKickoff, home, away, venue]
```

Example:

```js
["Group", "A", "2026-06-11T19:00:00Z", "Mexico", "South Africa", "Mexico City"]
```

The app converts UTC kickoff time to IST using:

```js
new Intl.DateTimeFormat("en-IN", {
  timeZone: "Asia/Kolkata",
  weekday: "short",
  day: "2-digit",
  month: "short",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
  hour12: true
})
```

User edits are saved with this key:

```js
wc2026-tracker-v3
```

If the data model changes again, bump the storage key to avoid old saved browser data mixing with the new schedule.

## Important Notes

- This is currently a static frontend only. There is no backend database.
- Scores, status changes, and best-player names are stored per browser using `localStorage`.
- Knockout-stage team names are placeholders such as `Round of 32 Team 1`.
- If you want the tracker to support multiple users or devices, add a backend or connect it to a database.
- If you want live official scores, integrate a sports data API later.

## Verification Already Done

- Confirmed the page renders 104 match cards.
- Confirmed Match 1 displays:

```text
Fri, 12 Jun, 2026, 12:30 am IST
```

- Confirmed the final displays:

```text
Mon, 20 Jul, 2026, 12:30 am IST
```

- Confirmed there was no horizontal overflow at a mobile viewport around 390px wide.

## Source References

Schedule and tournament details were checked on 6 June 2026.

- FIFA groups and rules: https://www.fifa.com/en/articles/groups-how-teams-qualify-tie-breakers
- FIFA kickoff-time release: https://vod.fifa.com/organisation/media-releases/updated-world-cup-2026-match-schedule-venues-kick-off-times-104-matches
- IST schedule PDF: https://www.kickoffclock.com/downloads/world-cup-2026-schedule-ist.pdf

## Suggested Next Steps

1. Move this folder into the desired Git repository.
2. Rename `index.html` or wrap it in a framework if needed.
3. Add a backend if cross-device persistence is needed.
4. Replace knockout placeholders after group winners are known.
5. Add import/export for saved scores if manual tracking across browsers matters.
6. Add tests for standings and winner calculation if the project grows.

