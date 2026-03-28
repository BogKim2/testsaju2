# 사주 8자 계산 엔진 — 양력 생년월일시 -> 연월일시주

from datetime import date

from .saju_data import (
    CHEONGAN,
    CHEONGAN_HANJA,
    CHEONGAN_OHAENG,
    CHEONGAN_YANGEUM,
    JIJI,
    JIJI_HANJA,
    JIJI_OHAENG,
    JIJI_YANGEUM,
    JIJI_ANIMAL,
    OHAENG_HANJA,
    OHAENG_COLOR,
    MONTH_JIJI_SOLAR,
    JEOLGI_TABLE,
    get_siji_index,
)


def get_gan_index(year: int, month: int, day: int) -> int:
    base = date(1900, 1, 1)
    target = date(year, month, day)
    delta = (target - base).days
    return delta % 10


def get_ji_index(year: int, month: int, day: int) -> int:
    base = date(1900, 1, 1)
    target = date(year, month, day)
    delta = (target - base).days
    return delta % 12


def get_year_gan(year: int) -> int:
    return (year - 4) % 10


def get_year_ji(year: int) -> int:
    return (year - 4) % 12


def get_month_jiji(year: int, month: int, day: int) -> int:
    _, jeol_day = JEOLGI_TABLE[month - 1]
    if day < jeol_day:
        prev_month = month - 1 if month > 1 else 12
        return MONTH_JIJI_SOLAR[prev_month - 1]
    return MONTH_JIJI_SOLAR[month - 1]


def get_month_gan(year_gan: int, month_jiji: int) -> int:
    base_month_gan = [2, 4, 6, 8, 0, 2, 4, 6, 8, 0]
    month_order = (month_jiji - 2) % 12
    return (base_month_gan[year_gan] + month_order) % 10


def get_hour_gan(day_gan: int, hour: int) -> int:
    base_hour_gan = [0, 2, 4, 6, 8, 0, 2, 4, 6, 8]
    siji = get_siji_index(hour)
    return (base_hour_gan[day_gan] + siji) % 10


def make_pillar(gan_idx: int, ji_idx: int) -> dict:
    return {
        "gan": CHEONGAN[gan_idx],
        "ji": JIJI[ji_idx],
        "gan_hanja": CHEONGAN_HANJA[gan_idx],
        "ji_hanja": JIJI_HANJA[ji_idx],
        "gan_ohaeng": CHEONGAN_OHAENG[gan_idx],
        "ji_ohaeng": JIJI_OHAENG[ji_idx],
        "gan_yangeum": "양" if CHEONGAN_YANGEUM[gan_idx] else "음",
        "ji_yangeum": "양" if JIJI_YANGEUM[ji_idx] else "음",
    }


def calculate_saju(year: int, month: int, day: int, hour: int, gender: str) -> dict:
    year_gan = get_year_gan(year)
    year_ji = get_year_ji(year)
    month_ji = get_month_jiji(year, month, day)
    month_gan = get_month_gan(year_gan, month_ji)
    day_gan = get_gan_index(year, month, day)
    day_ji = get_ji_index(year, month, day)
    hour_ji = get_siji_index(hour)
    hour_gan = get_hour_gan(day_gan, hour)

    pillars = {
        "year": make_pillar(year_gan, year_ji),
        "month": make_pillar(month_gan, month_ji),
        "day": make_pillar(day_gan, day_ji),
        "hour": make_pillar(hour_gan, hour_ji),
    }

    ohaeng_count = {"목": 0, "화": 0, "토": 0, "금": 0, "수": 0}
    for pillar in pillars.values():
        ohaeng_count[pillar["gan_ohaeng"]] += 1
        ohaeng_count[pillar["ji_ohaeng"]] += 1

    yangeum_count = {"양": 0, "음": 0}
    for pillar in pillars.values():
        yangeum_count[pillar["gan_yangeum"]] += 1
        yangeum_count[pillar["ji_yangeum"]] += 1

    ilgan = CHEONGAN[day_gan]
    ilgan_ohaeng = CHEONGAN_OHAENG[day_gan]
    ilgan_yangeum = "양" if CHEONGAN_YANGEUM[day_gan] else "음"
    animal = JIJI_ANIMAL[year_ji]
    year_is_yang = CHEONGAN_YANGEUM[year_gan]

    return {
        "pillars": pillars,
        "ohaeng": {
            k: {"count": v, "hanja": OHAENG_HANJA[k], "color": OHAENG_COLOR[k]}
            for k, v in ohaeng_count.items()
        },
        "yangeum": yangeum_count,
        "ilgan": ilgan,
        "ilgan_ohaeng": ilgan_ohaeng,
        "ilgan_yangeum": ilgan_yangeum,
        "animal": animal,
        "year_is_yang": year_is_yang,
        "birth": {
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "gender": gender,
        },
    }
