import datetime


def date_convert(date_: datetime.date) -> list[str, str]:
    return date_.strftime("%d %b|%A").split("|")
