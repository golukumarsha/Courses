"""
tests/test_analytics.py
Analytics endpoints ke tests
"""
import pytest


class TestPopularCategory:
    """GET /analytics/popular-category"""

    def test_popular_category_success(self, client):
        res = client.get("/analytics/popular-category")
        assert res.status_code == 200
        data = res.json()
        assert "most_popular" in data
        assert "total_courses" in data
        assert "all_categories" in data
        assert isinstance(data["all_categories"], list)

    def test_popular_category_structure(self, client):
        res = client.get("/analytics/popular-category")
        cats = res.json()["all_categories"]
        if cats:
            first = cats[0]
            assert "category" in first
            assert "total_courses" in first
            assert "published_courses" in first


class TestAvgPrice:
    """GET /analytics/avg-price"""

    def test_avg_price_success(self, client):
        res = client.get("/analytics/avg-price")
        assert res.status_code == 200
        data = res.json()
        assert "total_categories" in data
        assert "data" in data

    def test_avg_price_structure(self, client):
        res = client.get("/analytics/avg-price")
        items = res.json()["data"]
        if items:
            first = items[0]
            assert "category" in first
            assert "avg_price" in first
            assert "min_price" in first
            assert "max_price" in first
            assert "total_courses" in first

    def test_avg_price_values_valid(self, client):
        res = client.get("/analytics/avg-price")
        for item in res.json()["data"]:
            assert float(item["min_price"]) <= float(
                item["avg_price"]) <= float(item["max_price"])


class TestRevenue:
    """GET /analytics/revenue"""

    def test_revenue_success(self, client):
        res = client.get("/analytics/revenue")
        assert res.status_code == 200
        data = res.json()
        assert "overall_gross_revenue" in data
        assert "overall_net_revenue_after_discount" in data
        assert "by_category" in data

    def test_revenue_net_lte_gross(self, client):
        data = client.get("/analytics/revenue").json()
        gross = float(data["overall_gross_revenue"] or 0)
        net = float(data["overall_net_revenue_after_discount"] or 0)
        assert net <= gross


class TestTopInstructors:
    """GET /analytics/top-instructors"""

    def test_top_instructors_success(self, client):
        res = client.get("/analytics/top-instructors")
        assert res.status_code == 200
        data = res.json()
        assert "total_instructors" in data
        assert "top_instructor" in data
        assert "data" in data

    def test_top_instructors_structure(self, client):
        res = client.get("/analytics/top-instructors")
        items = res.json()["data"]
        if items:
            first = items[0]
            assert "instructor" in first
            assert "total_courses" in first
            assert "avg_price" in first
            assert "net_revenue" in first
            assert "avg_duration_hours" in first


class TestAnalyticsSummary:
    """GET /analytics/summary"""

    def test_summary_success(self, client):
        res = client.get("/analytics/summary")
        assert res.status_code == 200
        data = res.json()
        assert "total_courses" in data
        assert "published_courses" in data
        assert "unpublished_courses" in data
        assert "total_categories" in data
        assert "total_instructors" in data
        assert "pricing" in data
        assert "revenue" in data
        assert "avg_duration_hours" in data

    def test_summary_pricing_keys(self, client):
        pricing = client.get("/analytics/summary").json()["pricing"]
        assert "avg_price" in pricing
        assert "min_price" in pricing
        assert "max_price" in pricing

    def test_summary_revenue_keys(self, client):
        revenue = client.get("/analytics/summary").json()["revenue"]
        assert "gross_revenue" in revenue
        assert "net_revenue" in revenue

    def test_summary_counts_match(self, client):
        summary = client.get("/analytics/summary").json()
        all_count = len(client.get("/courses").json())
        assert summary["total_courses"] == all_count

    def test_summary_pub_unpub_sum(self, client):
        data = client.get("/analytics/summary").json()
        assert data["published_courses"] + \
            data["unpublished_courses"] == data["total_courses"]
