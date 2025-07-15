"""
Canvas to Notion Sync Script - 07/14/2025
-------------------------------
This Python script automatically pulls assignment data from a user's Canvas LMS and sends it to a Notion database.

Features:
- Canvas API authentication
- Notion API integration
- Filters out existing assignments to avoid duplicates
- Converts due dates to Pacific Time (US/Pacific, UT-7)

Setup Requirements:
- A Notion database with the following properties: Assignment Name (title), Course (rich_text), Due Date (date), Status (select), Points (rich_text), Notes (rich_text)
- Canvas API token and Canvas URL (e.g., 'https://school.instructure.com/api/v1')
- Notion integration token and Database ID

Notes:
- The script assumes your Notion database has specific property names (listed above). These must match exactly or errors will occur.
- Limitation is Professors updating assignment due dates, points, etc. The code skips the assignment if the name is identical
- Future updates would include way to check if assignment information is correct everytime script is run, and updating information if incorrect
"""

# Imports
import requests
from datetime import datetime
import pytz

# Tokens
CANVAS_TOKEN = "Your Canvas Token"
CANVAS_URL = "Your Canvas API Url"
NOTION_TOKEN = "Your Notion Token"  
DATABASE_ID = "Your Notion Table ID"

# Headers
notion_headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "" # doesn't exactly matter Notion Version
}
canvas_headers = {
    "Authorization": f"Bearer {CANVAS_TOKEN}"
}

# Gets list of Canvas Courses using API
def get_courses():
    response = requests.get(f"{CANVAS_URL}/courses", headers=canvas_headers)
    if response.status_code != 200:
        print("Error fetching courses:", response.status_code, response.json())
        return []
    return response.json()
# Gets a list of assignments from a specific Course ID on Canvas
def get_assignments(course_id):
    response = requests.get(f"{CANVAS_URL}/courses/{course_id}/assignments", headers=canvas_headers)
    url = f"{CANVAS_URL}/courses/{course_id}/assignments?include[]=submission"
    response = requests.get(url, headers=canvas_headers)
    if response.status_code != 200:
        print(f"Error fetching assignments for course {course_id}:", response.status_code)
        return []
    return response.json()
# Sends an assignment to the Notion database table with relavant information
def send_to_notion(course_name, assignment_name, due_datetime, points="", notes=""):
    if notes is None:
        notes = "No Description"
    # DB Headers: Assignment Name(title), Course(rich_text), Due Date(date), Status(select), Points(rich_text), Notes(rich_text)
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
                "rich_text": [
                    "text": {"content": "" }
                ]
            } # Left blank in Notion but still leaves a string, not completely empty
        }
    }
    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers=notion_headers,
        json=notion_payload
    )

    if response.status_code != 200:
        print(f"❌ Failed: {assignment_name}:", response.status_code, response.text)
    else:
        print(f"✅ Added: {assignment_name}")
# Checking if assignment is already in Notion
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
# Pulls all assignments from Canvas and sends them to the Notion DB
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
            normalized_key = (course_name.strip().lower(), a['name'].strip().lower()) # Checking and Skipping existing assignmnets
            if normalized_key in {(c.strip().lower(), t.strip().lower()) for (c, t) in existing_assignments}:
                print(f"🔁 Skipping existing: {a['name']}")
                continue

            due = datetime.strptime(a['due_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)
            pacific = pytz.timezone('US/Pacific')
            due_local = due.replace(tzinfo=pytz.utc).astimezone(pacific)

            points_possible = a.get("points_possible", 0)
            submission = a.get("submission")

            if submission: # Determining assignment submission type
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


# Run
pull_all_assignments()