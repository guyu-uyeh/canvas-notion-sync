import requests

# Token
CANVAS_TOKEN = "9~MrXR6fXZcYQ66MeZnZT8am8CD7yzPKBWx3U24eCvNQWrvFKwUvnTKvNmTvemLPkz"
CANVAS_URL = "https://bc.instructure.com/api/v1"

headers = {
    "Authorization": f"Bearer {CANVAS_TOKEN}"
}

def get_courses():
    response = requests.get(f"{CANVAS_URL}/courses", headers=headers)
    if response.status_code == 200:
        courses = response.json()
        for course in courses:
            print(f"{course['id']} — {course['name']}")
    else:
        print("Error:", response.status_code, response.json())

# Run
get_courses()
