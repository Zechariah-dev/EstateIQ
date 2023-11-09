import json
from datetime import datetime, timedelta
from django.utils import timezone
import calendar


def create_json_of_months_for_twelve():
    # Get today's date and time in the local timezone
    now = timezone.now()
    # Calculate the start and end dates for the last 12 months
    if now.month <= 12:
        start_date = timezone.datetime(now.year - 1, now.month + 1, 1, tzinfo=timezone.utc)
    else:
        start_date = timezone.datetime(now.year, now.month - 11, 1, tzinfo=timezone.utc)

    end_date = now.replace(day=1) - timedelta(days=1)

    # Create a list of dictionaries with the start and end dates for each month
    month_data = []
    for i in range(12):
        new_month = start_date.month + i
        new_year = start_date.year
        if new_month > 12:
            new_month -= 12
            new_year += 1
        start_of_month = timezone.datetime(new_year, new_month, 1, tzinfo=timezone.utc)
        _, days_in_month = calendar.monthrange(new_year, new_month)
        end_of_month = timezone.datetime(new_year, new_month, days_in_month, 23, 59, 59, 999999, tzinfo=timezone.utc)
        month_data.append({
            'month': start_of_month.strftime('%B'),
            'start_date': start_of_month.isoformat(),
            'end_date': end_of_month.isoformat()
        })

    # Convert the list of dictionaries to JSON and print it
    json_data = json.dumps(month_data, indent=4)
    return json_data
