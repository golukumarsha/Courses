import requests

BASE = "http://127.0.0.1:8000"

# Step 1: Login
login = requests.post(f"{BASE}/auth/login", json={
    "email": "kumargolu83353@gmail.com",
    "password": "golu1234"
})
print("LOGIN STATUS:", login.status_code)
print("LOGIN RESPONSE:", login.text)

if login.status_code != 200:
    print("Login failed!")
    exit()

token = login.json()["access_token"]

# Step 2: Create course
create = requests.post(f"{BASE}/create",
                       headers={
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
},
    json={
        "title": "Test Course",
        "instructor": "Test Instructor",
        "category": "programming",
        "price": 999.0,
        "duration_hours": 10,
        "is_published": True,
        "discount_percent": 5.0
}
)
print("\nCREATE STATUS:", create.status_code)
print("CREATE RESPONSE:", create.text)
