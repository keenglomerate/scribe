#!/usr/bin/env python3
import os
import sys
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from mcp.server.fastmcp import FastMCP

# Define Google Calendar API access scope
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Initialize FastMCP Server
mcp = FastMCP("scribe")

def get_calendar_service():
    """Load authorized credentials and build Google Calendar client client."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(script_dir, 'token.json')
    
    if not os.path.exists(token_path):
        raise FileNotFoundError("Authentication token (token.json) not found. Please run auth.py first to authorize Scribe.")
        
    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    except Exception as e:
        raise RuntimeError(f"Failed to load credentials from token.json: {e}")
        
    # Auto-refresh expired access tokens
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            # Save refreshed credentials
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        except Exception as e:
            raise RuntimeError(f"Failed to refresh Google API access token: {e}. Please re-run auth.py.")
            
    return build('calendar', 'v3', credentials=creds)

def check_for_conflicts(service, start_time, end_time, ignore_event_id=None):
    """Check if there are any events overlapping with the given start and end times."""
    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True
        ).execute()
        events = events_result.get('items', [])
        
        conflicts = []
        for event in events:
            if ignore_event_id and event.get('id') == ignore_event_id:
                continue
            
            event_start = event['start'].get('dateTime', event['start'].get('date'))
            event_end = event['end'].get('dateTime', event['end'].get('date'))
            
            # Simple boundary check to ensure actual overlap
            if event_start < end_time and event_end > start_time:
                conflicts.append(f"'{event.get('summary', 'Untitled')}' ({event_start} - {event_end})")
        return conflicts
    except Exception:
        return []

# --- MCP TOOLS ---

@mcp.tool()
def list_events(time_min: str = None, time_max: str = None, max_results: int = 10) -> str:
    """List calendar events for a given time range.
    
    Args:
        time_min: Start time in RFC3339 format (e.g. '2026-07-10T00:00:00Z'). Defaults to now.
        time_max: End time in RFC3339 format (e.g. '2026-07-17T23:59:59Z'). Defaults to 7 days from now.
        max_results: Max number of events to return.
    """
    try:
        service = get_calendar_service()
        
        if not time_min:
            time_min = datetime.utcnow().isoformat() + 'Z'
        if not time_max:
            time_max = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'
            
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        if not events:
            return "No upcoming events found in this time range."
            
        output = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            event_id = event['id']
            summary = event.get('summary', 'No Title')
            description = event.get('description', 'No description.')
            location = event.get('location', '')
            
            loc_str = f" | Location: {location}" if location else ""
            output.append(
                f"📅 Event: {summary}\n"
                f"   Time: {start} to {end}{loc_str}\n"
                f"   ID: {event_id}\n"
                f"   Details: {description}\n"
            )
            
        return "\n".join(output)
    except Exception as e:
        return f"❌ Error listing events: {e}"

@mcp.tool()
def create_event(summary: str, start_time: str, end_time: str, description: str = None, location: str = None) -> str:
    """Create a new calendar event.
    
    Args:
        summary: Title of the event.
        start_time: Start time in RFC3339 format (e.g. '2026-07-10T14:00:00+07:00' or '2026-07-10T07:00:00Z').
        end_time: End time in RFC3339 format (e.g. '2026-07-10T15:00:00+07:00' or '2026-07-10T08:00:00Z').
        description: Optional body details/notes for the event.
        location: Optional location address or videoconference link.
    """
    try:
        service = get_calendar_service()
        
        # Check for overlaps/conflicts
        conflicts = check_for_conflicts(service, start_time, end_time)
        conflict_warning = ""
        if conflicts:
            conflict_warning = "⚠️ Warning: This event conflicts with the following scheduled events:\n" + "\n".join(f"  - {c}" for c in conflicts) + "\n\n"
            
        event_body = {
            'summary': summary,
            'start': {'dateTime': start_time},
            'end': {'dateTime': end_time},
        }
        if description:
            event_body['description'] = description
        if location:
            event_body['location'] = location
            
        created_event = service.events().insert(calendarId='primary', body=event_body).execute()
        return (
            f"{conflict_warning}✅ Event created successfully!\n"
            f"Title: {created_event.get('summary')}\n"
            f"ID: {created_event.get('id')}\n"
            f"Link: {created_event.get('htmlLink')}"
        )
    except Exception as e:
        return f"❌ Error creating event: {e}"

@mcp.tool()
def reschedule_event(event_id: str, start_time: str, end_time: str) -> str:
    """Move / reschedule an existing calendar event.
    
    Args:
        event_id: The ID of the event to reschedule.
        start_time: The new start time in RFC3339 format.
        end_time: The new end time in RFC3339 format.
    """
    try:
        service = get_calendar_service()
        
        # Check for overlaps/conflicts (excluding the event we are rescheduling)
        conflicts = check_for_conflicts(service, start_time, end_time, ignore_event_id=event_id)
        conflict_warning = ""
        if conflicts:
            conflict_warning = "⚠️ Warning: The new time conflicts with the following scheduled events:\n" + "\n".join(f"  - {c}" for c in conflicts) + "\n\n"
            
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        event['start']['dateTime'] = start_time
        event['end']['dateTime'] = end_time
        
        # Avoid timezone key conflict
        event['start'].pop('date', None)
        event['end'].pop('date', None)
        
        updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
        return (
            f"{conflict_warning}✅ Event rescheduled successfully!\n"
            f"Title: {updated_event.get('summary')}\n"
            f"New Start: {start_time}\n"
            f"New End: {end_time}"
        )
    except Exception as e:
        return f"❌ Error rescheduling event: {e}"

@mcp.tool()
def delete_event(event_id: str) -> str:
    """Delete / cancel an existing calendar event.
    
    Args:
        event_id: The ID of the event to delete.
    """
    try:
        service = get_calendar_service()
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return f"✅ Event with ID '{event_id}' has been cancelled and deleted."
    except Exception as e:
        return f"❌ Error deleting event: {e}"

@mcp.tool()
def search_events(query: str, max_results: int = 10) -> str:
    """Search for events in the calendar matching a text query.
    
    Args:
        query: Free text term to filter events.
        max_results: Max number of search results to return.
    """
    try:
        service = get_calendar_service()
        events_result = service.events().list(
            calendarId='primary',
            q=query,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        if not events:
            return f"No events found matching: '{query}'"
            
        output = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            event_id = event['id']
            summary = event.get('summary', 'No Title')
            description = event.get('description', 'No description.')
            
            output.append(
                f"🔍 Match: {summary}\n"
                f"   Time: {start} to {end}\n"
                f"   ID: {event_id}\n"
                f"   Details: {description}\n"
            )
            
        return "\n".join(output)
    except Exception as e:
        return f"❌ Error searching events: {e}"

@mcp.tool()
def find_free_slots(date: str, start_hour: int = 8, end_hour: int = 20) -> str:
    """Find available free time slots on a specific date.
    
    Args:
        date: The date to check in YYYY-MM-DD format (e.g. '2026-07-10').
        start_hour: Hour of the day to start scanning (default 8 for 8:00 AM).
        end_hour: Hour of the day to stop scanning (default 20 for 8:00 PM).
    """
    try:
        service = get_calendar_service()
        
        # Parse time range in local time (Asia/Bangkok)
        time_min = f"{date}T{start_hour:02d}:00:00+07:00"
        time_max = f"{date}T{end_hour:02d}:00:00+07:00"
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        
        # Build busy intervals
        busy_intervals = []
        for event in events:
            start = event['start'].get('dateTime')
            end = event['end'].get('dateTime')
            if start and end:
                busy_intervals.append((start, end))
                
        # Find free slots
        import datetime as dt
        current_time = dt.datetime.fromisoformat(time_min)
        limit_time = dt.datetime.fromisoformat(time_max)
        
        free_slots = []
        for start, end in sorted(busy_intervals):
            start_dt = dt.datetime.fromisoformat(start)
            end_dt = dt.datetime.fromisoformat(end)
            
            if start_dt > current_time:
                free_slots.append(f"- {current_time.strftime('%H:%M')} to {start_dt.strftime('%H:%M')}")
            current_time = max(current_time, end_dt)
            
        if current_time < limit_time:
            free_slots.append(f"- {current_time.strftime('%H:%M')} to {limit_time.strftime('%H:%M')}")
            
        if not free_slots:
            return f"No free slots found between {start_hour:02d}:00 and {end_hour:02d}:00 on {date}."
            
        return f"⏰ Free slots on {date} ({start_hour:02d}:00 - {end_hour:02d}:00):\n" + "\n".join(free_slots)
    except Exception as e:
        return f"❌ Error finding free slots: {e}"

@mcp.tool()
def quick_add(text: str) -> str:
    """Quickly add an event using natural language description.
    
    Args:
        text: Natural language string describing the event (e.g. 'Dinner with Bob tomorrow at 6pm').
    """
    try:
        service = get_calendar_service()
        created_event = service.events().quickAdd(
            calendarId='primary',
            text=text
        ).execute()
        
        start = created_event['start'].get('dateTime', created_event['start'].get('date'))
        end = created_event['end'].get('dateTime', created_event['end'].get('date'))
        
        return (
            f"⚡ Event added successfully via Quick Add!\n"
            f"Title: {created_event.get('summary')}\n"
            f"Time: {start} to {end}\n"
            f"ID: {created_event.get('id')}\n"
            f"Link: {created_event.get('htmlLink')}"
        )
    except Exception as e:
        return f"❌ Error in Quick Add: {e}"

if __name__ == "__main__":
    # Runs the stdio MCP server loop
    mcp.run()
