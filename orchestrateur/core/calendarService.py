import requests
from ics import Calendar

class CalendarService:
    def __init__(self, googleCalendarUrl):
        self.calendar_url = googleCalendarUrl
        self.calendar = None

    def updateCalendar(self):
        try:
            return Calendar(requests.get(self.calendar_url).text)
        except Exception:
            return self.calendar

    def getCurrentEvent(self):
        self.calendar = self.updateCalendar()
        if self.calendar is not None:
            events = self.calendar.timeline.now()
            tags = [e.name.lower() for e in events]
            if 'open' in tags:
                print("CATCHED 'OPEN' STATE ON GOOGLE AGENDA")
                return "OPEN"
            print("NO 'OPEN' STATE ON GOOGLE AGENDA SENDING CLOSE SIGNAL")
            return "CLOSE"

if __name__ == "__main__":
    c = CalendarService("https://calendar.google.com/calendar/ical/5mvk2qo4dk7kp1vnum277hfar8%40group.calendar.google.com/public/basic.ics")

    c.getCurrentEvent()