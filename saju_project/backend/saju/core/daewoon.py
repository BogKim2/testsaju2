# 대운(大運) 및 세운(歲運) 계산
# 음양년/성별 기준으로 순행/역행 결정 후 절기까지 일수로 대운 시작 나이 산출

from datetime import date
from .saju_data import (
    CHEONGAN, CHEONGAN_HANJA, CHEONGAN_OHAENG,
    JIJI, JIJI_HANJA, JIJI_OHAENG,
    JEOLGI_TABLE
)


def get_days_to_next_jeolgi(year: int, month: int, day: int, forward: bool) -> int:
    """
    순행(forward=True): 다음 절기까지의 일수
    역행(forward=False): 이전 절기까지의 일수
    """
    birth = date(year, month, day)

    if forward:
        # 다음 절기 찾기
        for m in range(month, month + 13):
            actual_month = ((m - 1) % 12) + 1
            actual_year = year + (m - 1) // 12
            jeol_day = JEOLGI_TABLE[actual_month - 1][1]
            jeol_date = date(actual_year, actual_month, jeol_day)
            if jeol_date > birth:
                return (jeol_date - birth).days
    else:
        # 이전 절기 찾기
        for m in range(month, month - 13, -1):
            actual_month = ((m - 1) % 12) + 1
            actual_year = year - (1 if m <= 0 else 0)
            if m <= 0:
                actual_month = ((m + 11) % 12) + 1
                actual_year = year - 1
            jeol_day = JEOLGI_TABLE[actual_month - 1][1]
            try:
                jeol_date = date(actual_year, actual_month, jeol_day)
            except ValueError:
                continue
            if jeol_date < birth:
                return (birth - jeol_date).days

    return 30  # 기본값


def calculate_daewoon(
    birth_year: int, birth_month: int, birth_day: int,
    gender: str, year_is_yang: bool,
    month_gan_idx: int, month_ji_idx: int
) -> list:
    """
    대운 8개 계산
    
    순행 조건: (양년 남성) or (음년 여성)
    역행 조건: (음년 남성) or (양년 여성)
    
    Returns:
        대운 리스트 (각 대운에 시작 나이, 간지, 오행 포함)
    """
    is_male = gender in ["남", "M", "male"]

    # 순행/역행 결정
    if year_is_yang:
        forward = is_male  # 양년: 남=순행, 여=역행
    else:
        forward = not is_male  # 음년: 남=역행, 여=순행

    # 절기까지 일수 → 대운 시작 나이
    days = get_days_to_next_jeolgi(birth_year, birth_month, birth_day, forward)
    start_age = round(days / 3)
    if start_age < 1:
        start_age = 1

    # 대운 8개 생성
    daewoon_list = []
    for i in range(8):
        age = start_age + i * 10
        # 순행/역행에 따라 월주에서 간지 증가/감소
        if forward:
            gan_idx = (month_gan_idx + i + 1) % 10
            ji_idx = (month_ji_idx + i + 1) % 12
        else:
            gan_idx = (month_gan_idx - i - 1) % 10
            ji_idx = (month_ji_idx - i - 1) % 12

        daewoon_list.append({
            "age": age,
            "gan": CHEONGAN[gan_idx],
            "ji": JIJI[ji_idx],
            "gan_hanja": CHEONGAN_HANJA[gan_idx],
            "ji_hanja": JIJI_HANJA[ji_idx],
            "gan_ohaeng": CHEONGAN_OHAENG[gan_idx],
            "ji_ohaeng": JIJI_OHAENG[ji_idx],
            "direction": "순행" if forward else "역행",
        })

    return daewoon_list


def calculate_seun(current_year: int, birth_year: int) -> list:
    """
    세운(歲運) 계산 - 현재부터 10년간
    
    Args:
        current_year: 현재 연도
        birth_year: 출생 연도
    
    Returns:
        세운 10개 리스트
    """
    from .saju_data import CHEONGAN_YANGEUM, JIJI_YANGEUM

    seun_list = []
    for i in range(10):
        year = current_year + i
        age = year - birth_year
        gan_idx = (year - 4) % 10
        ji_idx = (year - 4) % 12

        seun_list.append({
            "year": year,
            "age": age,
            "gan": CHEONGAN[gan_idx],
            "ji": JIJI[ji_idx],
            "gan_hanja": CHEONGAN_HANJA[gan_idx],
            "ji_hanja": JIJI_HANJA[ji_idx],
            "gan_ohaeng": CHEONGAN_OHAENG[gan_idx],
            "ji_ohaeng": JIJI_OHAENG[ji_idx],
        })

    return seun_list
