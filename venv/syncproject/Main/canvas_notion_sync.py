# Imports
import requests
from datetime import datetime
import pytz

# Tokens
CANVAS_TOKEN = "9~MrXR6fXZcYQ66MeZnZT8am8CD7yzPKBWx3U24eCvNQWrvFKwUvnTKvNmTvemLPkz"
CANVAS_URL = "https://bc.instructure.com/api/v1" # remember not bellevuecollege, it is bc
NOTION_TOKEN = "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"  
DATABASE_ID = "22dff8a7148c8067975fcf2521925911"

# Headers
notion_headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}
canvas_headers = {
    "Authorization": f"Bearer {CANVAS_TOKEN}"
}

# Functions
### Grabbing courses
def get_courses():
    response = requests.get(f"{CANVAS_URL}/courses", headers=canvas_headers)
    if response.status_code != 200:
        print("Error fetching courses:", response.status_code, response.json())
        return []
    return response.json()
### Grabbing Assignments
def get_assignments(course_id):
    response = requests.get(f"{CANVAS_URL}/courses/{course_id}/assignments", headers=canvas_headers)
    url = f"{CANVAS_URL}/courses/{course_id}/assignments?include[]=submission"
    response = requests.get(url, headers=canvas_headers)
    if response.status_code != 200:
        print(f"Error fetching assignments for course {course_id}:", response.status_code)
        return []
    return response.json()
### Sending data to notion
def send_to_notion(course_name, assignment_name, due_datetime, points="", notes=""):
    if notes is None:
        notes = "No Description"

    notion_payload = {
        "parent": { "database_id": DATABASE_ID },
        "properties": {
            "Assignment Name": {
                "title": [{
                    "text": { "content": assignment_name }
                }]
            },
            "Course": {
                "rich_text": [{
                    "text": { "content": course_name }
                }]
            },
            "Due Date": {
                "date": {
                    "start": due_datetime.isoformat()
                }
            },
            "Status": {
                "select": {
                    "name": "Not Started"
                }
            },
            "Points": {
                "rich_text": [{
                    "text": {"content": points}
                }]
            },
            "Notes": {
                "rich_text": [{
                    "text": { "content": notes[:200] }
                }]
            }
        }
    }
    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers=notion_headers,
        json=notion_payload
    )

    if response.status_code != 200:
        print(f"❌ Failed to add {assignment_name} to Notion:", response.status_code, response.text)
    else:
        print(f"✅ Added: {assignment_name}")
### Checking if assignment is already in Notion
def get_existing_assignments():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    existing = set()

    has_more = True
    next_cursor = None

    while has_more:
        payload = {"page_size": 100}
        if next_cursor:
            payload["start_cursor"] = next_cursor

        response = requests.post(url, headers=notion_headers, json=payload)
        data = response.json()

        for result in data["results"]:
            try:
                title = result["properties"]["Assignment Name"]["title"][0]["text"]["content"]
                course = result["properties"]["Course"]["rich_text"][0]["text"]["content"]
                existing.add((course, title))
            except (KeyError, IndexError):
                continue

        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor", None)

    return existing
### Full function
def pull_all_assignments():
    print("\n=== Pulling Assignments ===")
    existing_assignments = get_existing_assignments()
    courses = get_courses()

    for course in courses:
        course_id = course['id']
        course_name_full = course['name']
        course_name = course_name_full.split("  ")[0].strip()
        print(f"\n📘 {course_name}")
        assignments = get_assignments(course_id)
        for a in assignments:
            if a['workflow_state'] != 'published' or not a['due_at']:
                continue
            normalized_key = (course_name.strip().lower(), a['name'].strip().lower())
            if normalized_key in {(c.strip().lower(), t.strip().lower()) for (c, t) in existing_assignments}:
                print(f"🔁 Skipping existing: {a['name']}")
                continue

            due = datetime.strptime(a['due_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)
            pacific = pytz.timezone('US/Pacific')
            due_local = due.replace(tzinfo=pytz.utc).astimezone(pacific)

            points_possible = a.get("points_possible", 0)
            submission = a.get("submission")

            if submission:
                submitted_at = submission.get("submitted_at")
                score = submission.get("score")
                missing = submission.get("missing")

                if submission.get("score") is not None:
                    points_display = f"{submission['score']}/{points_possible}"
                elif submitted_at:
                    submitted_dt = datetime.strptime(submitted_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)
                    if submitted_dt > due:
                        points_display = f"Late -/{points_possible}"
                    else:
                        points_display = f"Submitted -/{points_possible}"
                elif submission.get("submitted_at"):
                    points_display = f"Submitted -/{points_possible}"
                elif submission.get("missing"):
                    points_display = f"Not Submitted -/{points_possible}"
                else:
                    points_display = f"-/{points_possible}"
            else: #redundancy avoids the error when the submission is 'none'
                points_display = f"-/{points_possible}"

            send_to_notion(
                course_name=course_name,
                assignment_name=a['name'],
                due_datetime=due_local,
                points=points_display,
                notes=""
            )


# Run the sync
pull_all_assignments()