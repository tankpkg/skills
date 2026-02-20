# Google Calendar

Create, query, update, and manage Google Calendar events, schedules, and availability.

## Overview

This skill enables AI agents to manage Google Calendar — creating and modifying events, checking free/busy availability, managing multiple calendars, and handling recurring events. Ideal for scheduling automation, meeting coordination, and time management workflows.

## Capabilities

### Event Management
- Create events with title, description, location, start/end times
- Update existing events (time, attendees, description)
- Delete and cancel events with optional notification to attendees
- Move events between calendars
- Set event colors and visibility (public, private, default)

### Scheduling
- Query free/busy information across multiple calendars
- Find available time slots for a group of attendees
- Create events with conferencing (Google Meet auto-generation)
- Set reminders (email, popup) with configurable lead times
- Handle all-day events and multi-day spans

### Recurring Events
- Create recurring events with RRULE patterns (daily, weekly, monthly, yearly)
- Modify single instances or entire series
- Handle exceptions to recurring patterns
- Query instances of a recurring event within a date range

### Calendar Management
- List all calendars for the authenticated user
- Create and delete secondary calendars
- Subscribe to other users' calendars
- Set calendar-level default reminders and notification preferences
- Manage calendar access control lists (ACLs)

### Attendees & RSVPs
- Add and remove attendees from events
- Set optional vs. required attendance
- Read attendee response status (accepted, declined, tentative)
- Send update notifications to attendees on changes

## Authentication

Requires Google OAuth 2.0:

- `https://www.googleapis.com/auth/calendar` — Full calendar access
- `https://www.googleapis.com/auth/calendar.events` — Event-only access
- `https://www.googleapis.com/auth/calendar.readonly` — Read-only access

## Example Usage

```json
{
  "action": "createEvent",
  "calendarId": "primary",
  "summary": "Sprint Planning",
  "start": "2026-02-17T10:00:00-08:00",
  "end": "2026-02-17T11:00:00-08:00",
  "attendees": ["alice@example.com", "bob@example.com"],
  "conferenceData": true,
  "reminders": [{"method": "popup", "minutes": 10}]
}
```

```json
{
  "action": "findAvailability",
  "attendees": ["alice@example.com", "bob@example.com"],
  "timeMin": "2026-02-17T08:00:00-08:00",
  "timeMax": "2026-02-17T18:00:00-08:00",
  "duration": 30
}
```

## Permissions

| Permission | Scope | Reason |
|-----------|-------|--------|
| Network | `*.googleapis.com` | Calendar API calls |
| Network | `accounts.google.com` | OAuth authentication |
| Filesystem | Read `./**` | Read ICS files for import |
| Subprocess | None | Not required |

## Best Practices

1. **Use RFC 3339 timestamps**: Always include timezone offset or use UTC
2. **Batch requests**: Combine multiple operations when creating/updating several events
3. **Incremental sync**: Use `syncToken` from list responses to efficiently poll for changes
4. **Time zone awareness**: Set `timeZone` on events explicitly — don't rely on calendar defaults
5. **Respect quotas**: Calendar API has per-user rate limits — implement exponential backoff
