"""
    `src/util/calculation.py`
"""

from datetime import datetime, timedelta


def average(data: list):
    """ Function: Returns average value of the list """
    return sum(data)/len(data)


def compare_date(date_string_a: str, date_string_b: str) -> int:
    date_a = datetime.strptime(date_string_a, '%Y-%m-%d')
    date_b = datetime.strptime(date_string_b, '%Y-%m-%d')

    return (date_a - date_b).days


def add_day_to_date(date_string: str, days: int=1) -> str:
    """ Function: Add days to date """
    date = datetime.strptime(date_string, '%Y-%m-%d')
    added_days = timedelta(days=days)

    return str(date + added_days).split()[0]
