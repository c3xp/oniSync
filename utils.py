import math


def format_duration(seconds: float) -> str:
    total = int(round(seconds))
    mins = total // 60
    secs = total % 60
    return f"{mins}:{secs:02d} ({seconds:.2f} s)"


def parse_positive_float(value: str, field_name: str) -> float:
    try:
        num = float(value.replace(",", "."))
    except ValueError as exc:
        raise ValueError(f"{field_name} non è un numero valido.") from exc

    if not math.isfinite(num) or num <= 0:
        raise ValueError(f"{field_name} deve essere maggiore di 0.")

    return num
