import datetime


def date_convert(date_: datetime.date) -> str:
    return date_.strftime("%d %b | %a")


if __name__ == '__main__':
    print(date_convert(datetime.date(2024, 7, 13)))