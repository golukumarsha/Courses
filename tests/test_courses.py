"""
tests/test_courses.py
Course CRUD endpoints ke tests
"""
import pytest


class TestHome:
    """GET /home"""

    def test_home(self, client):
        res = client.get("/home")
        assert res.status_code == 200
        assert "message" in res.json()


class TestCreateCourse:
    """POST /create"""

    def test_create_success(self, client, admin_headers, sample_course):
        res = client.post("/create", json=sample_course, headers=admin_headers)
        assert res.status_code == 200
        assert "message" in res.json()

    def test_create_without_auth(self, client, sample_course):
        res = client.post("/create", json=sample_course)
        assert res.status_code == 403

    def test_create_user_cannot_create(self, client, user_headers, sample_course):
        res = client.post("/create", json=sample_course, headers=user_headers)
        assert res.status_code == 403

    def test_create_invalid_price(self, client, admin_headers, sample_course):
        bad = {**sample_course, "price": -100}
        res = client.post("/create", json=bad, headers=admin_headers)
        assert res.status_code == 422

    def test_create_invalid_title_special_chars(self, client, admin_headers, sample_course):
        bad = {**sample_course, "title": "Course <script>alert()</script>"}
        res = client.post("/create", json=bad, headers=admin_headers)
        assert res.status_code == 422

    def test_create_discount_too_high(self, client, admin_headers, sample_course):
        bad = {**sample_course, "discount_percent": 100.0}
        res = client.post("/create", json=bad, headers=admin_headers)
        assert res.status_code == 422

    def test_create_duration_float_rejected(self, client, admin_headers, sample_course):
        bad = {**sample_course, "duration_hours": 10.5}
        res = client.post("/create", json=bad, headers=admin_headers)
        assert res.status_code == 422

    def test_create_missing_required_fields(self, client, admin_headers):
        res = client.post(
            "/create", json={"title": "Only Title"}, headers=admin_headers)
        assert res.status_code == 422


class TestGetCourse:
    """GET /course/{id} and GET /courses"""

    def test_get_all_courses(self, client):
        res = client.get("/courses")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_get_course_by_id_success(self, client, admin_headers, sample_course):
        # Create first
        client.post("/create", json=sample_course, headers=admin_headers)
        res_all = client.get("/courses")
        first_id = res_all.json()[0]["id"]

        res = client.get(f"/course/{first_id}")
        assert res.status_code == 200
        data = res.json()
        assert "title" in data
        assert "instructor" in data
        assert "price" in data

    def test_get_course_not_found(self, client):
        res = client.get("/course/99999")
        assert res.status_code == 404

    def test_get_data_by_id(self, client):
        res_all = client.get("/courses")
        if res_all.json():
            first_id = res_all.json()[0]["id"]
            res = client.get(f"/data/{first_id}")
            assert res.status_code == 200


class TestUpdateCourse:
    """PUT /update/{id}"""

    def test_update_success(self, client, admin_headers, sample_course):
        client.post("/create", json=sample_course, headers=admin_headers)
        courses = client.get("/courses").json()
        cid = courses[-1]["id"]

        updated = {**sample_course,
                   "title": "Updated Python Course", "price": 599.0}
        res = client.put(f"/update/{cid}", json=updated, headers=admin_headers)
        assert res.status_code == 200
        assert "update" in res.json()["message"].lower()

    def test_update_not_found(self, client, admin_headers, sample_course):
        res = client.put("/update/99999", json=sample_course,
                         headers=admin_headers)
        assert res.status_code == 404

    def test_update_without_auth(self, client, sample_course):
        res = client.put("/update/1", json=sample_course)
        assert res.status_code == 403

    def test_update_user_cannot_update(self, client, user_headers, sample_course):
        res = client.put("/update/1", json=sample_course, headers=user_headers)
        assert res.status_code == 403


class TestDeleteCourse:
    """DELETE /delete/{id}"""

    def test_delete_success(self, client, admin_headers, sample_course):
        # Create a temp course to delete
        temp = {**sample_course, "title": "Delete Me Course"}
        client.post("/create", json=temp, headers=admin_headers)
        courses = client.get("/courses").json()
        cid = courses[-1]["id"]

        res = client.delete(f"/delete/{cid}", headers=admin_headers)
        assert res.status_code == 200
        assert "delete" in res.json()["message"].lower()

        # Verify deleted
        check = client.get(f"/course/{cid}")
        assert check.status_code == 404

    def test_delete_not_found(self, client, admin_headers):
        res = client.delete("/delete/99999", headers=admin_headers)
        assert res.status_code == 404

    def test_delete_without_auth(self, client):
        res = client.delete("/delete/1")
        assert res.status_code == 403


