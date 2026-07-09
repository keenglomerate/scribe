#!/usr/bin/env python3
import os
import sys
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from scribe_server import get_calendar_service

# Define university classes based on the screenshots from the KMITL registration portal.
# First occurrence dates are calculated starting from Monday, June 29th, 2026.
# End date is Saturday, November 7th, 2026 (UNTIL date in RRULE is Nov 8th).
# Google Calendar Color ID mapping:
# '1': Lavender (Light Blue/Purple) | '3': Grape (Purple) | '5': Banana (Yellow)
# '6': Tangerine (Orange) | '9': Blueberry (Dark Blue) | '10': Basil (Green) | '11': Tomato (Red)
classes = [
    {
        "summary": "SAFETY AND STANDARDIZATION IN RAI",
        "location": "E12-505 อาคาร 12 ชั้น",
        "description": "Subject Code: 01416306 (Group 1)\nInstructor: รศ. ดร. วรรณดี เพชรมนต์ล้ำค่า",
        "start": "2026-06-29T08:45:00",
        "end": "2026-06-29T12:00:00",
        "colorId": "6" # Tangerine (Orange)
    },
    {
        "summary": "FUNDAMENTALS OF AR, VR AND MIXED REALITY",
        "location": "KMITL",
        "description": "Subject Code: 01416613 (Group 1)\nInstructors: ผศ. ดร. ภูมิ คงห้วยรอบ, อ. ประวิตร พงศ์รัตนเดชาชัย",
        "start": "2026-06-29T13:00:00",
        "end": "2026-06-29T16:15:00",
        "colorId": "3" # Grape (Purple)
    },
    {
        "summary": "INDUSTRIAL AUTOMATION (Sec 1)",
        "location": "HM 603 HM",
        "description": "Subject Code: 01416518 (Group 1)\nInstructors: ผศ. ดร. ภูมิ คงห้วยรอบ, อ. ฐิติพงศ์ เทพสิทธิ์, อาจารย์ ชวภณ อำรงวัชระชาติ",
        "start": "2026-07-01T08:00:00",
        "end": "2026-07-01T10:00:00",
        "colorId": "10" # Basil (Green)
    },
    {
        "summary": "INDUSTRIAL AUTOMATION (Sec 101)",
        "location": "HM 603 HM",
        "description": "Subject Code: 01416518 (Group 101)\nInstructors: ผศ. ดร. ภูมิ คงห้วยรอบ, อ. ฐิติพงศ์ เทพสิทธิ์, อาจารย์ ชวภณ อำรงวัชระชาติ",
        "start": "2026-07-01T10:00:00",
        "end": "2026-07-01T12:00:00",
        "colorId": "10" # Basil (Green)
    },
    {
        "summary": "PSYCHOLOGY IN COMMUNICATION",
        "location": "HM-502 HM",
        "description": "Subject Code: 96642142 (Group 101)\nInstructors: อ. Gaius Gallaza, รศ. ดร. รวีภัทร ลาภเจริญสุข",
        "start": "2026-07-02T09:00:00",
        "end": "2026-07-02T12:00:00",
        "colorId": "5" # Banana (Yellow)
    },
    {
        "summary": "DISCRETE MATHEMATICS",
        "location": "HM-304 HM",
        "description": "Subject Code: 01006718 (Group 1)\nInstructor: ผศ. ดร. พุทธชาติ ขันดันธง",
        "start": "2026-07-03T08:45:00",
        "end": "2026-07-03T12:00:00",
        "colorId": "9" # Blueberry (Dark Blue)
    },
    {
        "summary": "MANUFACTURING PROCESS",
        "location": "HM-303 HM",
        "description": "Subject Code: 01416319 (Group 2)\nInstructors: ดร. พลชัย โชติปรายนกุล, รศ. ดร. สุวารี ชาญกิจมั่นคง",
        "start": "2026-07-03T13:00:00",
        "end": "2026-07-03T16:15:00",
        "colorId": "11" # Tomato (Red)
    },
    {
        "summary": "MATHEMATICS OF DATA SCIENCE AND DATA ANALYTIC",
        "location": "HM-301 HM",
        "description": "Subject Code: 01416801 (Group 2)\nInstructors: รศ. ดร. วรรณดี เพชรมนต์ล้ำค่า, อาจารย์ รพีพรรณ พรหมอยู่",
        "start": "2026-07-04T08:45:00",
        "end": "2026-07-04T12:00:00",
        "colorId": "1" # Lavender (Light Blue/Purple)
    }
]

def main():
    print("🚀 Initializing Google Calendar Service...")
    try:
        service = get_calendar_service()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
        
    print("🧹 Cleaning up previously scheduled university events to avoid duplicates...")
    try:
        # Fetch events around the first week of school to locate our series
        events_result = service.events().list(
            calendarId='primary',
            timeMin='2026-06-29T00:00:00Z',
            timeMax='2026-07-05T00:00:00Z',
            singleEvents=True
        ).execute()
        existing_events = events_result.get('items', [])
        summaries_to_clean = {cls['summary'] for cls in classes}
        
        deleted_series = set()
        for event in existing_events:
            summary = event.get('summary')
            if summary in summaries_to_clean:
                recurring_id = event.get('recurringEventId')
                if recurring_id and recurring_id not in deleted_series:
                    try:
                        service.events().delete(calendarId='primary', eventId=recurring_id).execute()
                        print(f"🗑️ Deleted existing recurring series: {summary}")
                        deleted_series.add(recurring_id)
                    except Exception as delete_error:
                        print(f"⚠️ Could not delete series {summary}: {delete_error}")
                elif not recurring_id:
                    try:
                        service.events().delete(calendarId='primary', eventId=event['id']).execute()
                        print(f"🗑️ Deleted existing single event: {summary}")
                    except Exception as delete_error:
                        print(f"⚠️ Could not delete event {summary}: {delete_error}")
    except Exception as e:
        print(f"⚠️ Warning during cleanup: {e}")

    print("📅 Scheduling color-coded university timetable events...")
    
    # UNTIL parameter in RRULE format: YYYYMMDDTHHMMSSZ (UTC).
    # Since semester ends on Nov 7th, 2026, setting limit to Nov 8th.
    recurrence_rrule = "RRULE:FREQ=WEEKLY;UNTIL=20261108T000000Z"
    
    for cls in classes:
        event = {
            'summary': cls['summary'],
            'location': cls['location'],
            'description': cls['description'],
            'colorId': cls['colorId'], # Apply color code
            'start': {
                'dateTime': cls['start'],
                'timeZone': 'Asia/Bangkok',
            },
            'end': {
                'dateTime': cls['end'],
                'timeZone': 'Asia/Bangkok',
            },
            'recurrence': [
                recurrence_rrule
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 15},
                ],
            },
        }
        
        try:
            created_event = service.events().insert(calendarId='primary', body=event).execute()
            print(f"✅ Added Colored Event: {cls['summary']} (Color ID: {cls['colorId']})")
        except Exception as e:
            print(f"❌ Failed to create event for {cls['summary']}: {e}")
            
    print("\n🎉 Color-coded timetable successfully loaded into your Google Calendar!")

if __name__ == '__main__':
    main()
