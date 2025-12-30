import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesAPI:
    def test_root_redirect(self):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.url.path == "/static/index.html"

    def test_get_activities(self):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()

        # Check that we have activities
        assert isinstance(data, dict)
        assert len(data) > 0

        # Check structure of first activity
        first_activity = next(iter(data.values()))
        assert "description" in first_activity
        assert "schedule" in first_activity
        assert "max_participants" in first_activity
        assert "participants" in first_activity
        assert isinstance(first_activity["participants"], list)

    def test_signup_successful(self):
        """Test successful signup for an activity"""
        # Use an activity that exists and an email not already signed up
        activity_name = "Soccer Team"
        email = "test@example.com"

        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

        # Verify the participant was added
        response = client.get("/activities")
        activities = response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity"""
        response = client.post("/activities/NonExistent/signup?email=test@example.com")
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_already_signed_up(self):
        """Test signup when student is already signed up"""
        activity_name = "Soccer Team"
        email = "existing@example.com"

        # First signup
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Try to signup again
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_unregister_successful(self):
        """Test successful unregister from an activity"""
        activity_name = "Swimming Club"
        email = "test_unregister@example.com"

        # First sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Then unregister
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

        # Verify the participant was removed
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_activity_not_found(self):
        """Test unregister from non-existent activity"""
        response = client.delete("/activities/NonExistent/unregister?email=test@example.com")
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_not_signed_up(self):
        """Test unregister when student is not signed up"""
        activity_name = "Art Club"
        email = "not_signed_up@example.com"

        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]