class TestFilterCourses:
    """GET /filter"""

    def test_filter_by_category(self, client):
        res = client.get("/filter?category=programming")
        assert res.status_code == 200
        data = res.json()
        for course in data:
            assert course["category"].lower() == "programming"

    def test_filter_by_is_published(self, client):
        res = client.get("/filter?is_published=true")
        assert res.status_code == 200
        for course in res.json():
            assert course["is_published"] is True

    def test_filter_by_min_price(self, client):
        res = client.get("/filter?min_price=500")
        assert res.status_code == 200
        for course in res.json():
            assert course["price"] >= 500

    def test_filter_by_max_price(self, client):
        res = client.get("/filter?max_price=800")
        assert res.status_code == 200
        for course in res.json():
            assert course["price"] <= 800

    def test_filter_combined(self, client):
        res = client.get(
            "/filter?category=programming&is_published=true&min_price=100")
        assert res.status_code == 200

    def test_filter_no_params(self, client):
        res = client.get("/filter")
        assert res.status_code == 200
        assert isinstance(res.json(), list)


class TestSearchCourses:
    """GET /search"""

    def test_search_by_title(self, client):
        res = client.get("/search?q=python")
        assert res.status_code == 200
        data = res.json()
        assert "query" in data
        assert "total_found" in data
        assert "results" in data
        assert data["query"] == "python"

    def test_search_by_instructor(self, client):
        res = client.get("/search?q=sharma")
        assert res.status_code == 200
        assert "results" in res.json()

    def test_search_no_results(self, client):
        res = client.get("/search?q=xyznonexistentxyz123")
        assert res.status_code == 200
        assert res.json()["total_found"] == 0

    def test_search_empty_query(self, client):
        res = client.get("/search?q=")
        assert res.status_code == 422


class TestSortCourses:
    """GET /sort"""

    def test_sort_by_price_asc(self, client):
        res = client.get("/sort?sort_by=price&order=asc")
        assert res.status_code == 200
        data = res.json()
        assert data["sort_by"] == "price"
        assert data["order"] == "asc"
        prices = [c["price"] for c in data["data"]]
        assert prices == sorted(prices)

    def test_sort_by_price_desc(self, client):
        res = client.get("/sort?sort_by=price&order=desc")
        assert res.status_code == 200
        prices = [c["price"] for c in res.json()["data"]]
        assert prices == sorted(prices, reverse=True)

    def test_sort_by_title(self, client):
        res = client.get("/sort?sort_by=title&order=asc")
        assert res.status_code == 200
        titles = [c["title"] for c in res.json()["data"]]
        assert titles == sorted(titles)

    def test_sort_by_duration(self, client):
        res = client.get("/sort?sort_by=duration_hours&order=asc")
        assert res.status_code == 200
        durations = [c["duration_hours"] for c in res.json()["data"]]
        assert durations == sorted(durations)

    def test_sort_invalid_field(self, client):
        res = client.get("/sort?sort_by=invalid_field&order=asc")
        assert res.status_code == 400

    def test_sort_invalid_order(self, client):
        res = client.get("/sort?sort_by=price&order=random")
        assert res.status_code == 400

    def test_sort_with_published_filter(self, client):
        res = client.get("/sort?sort_by=price&order=asc&is_published=true")
        assert res.status_code == 200
        for c in res.json()["data"]:
            assert c["is_published"] is True


class TestPagination:
    """GET /items"""

    def test_pagination_default(self, client):
        res = client.get("/items")
        assert res.status_code == 200
        data = res.json()
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "total_pages" in data
        assert "data" in data
        assert data["page"] == 1
        assert data["limit"] == 5

    def test_pagination_custom(self, client):
        res = client.get("/items?page=1&limit=3")
        assert res.status_code == 200
        data = res.json()
        assert data["limit"] == 3
        assert len(data["data"]) <= 3

    def test_pagination_invalid_page(self, client):
        res = client.get("/items?page=0")
        assert res.status_code == 422

    def test_pagination_limit_too_high(self, client):
        res = client.get("/items?limit=999")
        assert res.status_code == 422
