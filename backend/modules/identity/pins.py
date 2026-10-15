"""Rules for the 4-digit student quick-login PIN.

Anyone who knows a parent's email can try a student's PIN, so obvious ones (1234, 0000,
1212, ...) are refused when a PIN is set. PINs already in use keep working.
"""
from typing import Optional

from backend.errors import ApplicationError

_COMMON = {"2580", "0852", "1004", "1122", "6969", "2000", "1010"}


def is_weak_pin(pin: str) -> bool:
    digits = [int(d) for d in pin]
    steps = {b - a for a, b in zip(digits, digits[1:])}
    return (
        len(set(pin)) == 1                      # 0000, 7777
        or steps in ({1}, {-1})                 # 1234, 6789, 4321
        or (pin[:2] == pin[2:])                 # 1212, 4545
        or pin in _COMMON
    )


def checked_pin(pin: Optional[str]) -> Optional[str]:
    """The PIN to store, or None when none was given; raises 400 for a bad or obvious PIN."""
    pin = (pin or "").strip()
    if not pin:
        return None
    if len(pin) != 4 or not pin.isdigit():
        raise ApplicationError(400, "The student PIN must be exactly 4 digits.")
    if is_weak_pin(pin):
        raise ApplicationError(400, "Please choose a less obvious student PIN: avoid repeated or consecutive digits like 1111, 1234 or 1212.")
    return pin
