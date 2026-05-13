"""
tests/test_reviews.py
Reviews & Ratings endpoints ke tests
"""
import pytest


class TestSubmitReview:
    """POST /reviews/course/{id}"""

    def test_submit_review_success(self, client, user_headers, admin_headers, sample_course):
        # Create course first
        client.post("/create", json=sample_course, headers=admin_headers)
        courses = client.get("/courses").json()
        cid = courses[-1]["id"]

        res = client.post(f"/reviews/course/{cid}", json={
            "rating": 5,
            "review": "Bahut accha course hai"
        }, headers=user_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["rating"] == 5
        assert data["course_id"] == cid

    def test_submit_review_no_auth(self, client):
        res = client.post("/reviews/course/1", json={"rating": 4})
        assert res.status_code == 403

    def test_submit_review_invalid_rating_high(self, client, user_headers):
        res = client.post("/reviews/course/1",
                          json={"rating": 6}, headers=user_headers)
        assert res.status_code == 422

    def test_submit_review_invalid_rating_low(self, client, user_headers):
        res = client.post("/reviews/course/1",
                          json={"rating": 0}, headers=user_headers)
        assert res.status_code == 422

    def test_submit_review_course_not_found(self, client, user_headers):
        res = client.post("/reviews/course/99999",
                          json={"rating": 4}, headers=user_headers)
        assert res.status_code == 404

    def test_submit_duplicate_review(self, client, user_headers, admin_headers, sample_course):
        # Create course
        client.post("/create", json={**sample_course,
                    "title": "Dup Review Course"}, headers=admin_headers)
        courses = client.get("/courses").json()
        cid = courses[-1]["id"]

        # First review
        client.post(f"/reviews/course/{cid}", json={"rating": 4,
                    "review": "Good course overall"}, headers=user_headers)
        # Second review — should fail
        res = client.post(f"/reviews/course/{cid}", json={
                          "rating": 3, "review": "Another review attempt"}, headers=user_headers)
        assert res.status_code == 400


class TestGetReviews:
    """GET /reviews/course/{id}"""

    def test_get_reviews_success(self, client):
        res_all = client.get("/courses").json()
        if res_all:
            cid = res_all[0]["id"]
            res = client.get(f"/reviews/course/{cid}")
            assert res.status_code == 200
            data = res.json()
            assert "course_id" in data
            assert "stats" in data
            assert "reviews" in data
            assert "total_reviews" in data["stats"]
            assert "avg_rating" in data["stats"]

    def test_get_reviews_course_not_found(self, client):
        res = client.get("/reviews/course/99999")
        assert res.status_code == 404


class TestUpdateReview:
    """PUT /reviews/course/{id}"""

    def test_update_review_success(self, client, admin_headers, user_headers, sample_course):
        # Create course
        client.post("/create", json={**sample_course,
                    "title": "Update Review Course"}, headers=admin_headers)
        courses = client.get("/courses").json()
        cid = courses[-1]["id"]

        # Submit review first
        client.post(f"/reviews/course/{cid}", json={"rating": 3,
                    "review": "Average course material"}, headers=user_headers)

        # Update it
        res = client.put(f"/reviews/course/{cid}", json={"rating": 5,
                         "review": "Actually great course"}, headers=user_headers)
        assert res.status_code == 200
        assert res.json()["rating"] == 5

    def test_update_nonexistent_review(self, client, user_headers):
        res = client.put("/reviews/course/99999",
                         json={"rating": 4}, headers=user_headers)
        assert res.status_code == 404


class TestDeleteReview:
    """DELETE /reviews/course/{id}"""

    def test_delete_review_success(self, client, admin_headers, user_headers, sample_course):
        # Create course
        client.post("/create", json={**sample_course,
                    "title": "Delete Review Course"}, headers=admin_headers)
        courses = client.get("/courses").json()
        cid = courses[-1]["id"]

        # Submit review
        client.post(f"/reviews/course/{cid}", json={"rating": 4,
                    "review": "Delete this review"}, headers=user_headers)

        # Delete it
        res = client.delete(f"/reviews/course/{cid}", headers=user_headers)
        assert res.status_code == 200
        assert "delete" in res.json()["message"].lower()

    def test_delete_nonexistent_review(self, client, user_headers):
        res = client.delete("/reviews/course/99999", headers=user_headers)
        assert res.status_code == 404


class TestMyReviews:
    """GET /reviews/my/all"""

    def test_get_my_reviews(self, client, user_headers):
        res = client.get("/reviews/my/all", headers=user_headers)
        assert res.status_code == 200
        data = res.json()
        assert "username" in data
        assert "total_reviews" in data
        assert "reviews" in data

    def test_get_my_reviews_no_auth(self, client):
        res = client.get("/reviews/my/all")
        assert res.status_code == 403


class TestTopRated:
    """GET /reviews/top-rated"""

    def test_top_rated_success(self, client):
        res = client.get("/reviews/top-rated")
        assert res.status_code == 200
        data = res.json()
        assert "total" in data
        assert "top_rated" in data
        assert isinstance(data["top_rated"], list)
