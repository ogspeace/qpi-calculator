"""Simple QPI (Quality Point Index) calculator built with Flask."""

from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from zoneinfo import ZoneInfo

from flask import Flask, render_template, request

app = Flask(__name__)

# Letter grade -> quality points, per the AdDU Student Handbook (2025), Sec. 15.
# None means the grade is not counted in the QPI.
GRADE_POINTS = {
    "A": Decimal("4.0"),
    "B+": Decimal("3.5"),
    "B": Decimal("3.0"),
    "C+": Decimal("2.5"),
    "C": Decimal("2.0"),
    "D": Decimal("1.0"),
    "F": Decimal("0.0"),
    "FD": Decimal("0.0"),  # Failure Debarred
    "WP": None,  # Withdrawn with Permission
}

MAX_UNITS = Decimal("10")

PH_TIME = ZoneInfo("Asia/Manila")
COPYRIGHT_START = 2026


@app.context_processor
def page_globals():
    """Navbar clock timestamp and footer years, both in Philippine time."""
    now = datetime.now(PH_TIME)
    years = str(COPYRIGHT_START)
    if now.year > COPYRIGHT_START:
        years += f" - {now.year}"
    return {"clock_now": now, "copyright_years": years}


def calculate_qpi(subjects):
    """Return (total_units, total_quality_points, qpi) for a list of
    {"units": Decimal, "grade": str} dicts.

    QPI = sum(quality points * units) / total units, rounded off to four
    decimal places (Handbook Sec. 15.2-15.3). Grades worth None are skipped."""
    total_units = Decimal("0")
    total_points = Decimal("0")
    for s in subjects:
        points = GRADE_POINTS[s["grade"]]
        if points is None:          # WP: not counted in QPI
            continue
        total_units += s["units"]
        total_points += s["units"] * points
    if total_units == 0:
        return total_units, total_points, None
    qpi = (total_points / total_units).quantize(Decimal("0.0001"), ROUND_HALF_UP)
    return total_units, total_points, qpi


def parse_subjects(form):
    """Read the subject rows from the submitted form.

    Returns (rows, errors). Each row keeps the raw values so the form can be
    re-displayed exactly as the student entered it."""
    names = form.getlist("subject")
    units = form.getlist("units")
    grades = form.getlist("grade")

    rows, errors = [], []
    for i, (name, unit, grade) in enumerate(zip(names, units, grades), start=1):
        name, unit, grade = name.strip(), unit.strip(), grade.strip()
        if not (name or unit or grade):
            continue  # skip completely empty rows

        row = {"subject": name, "units_raw": unit, "grade": grade}
        label = name or f"Row {i}"

        try:
            row["units"] = Decimal(unit)
            if not row["units"].is_finite() or not 0 < row["units"] <= MAX_UNITS:
                raise InvalidOperation
        except InvalidOperation:
            errors.append(f"{label}: units must be a number greater than 0 and at most {MAX_UNITS}.")

        if grade not in GRADE_POINTS:
            errors.append(f"{label}: please choose a valid grade.")

        rows.append(row)

    if not rows and not errors:
        errors.append("Add at least one subject before calculating.")
    return rows, errors


@app.route("/", methods=["GET", "POST"])
def index():
    rows, errors, result = [], [], None

    if request.method == "POST":
        rows, errors = parse_subjects(request.form)
        if not errors:
            total_units, total_points, qpi = calculate_qpi(rows)
        if not errors and qpi is None:
            errors.append("None of the subjects count toward the QPI (all are WP).")
        elif not errors:
            result = {
                "total_units": total_units.normalize(),
                "total_points": total_points.quantize(Decimal("0.01")),
                "qpi": qpi,
            }

    return render_template(
        "index.html",
        rows=rows,
        errors=errors,
        result=result,
        grades=GRADE_POINTS,
    )


if __name__ == "__main__":
    app.run(debug=True)
