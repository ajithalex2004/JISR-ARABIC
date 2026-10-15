"""Obvious student PINs are refused when a PIN is set; nothing defaults to 1234 any more."""
import unittest

from backend.errors import ApplicationError
from backend.modules.identity.pins import checked_pin, is_weak_pin
from backend.schemas import AddChildRequest, ChildProfileSchema


class TestStudentPins(unittest.TestCase):
    def test_obvious_pins_are_weak(self):
        for pin in ("0000", "7777", "1234", "6789", "4321", "1212", "2580"):
            self.assertTrue(is_weak_pin(pin), pin)
        for pin in ("4826", "3917", "2468", "1357", "9054"):
            self.assertFalse(is_weak_pin(pin), pin)

    def test_checked_pin(self):
        self.assertIsNone(checked_pin(None))
        self.assertIsNone(checked_pin("  "))
        self.assertEqual(checked_pin(" 4826 "), "4826")
        for bad in ("123", "12a4", "12345", "1111"):
            with self.assertRaises(ApplicationError):
                checked_pin(bad)

    def test_no_default_pin(self):
        self.assertIsNone(AddChildRequest(name="Sam").access_pin)
        self.assertIsNone(ChildProfileSchema(id="c", name="Sam", gender="Boy", age=9, school_name="S", default_grade=3).access_pin)


if __name__ == "__main__":
    unittest.main()
