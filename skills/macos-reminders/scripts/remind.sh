#!/usr/bin/env bash
# Create a reminder in the macOS Reminders app.
# Usage: remind.sh "YYYY-MM-DD HH:MM" "Title" ["Notes"] ["List name"]
set -euo pipefail

if [[ $# -lt 2 || ! $1 =~ ^([0-9]{4})-([0-9]{2})-([0-9]{2})\ ([0-9]{2}):([0-9]{2})$ ]]; then
  echo 'usage: remind.sh "YYYY-MM-DD HH:MM" "Title" ["Notes"] ["List name"]' >&2
  exit 2
fi

osascript - "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}" "${BASH_REMATCH[3]}" \
  "${BASH_REMATCH[4]}" "${BASH_REMATCH[5]}" "$2" "${3:-}" "${4:-}" <<'EOF'
on run argv
  -- Build the date from numbers: date strings are parsed with the system locale.
  set d to current date
  set day of d to 1
  set year of d to (item 1 of argv) as integer
  set month of d to (item 2 of argv) as integer
  set day of d to (item 3 of argv) as integer
  set time of d to ((item 4 of argv) as integer) * hours + ((item 5 of argv) as integer) * minutes
  if d < (current date) then error "Reminder time is in the past: " & (d as string)

  tell application "Reminders"
    set props to {name:(item 6 of argv), remind me date:d}
    if (item 7 of argv) is not "" then set props to props & {body:(item 7 of argv)}
    if (item 8 of argv) is "" then
      set r to make new reminder with properties props
    else
      set r to make new reminder at end of reminders of list (item 8 of argv) with properties props
    end if
    return (name of r) & " @ " & ((remind me date of r) as string) & " in " & (name of container of r)
  end tell
end run
EOF
