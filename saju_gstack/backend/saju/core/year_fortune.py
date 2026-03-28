# 해당 양력 연도의 연주(年柱)와 일간 대비 연간 십성 — 결정적 계산

# 일간 천간 인덱스와 연간 천간 인덱스로 십성 이름을 구한다
from .saju_data import CHEONGAN, JIJI
from .calculator import get_year_gan, get_year_ji
from .sipseong import ten_god_for_stems


def build_year_fortune(day_master_stem: str, target_year: int) -> dict:
    """
    target_year 양력의 연주(천간·지지)와,
    일간(일주 천간)이 그 해의 연간을 십성으로 볼 때의 이름을 반환한다.
    """
    # 일간 = 일주 천간 한 글자
    day_gan_idx = CHEONGAN.index(day_master_stem)
    # 해당 양력 연도의 연간·연지 (엔진 규칙과 동일)
    yg = get_year_gan(target_year)
    yj = get_year_ji(target_year)
    ten = ten_god_for_stems(day_gan_idx, yg)
    return {
        "target_year": target_year,
        "annual_pillar": {
            "stem": CHEONGAN[yg],
            "branch": JIJI[yj],
        },
        "year_stem_ten_god_vs_day_master": ten,
    }
