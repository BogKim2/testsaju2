# Backend Spec — Saju Calculation Engine

You are a Python backend engineer specialized in astrology systems.

Design the saju calculation engine.

## Requirements

### Input

- birth datetime
- lunar/solar flag
- gender

### Output (STRICT JSON)

```json
{
  "saju": {
    "year": {"stem": "", "branch": ""},
    "month": {"stem": "", "branch": ""},
    "day": {"stem": "", "branch": ""},
    "hour": {"stem": "", "branch": ""}
  },
  "elements": {
    "wood": 0,
    "fire": 0,
    "earth": 0,
    "metal": 0,
    "water": 0
  },
  "ten_gods": [],
  "day_master": "",
  "strength": ""
}
```

## Task

- Define calculation pipeline
- Suggest libraries (if any)
- Edge cases (timezone, lunar conversion)
- Ensure determinism

**NO LLM USAGE.**
