# 엔진 결과 -> API strict JSON (stem/branch, elements 영문 키)

from typing import Any

from .saju_data import CHEONGAN
from .calculator import calculate_saju
from .sipseong import ten_gods_for_pillars


def _pillar_stem_branch(pillar: dict) -> dict[str, str]:
    return {"stem": pillar["gan"], "branch": pillar["ji"]}


def _elements_en(ohaeng_count: dict[str, int]) -> dict[str, int]:
    return {
        "wood": ohaeng_count["목"],
        "fire": ohaeng_count["화"],
        "earth": ohaeng_count["토"],
        "metal": ohaeng_count["금"],
        "water": ohaeng_count["수"],
    }


def _simple_strength(ten_gods: list[str]) -> str:
    bi_in = sum(1 for x in ten_gods if x in ("비견", "겁재", "편인", "정인"))
    other = len(ten_gods) - bi_in
    if bi_in > other:
        return "신강(경향)"
    if bi_in < other:
        return "신약(경향)"
    return "중화(경향)"


def compute_saju_strict(
    year: int,
    month: int,
    day: int,
    hour: int,
    gender: str,
) -> dict[str, Any]:
    raw = calculate_saju(year=year, month=month, day=day, hour=hour, gender=gender)
    pillars = raw["pillars"]
    year_gan = CHEONGAN.index(pillars["year"]["gan"])
    month_gan = CHEONGAN.index(pillars["month"]["gan"])
    day_gan = CHEONGAN.index(pillars["day"]["gan"])
    hour_gan = CHEONGAN.index(pillars["hour"]["gan"])

    ohaeng_count = {k: v["count"] for k, v in raw["ohaeng"].items()}
    ten_gods = ten_gods_for_pillars(year_gan, month_gan, day_gan, hour_gan)

    return {
        "saju": {
            "year": _pillar_stem_branch(pillars["year"]),
            "month": _pillar_stem_branch(pillars["month"]),
            "day": _pillar_stem_branch(pillars["day"]),
            "hour": _pillar_stem_branch(pillars["hour"]),
        },
        "elements": _elements_en(ohaeng_count),
        "ten_gods": ten_gods,
        "day_master": raw["ilgan"],
        "strength": _simple_strength(ten_gods),
        "_legacy": raw,
    }
