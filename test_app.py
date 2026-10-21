from datetime import datetime
from decimal import Decimal

import app as app_module
from app import app, calculate_qpi


def post(data):
    app.config["TESTING"] = True
    with app.test_client() as client:
        return client.post("/", data=data)


def test_calculate_qpi():
    subjects = [
        {"units": Decimal("3"), "grade": "A"},
        {"units": Decimal("3"), "grade": "B+"},
        {"units": Decimal("2"), "grade": "C"},
    ]
    units, points, qpi = calculate_qpi(subjects)
    assert units == 8
    assert points == Decimal("26.5")
    assert qpi == Decimal("3.3125")


def test_index_get():
    with app.test_client() as client:
        response = client.get("/")
    assert response.status_code == 200
    assert b"QPI Calculator" in response.data


def test_post_calculates_qpi():
    response = post({
        "subject": ["Math", "English", ""],
        "units": ["3", "3", ""],
        "grade": ["A", "B", ""],
    })
    assert response.status_code == 200
    assert b"3.5000" in response.data


def test_post_invalid_input():
    response = post({"subject": ["Math"], "units": ["abc"], "grade": ["Z"]})
    assert b"units must be a number" in response.data
    assert b"please choose a valid grade" in response.data


def test_post_no_subjects():
    response = post({"subject": [""], "units": [""], "grade": [""]})
    assert b"Add at least one subject" in response.data


def test_qpi_rounds_to_four_decimals():
    subjects = [
        {"units": Decimal("3"), "grade": "A"},
        {"units": Decimal("3"), "grade": "B"},
        {"units": Decimal("3"), "grade": "B"},
    ]
    assert calculate_qpi(subjects)[2] == Decimal("3.3333")


def test_fd_counts_as_zero_and_wp_is_excluded():
    subjects = [
        {"units": Decimal("3"), "grade": "A"},
        {"units": Decimal("3"), "grade": "FD"},
        {"units": Decimal("3"), "grade": "WP"},
    ]
    units, points, qpi = calculate_qpi(subjects)
    assert units == 6
    assert qpi == Decimal("2.0000")


def test_post_only_wp():
    response = post({"subject": ["Math"], "units": ["3"], "grade": ["WP"]})
    assert b"None of the subjects count toward the QPI" in response.data


def fake_now(year):
    class FakeDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(year, 6, 1, 8, 30, 15, tzinfo=tz)
    return FakeDatetime


def test_footer_shows_only_2026_in_2026(monkeypatch):
    monkeypatch.setattr(app_module, "datetime", fake_now(2026))
    with app.test_client() as client:
        html = client.get("/").get_data(as_text=True)
    assert "QPI Calc for AdDU &copy; Ogs Peace 2026\n" in html


def test_footer_shows_range_after_2026(monkeypatch):
    monkeypatch.setattr(app_module, "datetime", fake_now(2028))
    with app.test_client() as client:
        html = client.get("/").get_data(as_text=True)
    assert "QPI Calc for AdDU &copy; Ogs Peace 2026 - 2028" in html


def test_clock_starts_at_server_time(monkeypatch):
    monkeypatch.setattr(app_module, "datetime", fake_now(2026))
    with app.test_client() as client:
        html = client.get("/").get_data(as_text=True)
    assert 'aria-label="Philippine time 08:30:15"' in html
