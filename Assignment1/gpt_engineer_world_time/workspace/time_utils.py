import pytz
from datetime import datetime

def get_country_timezones(country):
    """Return a list of timezones for a given country."""
    return pytz.country_timezones.get(country.upper(), [])

def get_current_time(timezone):
    """Return the current time for a given timezone."""
    tz = pytz.timezone(timezone)
    return datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
