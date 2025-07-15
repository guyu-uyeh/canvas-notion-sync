import requests

# Token
CANVAS_TOKEN = "Your Canvas token"
CANVAS_URL = "your school's API url"

headers = {
    "Authorization": f"Bearer {CANVAS_TOKEN}"
}

def get_courses(): # get courses from Canvas
    response = requests.get(f"{CANVAS_URL}/courses", headers=headers)
    if response.status_code == 200:
        courses = response.json()
        for course in courses:
            print(f"{course['id']} — {course['name']}")
    else:
        print("Error:", response.status_code, response.json()) # failed

# Run
get_courses()
