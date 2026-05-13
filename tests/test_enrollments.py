"""
tests/test_enrollments.py
Enrollment endpoints ke tests
"""
import pytest


class TestEnroll:
    """POST /enrollments/enroll/{id}"""

    def test_enroll_success(self, client, user_headers, admin_headers, sample_course):
        # Create published course
        client.post("/create", json=sample_course, headers=admin_headers)
        courses = client.get("/courses").json()
        cid = courses[-1]["id"]

        res = client.post(f"/enrollments/enroll/{cid}", headers=user_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["course_id"] == cid
        assert data["status"] == "active"

    def test_enroll_duplicate(self, client, user_headers, admin_headers, sample_course):
        client.post("/create", json={**sample_course,
                    "title": "Dup Enroll Course"}, headers=admin_headers)
        courses = client.get("/courses").json()
        cid = courses[-1]["id"]

        client.post(f"/enrollments/enroll/{cid}", headers=user_headers)
        res = client.post(f"/enrollments/enroll/{cid}", headers=user_headers)
        assert res.status_code == 400

    def test_enroll_unpublished_course(self, client, user_headers, admin_headers):
        # Create unpublished course
        client.post("/create", json={
            "title": "Unpublished Course",
            "instructor": "Test Teacher",
            "category": "programming",
            "price": 499.0,
            "duration_hours": 10,
            "is_published": False
        }, headers=admin_headers)
        courses = client.get("/courses").json()
        cid = courses[-1]["id"]

        res = client.post(f"/enrollments/enroll/{cid}", headers=user_headers)
        assert res.status_code == 400

    def test_enroll_no_auth(self, client):
        res = client.post("/enrollments/enroll/1")
        assert res.status_code == 403

    def test_enroll_course_not_found(self, client, user_headers):
        res = client.post("/enrollments/enroll/99999", headers=user_headers)
        assert res.status_code == 404


class TestCancelEnrollment:
    """DELETE /enrollments/cancel/{id}"""

    def test_cancel_success(self, client, user_headers, admin_headers, sample_course):
        client.post("/create", json={**sample_course,
                    "title": "Cancel Course"}, headers=admin_headers)
        courses = client.get("/courses").json()
        cid = courses[-1]["id"]

        client.post(f"/enrollments/enroll/{cid}", headers=user_headers)
        res = client.delete(f"/enrollments/cancel/{cid}", headers=user_headers)
        assert res.status_code == 200
        assert "cancel" in res.json()["message"].lower()

    def test_cancel_not_enrolled(self, client, user_headers):
        res = client.delete("/enrollments/cancel/99999", headers=user_headers)
        assert res.status_code == 404


class TestUpdateStatus:
    """PUT /enrollments/status/{id}"""

    def test_update_status_completed(self, client, user_headers, admin_headers, sample_course):
        client.post("/create", json={**sample_course,
                    "title": "Status Course"}, headers=admin_headers)
        courses = client.get("/courses").json()
        cid = courses[-1]["id"]

        client.post(f"/enrollments/enroll/{cid}", headers=user_headers)
        res = client.put(
            f"/enrollments/status/{cid}", json={"status": "completed"}, headers=user_headers)
        assert res.status_code == 200
        assert res.json()["status"] == "completed"

    def test_update_status_invalid(self, client, user_headers):
        res = client.put("/enrollments/status/1",
                         json={"status": "unknown"}, headers=user_headers)
        assert res.status_code == 400


class TestMyEnrollments:
    """GET /enrollments/my"""

    def test_my_enrollments(self, client, user_headers):
        res = client.get("/enrollments/my", headers=user_headers)
        assert res.status_code == 200
        data = res.json()
        assert "username" in data
        assert "stats" in data
        assert "enrollments" in data
        assert "total" in data["stats"]

    def test_my_enrollments_no_auth(self, client):
        res = client.get("/enrollments/my")
        assert res.status_code == 403


class TestTopEnrolled:
    """GET /enrollments/top-courses"""

    def test_top_courses(self, client):
        res = client.get("/enrollments/top-courses")
        assert res.status_code == 200
        data = res.json()
        assert "total" in data
        assert "top_courses" in data

    def test_top_courses_structure(self, client):
        res = client.get("/enrollments/top-courses")
        assert res.status_code == 200
        top = res.json()["top_courses"]
        if top:
            first = top[0]
            assert "title" in first
            assert "total_enrollments" in first


class TestAllEnrollments:
    """GET /enrollments/all (Admin only)"""

    def test_admin_can_see_all(self, client, admin_headers):
        res = client.get("/enrollments/all", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert "stats" in data
        assert "enrollments" in data

    def test_user_cannot_see_all(self, client, user_headers):
        res = client.get("/enrollments/all", headers=user_headers)
        assert res.status_code == 403
