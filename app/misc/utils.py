import datetime
import locale

SPANISH_DAY_INITIALS = {
    "lu.": "L",
    "ma.": "M",
    "mi.": "X",
    "ju.": "J",
    "vi.": "V",
    "sá.": "S",
    "do.": "D",
}


def date_convert(date_: datetime.date) -> list[str, str]:
    date_str = date_.strftime("%d %b|%a")
    if locale.getlocale(locale.LC_TIME)[0] == "es_ES":
        date_split = (lambda x: [x[0][:-1], SPANISH_DAY_INITIALS[x[1]]])(date_str.split('|'))
    else:
        date_split = date_str.split('|')
    return date_split
