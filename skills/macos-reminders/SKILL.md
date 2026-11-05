---
name: macos-reminders
description: Creates reminders in the macOS Reminders app at a given date and time. Use when the user asks to be reminded of something, to schedule a reminder or follow-up check, or says "remind me".
---

# macOS Reminders

Create the reminder by running the script (it needs to run outside the sandbox):

```bash
scripts/remind.sh "YYYY-MM-DD HH:MM" "Title" ["Notes"] ["List name"]
```

- Resolve relative times ("tomorrow morning", "in 2 hours") against the current local date and time. "Morning" with no time means 09:00. Ask only if the time is genuinely unclear.
- Title: a short, actionable line, e.g. `Check if Pull Request pipeline passed`.
- Notes: whatever the user needs to act on it without this chat: where to look, and links to the relevant task file, ticket, or PR/MR.
- List: omit to use the default list, unless the user names one.

The script prints `<title> @ <date> in <list>`. Confirm the date and time from that output to the user. It fails on a past time, a malformed date, or an unknown list name.

On the first run, macOS may ask the user to allow the terminal to control Reminders. If the script fails with a permission error, ask the user to allow it under System Settings > Privacy & Security > Automation, then retry.
