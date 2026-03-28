"""전압강하 계산 단위 테스트 (CONSTITUTION T-01 — 함수와 테스트 함께)."""

from harness_eng.tools.calculators import (
    MAX_VOLTAGE_DROP_V,
    calc_voltage_drop,
)


def test_voltage_drop_within_limit_returns_pass_status() -> None:
    """전압 강하가 기준(0.36V) 이하이면 is_acceptable True."""
    result = calc_voltage_drop(
        current_a=2.0,
        length_m_one_way=1.0,
        cross_section_mm2=2.5,
    )
    assert result["is_acceptable"] is True
    assert float(result["voltage_drop"]) <= MAX_VOLTAGE_DROP_V


def test_voltage_drop_exceeds_limit_returns_fail() -> None:
    """전류·길이가 크면 허용 초과."""
    result = calc_voltage_drop(
        current_a=50.0,
        length_m_one_way=10.0,
        cross_section_mm2=0.5,
    )
    assert result["is_acceptable"] is False


def test_invalid_cross_section_returns_not_acceptable() -> None:
    """단면적 0 이하."""
    result = calc_voltage_drop(1.0, 1.0, 0.0)
    assert result["is_acceptable"] is False
