import requests
from datetime import datetime

#Tokens
NOTION_TOKEN = "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"  
DATABASE_ID = "22dff8a7148c8067975fcf2521925911" # From Notion url, after last / and before ?

# Notion API headers
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28" # Doesn't really matter the version
}

# Stuff added
new_page_data = {
    "parent": { "database_id": DATABASE_ID },
    "properties": {
        "Name": {
            "title": [{
                "text": { "content": "Test Assignment" }
            }]
        },
        "Course": {
            "rich_text": [{
                "text": { "content": "PHIL&101" }
            }]
        },
        "Due Date": {
            "date": {
                "start": datetime.now().isoformat()
            }
        },
        "Status": {
            "select": {
                "name": "Not Started"
            }
        },
        "Notes": {
            "rich_text": [{
                "text": { "content": "This is a test sync from Python." }
            }]
        }
    }
}

# Request to Notion to make new page
response = requests.post(
    "https://api.notion.com/v1/pages",
    headers=headers,
    json=new_page_data
)

# Print the result
print("Status:", response.status_code)
print("Response:", response.json())
