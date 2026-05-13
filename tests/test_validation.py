"""
tests/test_validation.py
Input validation ke edge case tests
"""
import pytest


class TestCourseValidation:
    """Course model validation tests"""

    def test_title_with_script_tag(self, client, admin_headers):
        res = client.post("/create", json={
            "title": "<script>alert('xss')</script>",
            "instructor": "John Doe", "category": "programming",
            "price": 499.0, "duration_hours": 10
        }, headers=admin_headers)
        assert res.status_code == 422

    def test_title_too_short(self, client, admin_headers):
        res = client.post("/create", json={
            "title": "Ab", "instructor": "John Doe",
            "category": "programming", "price": 499.0, "duration_hours": 10
        }, headers=admin_headers)
        assert res.status_code == 422

    def test_price_zero(self, client, admin_headers):
        res = client.post("/create", json={
            "title": "Valid Title", "instructor": "John Doe",
            "category": "programming", "price": 0, "duration_hours": 10
        }, headers=admin_headers)
        assert res.status_code == 422

    def test_price_negative(self, client, admin_headers):
        res = client.post("/create", json={
            "title": "Valid Title", "instructor": "John Doe",
            "category": "programming", "price": -500, "duration_hours": 10
        }, headers=admin_headers)
        assert res.status_code == 422

    def test_price_too_many_decimals(self, client, admin_headers):
        res = client.post("/create", json={
            "title": "Valid Title", "instructor": "John Doe",
            "category": "programming", "price": 499.999, "duration_hours": 10
        }, headers=admin_headers)
        assert res.status_code == 422

    def test_duration_float_rejected(self, client, admin_headers):
        res = client.post("/create", json={
            "title": "Valid Title", "instructor": "John Doe",
            "category": "programming", "price": 499.0, "duration_hours": 10.5
        }, headers=admin_headers)
        assert res.status_code == 422

    def test_duration_zero(self, client, admin_headers):
        res = client.post("/create", json={
            "title": "Valid Title", "instructor": "John Doe",
            "category": "programming", "price": 499.0, "duration_hours": 0
        }, headers=admin_headers)
        assert res.status_code == 422

    def test_discount_100_percent(self, client, admin_headers):
        res = client.post("/create", json={
            "title": "Valid Title", "instructor": "John Doe",
            "category": "programming", "price": 499.0,
            "duration_hours": 10, "discount_percent": 100.0
        }, headers=admin_headers)
        assert res.status_code == 422

    def test_discount_negative(self, client, admin_headers):
        res = client.post("/create", json={
            "title": "Valid Title", "instructor": "John Doe",
            "category": "programming", "price": 499.0,
            "duration_hours": 10, "discount_percent": -10.0
        }, headers=admin_headers)
        assert res.status_code == 422

    def test_instructor_with_numbers(self, client, admin_headers):
        res = client.post("/create", json={
            "title": "Valid Title", "instructor": "John123",
            "category": "programming", "price": 499.0, "duration_hours": 10
        }, headers=admin_headers)
        assert res.status_code == 422


class TestAuthValidation:
    """Auth model validation tests"""

    def test_password_no_uppercase(self, client):
        res = client.post("/auth/register", json={
            "username": "testval1", "email": "testval1@example.com",
            "password": "lowercase@1234", "role": "user"
        })
        assert res.status_code == 422

    def test_password_no_lowercase(self, client):
        res = client.post("/auth/register", json={
            "username": "testval2", "email": "testval2@example.com",
            "password": "UPPERCASE@1234", "role": "user"
        })
        assert res.status_code == 422

    def test_password_no_number(self, client):
        res = client.post("/auth/register", json={
            "username": "testval3", "email": "testval3@example.com",
            "password": "NoNumber@Pass", "role": "user"
        })
        assert res.status_code == 422

    def test_password_no_special_char(self, client):
        res = client.post("/auth/register", json={
            "username": "testval4", "email": "testval4@example.com",
            "password": "NoSpecial1234", "role": "user"
        })
        assert res.status_code == 422

    def test_password_too_short(self, client):
        res = client.post("/auth/register", json={
            "username": "testval5", "email": "testval5@example.com",
            "password": "Ab@1", "role": "user"
        })
        assert res.status_code == 422

    def test_username_special_chars(self, client):
        res = client.post("/auth/register", json={
            "username": "bad user!", "email": "baduser@example.com",
            "password": "Valid@1234", "role": "user"
        })
        assert res.status_code == 422

    def test_email_missing_at(self, client):
        res = client.post("/auth/register", json={
            "username": "testval6", "email": "notanemail.com",
            "password": "Valid@1234", "role": "user"
        })
        assert res.status_code == 422

    def test_email_missing_domain(self, client):
        res = client.post("/auth/register", json={
            "username": "testval7", "email": "user@",
            "password": "Valid@1234", "role": "user"
        })
        assert res.status_code == 422

    def test_review_rating_out_of_range(self, client, user_headers):
        res = client.post("/reviews/course/1",
                          json={"rating": 10}, headers=user_headers)
        assert res.status_code == 422

    def test_review_with_url(self, client, user_headers, admin_headers, sample_course):
        client.post("/create", json={**sample_course,
                    "title": "Url Review Test"}, headers=admin_headers)
        courses = client.get("/courses").json()
        cid = courses[-1]["id"]
        res = client.post(f"/reviews/course/{cid}", json={
            "rating": 4,
            "review": "Check this http://spam.com for more"
        }, headers=user_headers)
        assert res.status_code == 422
