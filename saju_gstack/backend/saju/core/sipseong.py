# 십성: 일간 천간 기준 타 천간 십성 (결정적)

from .saju_data import CHEONGAN_OHAENG, CHEONGAN_YANGEUM

_OHAENG_IDX = {"목": 0, "화": 1, "토": 2, "금": 3, "수": 4}


def ten_god_for_stems(day_gan_idx: int, target_gan_idx: int) -> str:
    ed = _OHAENG_IDX[CHEONGAN_OHAENG[day_gan_idx]]
    et = _OHAENG_IDX[CHEONGAN_OHAENG[target_gan_idx]]
    diff = (et - ed) % 5
    same_y = CHEONGAN_YANGEUM[day_gan_idx] == CHEONGAN_YANGEUM[target_gan_idx]
    if diff == 0:
        return "비견" if same_y else "겁재"
    if diff == 1:
        return "식신" if same_y else "상관"
    if diff == 2:
        return "편재" if same_y else "정재"
    if diff == 3:
        return "편관" if same_y else "정관"
    return "편인" if same_y else "정인"


def ten_gods_for_pillars(year_gan: int, month_gan: int, day_gan: int, hour_gan: int) -> list:
    return [
        ten_god_for_stems(day_gan, year_gan),
        ten_god_for_stems(day_gan, month_gan),
        ten_god_for_stems(day_gan, day_gan),
        ten_god_for_stems(day_gan, hour_gan),
    ]
