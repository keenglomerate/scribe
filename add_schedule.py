#!/usr/bin/env python3
import os
import sys
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from scribe_server import get_calendar_service

# Define university classes based on the screenshots from the KMITL registration portal.
# First occurrence dates are calculated starting from Monday, June 29th, 2026.
# End date is Saturday, November 7th, 2026 (UNTIL date in RRULE is Nov 8th).
classes = [
    {
        "summary": "SAFETY AND STANDARDIZATION IN RAI",
        "location": "E12-505 อาคาร 12 ชั้น",
        "description": "Subject Code: 01416306 (Group 1)\nInstructor: รศ. ดร. วรรณดี เพชรมนต์ล้ำค่า",
        "start": "2026-06-29T08:45:00",
        "end": "2026-06-29T12:00:00"
    },
    {
        "summary": "FUNDAMENTALS OF AR, VR AND MIXED REALITY",
        "location": "KMITL",
        "description": "Subject Code: 01416613 (Group 1)\nInstructors: ผศ. ดร. ภูมิ คงห้วยรอบ, อ. ประวิตร พงศ์รัตนเดชาชัย",
        "start": "2026-06-29T13:00:00",
        "end": "2026-06-29T16:15:00"
    },
    {
        "summary": "INDUSTRIAL AUTOMATION (Sec 1)",
        "location": "HM 603 HM",
        "description": "Subject Code: 01416518 (Group 1)\nInstructors: ผศ. ดร. ภูมิ คงห้วยรอบ, อ. ฐิติพงศ์ เทพสิทธิ์, อาจารย์ ชวภณ อำรงวัชระชาติ",
        "start": "2026-07-01T08:00:00",
        "end": "2026-07-01T10:00:00"
    },
    {
        "summary": "INDUSTRIAL AUTOMATION (Sec 101)",
        "location": "HM 603 HM",
        "description": "Subject Code: 01416518 (Group 101)\nInstructors: ผศ. ดร. ภูมิ คงห้วยรอบ, อ. ฐิติพงศ์ เทพสิทธิ์, อาจารย์ ชวภณ อำรงวัชระชาติ",
        "start": "2026-07-01T10:00:00",
        "end": "2026-07-01T12:00:00"
    },
    {
        "summary": "PSYCHOLOGY IN COMMUNICATION",
        "location": "HM-502 HM",
        "description": "Subject Code: 96642142 (Group 101)\nInstructors: อ. Gaius Gallaza, รศ. ดร. รวีภัทร ลาภเจริญสุข",
        "start": "2026-07-02T09:00:00",
        "end": "2026-07-02T12:00:00"
    },
    {
        "summary": "DISCRETE MATHEMATICS",
        "location": "HM-304 HM",
        "description": "Subject Code: 01006718 (Group 1)\nInstructor: ผศ. ดร. พุทธชาติ ขันดันธง",
        "start": "2026-07-03T08:45:00",
        "end": "2026-07-03T12:00:00"
    },
    {
        "summary": "MANUFACTURING PROCESS",
        "location": "HM-303 HM",
        "description": "Subject Code: 01416319 (Group 2)\nInstructors: ดร. พลชัย โชติปรายนกุล, รศ. ดร. สุวารี ชาญกิจมั่นคง",
        "start": "2026-07-03T13:00:00",
        "end": "2026-07-03T16:15:00"
    },
    {
        "summary": "MATHEMATICS OF DATA SCIENCE AND DATA ANALYTIC",
        "location": "HM-301 HM",
        "description": "Subject Code: 01416801 (Group 2)\nInstructors: รศ. ดร. วรรณดี เพชรมนต์ล้ำค่า, อาจารย์ รพีพรรณ พรหมอยู่",
        "start": "2026-07-04T08:45:00",
        "end": "2026-07-04T12:00:00"
    }
]

def main():
    print("🚀 Initializing Google Calendar Service...")
    try:
        service = get_calendar_service()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
        
    print("📅 Scheduling university timetable events...")
    
    # UNTIL parameter in RRULE format: YYYYMMDDTHHMMSSZ (UTC).
    # Since semester ends on Nov 7th, 2026, setting limit to Nov 8th.
    recurrence_rrule = "RRULE:FREQ=WEEKLY;UNTIL=20261108T000000Z"
    
    for cls in classes:
        event = {
            'summary': cls['summary'],
            'location': cls['location'],
            'description': cls['description'],
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
            print(f"✅ Added Recurring Event: {cls['summary']} ({cls['start'].split('T')[1][:5]} - {cls['end'].split('T')[1][:5]})")
        except Exception as e:
            print(f"❌ Failed to create event for {cls['summary']}: {e}")
            
    print("\n🎉 Timetable successfully loaded into your Google Calendar!")

if __name__ == '__main__':
    main()
