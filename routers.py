from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from models import Course
from utils import read_data, write_data

router = APIRouter()   # ✅ नाम router ही रखना


# 1. Basic Routes
@router.get("/")
def home():
    return {"message": "Course API Running 🚀"}


# 2. GET all Courses
@router.get("/courses")
def get_courses():
    return read_data()


# 3. GET by ID
@router.get("/course/{id}")
def get_course(id: int):
    data = read_data()

    course = next((c for c in data if c["id"] == id), None)

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    return course


# 4. POST create
@router.post("/create")
def create_course(course: Course):
    data = read_data()

    new_id = max([c["id"] for c in data], default=0) + 1

    new_course = course.dict()
    new_course["id"] = new_id

    data.append(new_course)
    write_data(data)

    return {"message": "Course created", "id": new_id}


# 5. PUT update
@router.put("/update/{id}")
def update_course(id: int, course: Course):
    data = read_data()

    for i, c in enumerate(data):
        if c["id"] == id:
            updated = course.dict()
            updated["id"] = id
            data[i] = updated
            write_data(data)
            return {"message": "Course updated"}

    raise HTTPException(status_code=404, detail="Course not found")


# 6. DELETE
@router.delete("/delete/{id}")
def delete_course(id: int):
    data = read_data()

    for i, c in enumerate(data):
        if c["id"] == id:
            data.pop(i)
            write_data(data)
            return {"message": "Course deleted"}

    raise HTTPException(status_code=404, detail="Course not found")


# 7. FILTER
@router.get("/filter")
def filter_courses(
    category: Optional[str] = None,
    instructor: Optional[str] = None,
    price: Optional[float] = None,
    is_published: Optional[bool] = None
):
    data = read_data()

    if category:
        data = [c for c in data if c["category"] == category.lower()]

    if instructor:
        data = [c for c in data if instructor.lower() in c["instructor"].lower()]

    if price:
        data = [c for c in data if c["price"] == price]

    if is_published is not None:
        data = [c for c in data if c["is_published"] == is_published]

    return data


# 8. PAGINATION
@router.get("/pagination")
def paginate(
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1, le=50)
):
    data = read_data()

    start = (page - 1) * limit
    end = start + limit

    return {
        "total": len(data),
        "page": page,
        "limit": limit,
        "data": data[start:end]
    }
