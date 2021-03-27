from datetime import datetime
from dateutil import tz

# METHOD 1: Hardcode zones:
from_zone = tz.gettz('UTC')
to_zone = tz.gettz('Asia/Singapore')

# METHOD 2: Auto-detect zones:
from_zone = tz.tzutc()
to_zone = tz.tzlocal()

utc = datetime.utcnow()
# utc = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
print(f"utc: {utc}")
# Tell the datetime object that it's in UTC time zone since 
# datetime objects are 'naive' by default
utc = utc.replace(tzinfo=from_zone)
print(f"utc: {utc}")
# Convert time zone
central = utc.astimezone(to_zone)
print(f"central: {central}")