"""Electrical calculators (TOOLS.md — VoltageCalc)."""

from typing import Any

# 전압강하 허용: 12V × 3% = 0.36V (CONSTITUTION Rule C-05)
SUPPLY_VOLTAGE_V = 12.0
MAX_VOLTAGE_DROP_RATIO = 0.03
MAX_VOLTAGE_DROP_V = SUPPLY_VOLTAGE_V * MAX_VOLTAGE_DROP_RATIO
COPPER_RESISTIVITY_OHM_MM2_M = 0.01724


def calc_voltage_drop(
    current_a: float,
    length_m_one_way: float,
    cross_section_mm2: float,
    wire_material: str = "copper",
) -> dict[str, Any]:
    """와이어 왕복 길이로 전압강하 계산."""
    if cross_section_mm2 <= 0:
        return {
            "voltage_drop": 0.0,
            "resistance": 0.0,
            "is_acceptable": False,
            "warning": "invalid cross_section",
        }
    length_round_trip_m = length_m_one_way * 2.0
    # 현재는 구리만 지원 (추후 알루미늄 등 확장)
    rho = COPPER_RESISTIVITY_OHM_MM2_M
    _ = wire_material
    resistance = rho * length_round_trip_m / cross_section_mm2
    voltage_drop = current_a * resistance
    ok = voltage_drop <= MAX_VOLTAGE_DROP_V
    return {
        "voltage_drop": round(voltage_drop, 4),
        "resistance": round(resistance, 6),
        "is_acceptable": ok,
        "warning": ""
        if ok
        else f"voltage drop {voltage_drop:.3f}V exceeds limit {MAX_VOLTAGE_DROP_V}V",
    }
