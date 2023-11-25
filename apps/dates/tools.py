# get all dates between a range of dates
import pandas

def get_dates_from_range(start_date, end_date):
    dates = pandas.date_range(start_date, end_date)
    return dates

def get_times_from_range(start_time, end_time, freq):
    times = pandas.date_range(f'2024-1-1 {start_time}', f'2024-1-1 {end_time}', freq=freq)
    ftimes = [t.strftime('%H:%M') for t in times]
    return ftimes