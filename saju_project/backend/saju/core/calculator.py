# 사주 8자 계산 엔진
# 양력 생년월일시 -> 연주/월주/일주/시주 계산

from datetime import date, datetime
from typing import Optional

from .saju_data import (
    CHEONGAN, CHEONGAN_HANJA, CHEONGAN_OHAENG, CHEONGAN_YANGEUM,
    JIJI, JIJI_HANJA, JIJI_OHAENG, JIJI_YANGEUM, JIJI_ANIMAL,
    OHAENG_HANJA, OHAENG_COLOR,
    MONTH_JIJI_SOLAR, JEOLGI_TABLE, get_siji_index
)


def get_gan_index(year: int, month: int, day: int) -> int:
    """기준일(1900-01-01=甲子=0)부터 경과 일수로 일간 인덱스 계산"""
    base = date(1900, 1, 1)
    target = date(year, month, day)
    delta = (target - base).days
    return delta % 10


def get_ji_index(year: int, month: int, day: int) -> int:
    """기준일(1900-01-01=甲子=0)부터 경과 일수로 일지 인덱스 계산"""
    base = date(1900, 1, 1)
    target = date(year, month, day)
    delta = (target - base).days
    return delta % 12


def get_year_gan(year: int) -> int:
    """연간 인덱스 (甲子년=1984 기준)"""
    return (year - 4) % 10


def get_year_ji(year: int) -> int:
    """연지 인덱스 (子년=1984 기준)"""
    return (year - 4) % 12


def get_month_jiji(year: int, month: int, day: int) -> int:
    """
    월지 인덱스 계산 (절기 기준)
    절기일 이전이면 이전 월로 처리
    """
    jeol_month, jeol_day = JEOLGI_TABLE[month - 1]
    if day < jeol_day:
        # 절기 이전이면 이전 달 월지
        prev_month = month - 1 if month > 1 else 12
        return MONTH_JIJI_SOLAR[prev_month - 1]
    return MONTH_JIJI_SOLAR[month - 1]


def get_month_gan(year_gan: int, month_jiji: int) -> int:
    """
    월간 인덱스 계산
    연간에 따른 월간 기준: 갑/기년→병인월, 을/경년→무인월 등
    """
    # 연간별 인월(寅月) 월간 시작 인덱스
    # 갑(0)/기(5): 丙寅(병인) = 2
    # 을(1)/경(6): 戊寅(무인) = 4
    # 병(2)/신(7): 庚寅(경인) = 6
    # 정(3)/임(8): 壬寅(임인) = 8
    # 무(4)/계(9): 甲寅(갑인) = 0
    base_month_gan = [2, 4, 6, 8, 0, 2, 4, 6, 8, 0]
    # 인월(월지 인덱스=2)이 기준
    # month_jiji 인덱스: 인=2, 묘=3, ... 축=1, 자=0
    # 인월부터 순서대로 월간이 증가
    month_order = (month_jiji - 2) % 12  # 인월=0, 묘월=1, ...
    return (base_month_gan[year_gan] + month_order) % 10


def get_hour_gan(day_gan: int, hour: int) -> int:
    """
    시간 인덱스 계산
    일간에 따른 자시(子時) 시간 기준
    """
    # 일간별 자시(子時) 시간 시작 인덱스
    # 갑(0)/기(5): 甲子(갑자) = 0
    # 을(1)/경(6): 丙子(병자) = 2
    # 병(2)/신(7): 戊子(무자) = 4
    # 정(3)/임(8): 庚子(경자) = 6
    # 무(4)/계(9): 壬子(임자) = 8
    base_hour_gan = [0, 2, 4, 6, 8, 0, 2, 4, 6, 8]
    siji = get_siji_index(hour)
    return (base_hour_gan[day_gan] + siji) % 10


def make_pillar(gan_idx: int, ji_idx: int) -> dict:
    """천간+지지를 딕셔너리로 구성"""
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
    """
    사주 8자 전체 계산
    
    Args:
        year: 양력 연도
        month: 양력 월
        day: 양력 일
        hour: 시간 (0~23)
        gender: 성별 ("남" 또는 "여")
    
    Returns:
        사주 8자 및 오행 분포 딕셔너리
    """
    # 연주 계산
    year_gan = get_year_gan(year)
    year_ji = get_year_ji(year)

    # 월주 계산
    month_ji = get_month_jiji(year, month, day)
    month_gan = get_month_gan(year_gan, month_ji)

    # 일주 계산
    day_gan = get_gan_index(year, month, day)
    day_ji = get_ji_index(year, month, day)

    # 시주 계산
    hour_ji = get_siji_index(hour)
    hour_gan = get_hour_gan(day_gan, hour)

    # 4주 구성
    pillars = {
        "year": make_pillar(year_gan, year_ji),
        "month": make_pillar(month_gan, month_ji),
        "day": make_pillar(day_gan, day_ji),
        "hour": make_pillar(hour_gan, hour_ji),
    }

    # 오행 집계 (8자 기준)
    ohaeng_count = {"목": 0, "화": 0, "토": 0, "금": 0, "수": 0}
    for pillar in pillars.values():
        ohaeng_count[pillar["gan_ohaeng"]] += 1
        ohaeng_count[pillar["ji_ohaeng"]] += 1

    # 음양 집계
    yangeum_count = {"양": 0, "음": 0}
    for pillar in pillars.values():
        yangeum_count[pillar["gan_yangeum"]] += 1
        yangeum_count[pillar["ji_yangeum"]] += 1

    # 일주가 핵심 (일간=나 자신)
    ilgan = CHEONGAN[day_gan]
    ilgan_ohaeng = CHEONGAN_OHAENG[day_gan]
    ilgan_yangeum = "양" if CHEONGAN_YANGEUM[day_gan] else "음"

    # 띠
    animal = JIJI_ANIMAL[year_ji]

    # 연간이 양간이면 양년, 음간이면 음년
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
