"""Admin exports of students, parents and payments as a flat table (columns + rows).

The admin panel turns the table into an Excel file or a printable PDF in the browser, so Arabic
names keep their proper shaping. Exports follow the same search and filters as the lists, but
include every matching row (the on-screen lists are capped).
"""
from backend.errors import ApplicationError
from backend.modules.billing import admin_payments
from backend.modules.identity import admin_parents, admin_students


def _grades(values) -> str:
    return ", ".join(f"Grade {g}" for g in values or [])


def _terms(values) -> str:
    # "grade_5_term_1" -> "G5 T1"
    out = []
    for value in values or []:
        parts = str(value).split("_")
        out.append(f"G{parts[1]} T{parts[3]}" if len(parts) == 4 else str(value))
    return ", ".join(out)


def _date(value) -> str:
    return (value or "")[:10]


def _yes(value) -> str:
    return "Yes" if value else "No"


def _students(filters, actor, db):
    rows = admin_students.export_students(filters.get("q"), actor=actor, db=db)
    columns = ["Student", "Grade", "Grades with access", "Unlocked terms", "School", "Gender", "Age",
               "Has PIN", "Parent", "Parent email"]
    return "Students", columns, [[
        s["name"], s["default_grade"], _grades(s["entitled_grades"]), _terms(s["unlocked_terms"]),
        s["school_name"] or "", s["gender"] or "", s["age"] or "", _yes(s["has_pin"]),
        s["parent_name"] or "", s["parent_email"] or "",
    ] for s in rows]


def _parents(filters, actor, db):
    rows = admin_parents.export_parents(filters.get("q"), actor=actor, db=db, students=filters.get("students"))
    columns = ["Parent", "Email", "Phone", "Verified", "Weekly report emails", "Joined", "Students",
               "Student names (grade)", "Payments", "Paid payments", "Total paid (USD)", "Vouchers redeemed",
               "Last payment"]
    return "Parents", columns, [[
        p["full_name"] or "", p["email"], p["phone_number"] or "", _yes(p["is_verified"]),
        _yes(p["weekly_report_email"]), _date(p["created_at"]), p["students_count"],
        "; ".join(f"{c['name']} (G{c['default_grade']})" for c in p["students"]),
        p["payments_count"], p["paid_count"], p["total_paid_usd"], p["voucher_redemptions"],
        _date(p["last_payment_at"]),
    ] for p in rows]


def _payments(filters, actor, db):
    days = filters.get("days")
    data = admin_payments.list_payments(
        actor=actor, db=db, q=filters.get("q"), method=filters.get("method"), status=filters.get("status"),
        parent_id=filters.get("parent_id"), days=int(days) if days else None, limit=None)
    columns = ["Date", "Parent", "Parent email", "Student", "Grade", "Term", "Package", "Amount", "VAT",
               "Discount", "Currency", "Method", "Voucher code", "Promo code", "Receipt no.", "Tax invoice no.",
               "Status", "Refunded on"]
    return "Payments", columns, [[
        (p["created_at"] or "")[:16].replace("T", " "), p["parent_name"] or "", p["parent_email"] or "",
        p["child_name"] or "", p["grade"] or "", p["term"] or "", p["package_type"] or "", p["amount_usd"],
        p["vat_amount_usd"], p["discount_amount_usd"], p["currency"], p["payment_method"] or "",
        p["voucher_code"] or "", p["promo_code"] or "", p["receipt_number"] or "",
        p["tax_invoice_number"] or "", p["status"] or "", _date(p["refunded_at"]),
    ] for p in data["payments"]]


EXPORTS = {"students": _students, "parents": _parents, "payments": _payments}


def export_table(kind: str, filters: dict, *, actor, db) -> dict:
    build = EXPORTS.get(kind)
    if build is None:
        raise ApplicationError(404, "Unknown export.")
    title, columns, rows = build(filters, actor, db)
    return {"title": title, "columns": columns, "rows": rows}
