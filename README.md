# 🎓 Canvas to Notion Sync

This Python script automatically pulls assignment data from a user's **Canvas LMS** and adds it to a custom **Notion database**. It helps students centralize, organize, and track upcoming assignments from multiple courses in Notion.

---

## Features

- Canvas API integration for fetching all published assignments  
- Notion API integration for adding assignments into a database  
- Skips assignments that already exist to prevent duplicates  
- Converts all due dates to Pacific Time (US/Pacific) 

---

## 🛠 Requirements

- Python 3.9+
- A Canvas API token and Canvas API base URL (e.g., `https://school.instructure.com/api/v1`)
- A Notion integration token and Notion database ID
- A Notion database with these exact property names:
  - `Assignment Name` (title)
  - `Course` (rich_text)
  - `Due Date` (date)
  - `Status` (select)
  - `Points` (rich_text)
  - `Notes` (rich_text)

---

## Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/guyu-uyeh/canvas-notion-sync.git
cd canvas-notion-sync
```

### 2. Set Up Your Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Add Your API Keys

Create a `.env` file (or edit directly in the script if local only):

```
CANVAS_TOKEN = "your_canvas_token"
CANVAS_URL = "https://your.canvas.url/api/v1"
NOTION_TOKEN = "your_notion"
DATABASE_ID = "your_notion_database_id"
```

---

## How It Works

The script does the following:
1. Pulls your enrolled Canvas courses.
2. For each course, grabs all published assignments.
3. Skips any assignment that already exists in your Notion database (based on course + title).
4. Converts the due date to Pacific Time.
5. Pushes the assignment info into Notion.

---

##️ Optional: Automate with macOS Launch Agent

You can run this script automatically on login or every X minutes using macOS Launch Agents.

1. Create a `.plist` file in `~/Library/LaunchAgents/`, e.g.:
   ```
   com.yourname.canvasnotionsync.plist
   ```

2. Example entry (replace `YOUR_USERNAME` with your actual macOS username):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.canvas.notion.sync</string>

  <key>ProgramArguments</key>
  <array>
    <string>/Users/YOUR_USERNAME/projects/canvas-notion-sync/venv/bin/python</string>
    <string>/Users/YOUR_USERNAME/projects/canvas-notion-sync/venv/syncproject/Main/canvas_notion_sync.py</string>
  </array>

  <key>StartInterval</key>
  <integer>1800</integer> <!-- every 30 minutes -->

  <key>RunAtLoad</key>
  <true/>
</dict>
</plist>
```

3. Load the agent:

```bash
launchctl load ~/Library/LaunchAgents/com.canvas.notion.sync.plist
```

---

## Notes

- This version intentionally leaves the `Notes` column blank so users can fill in their own.
- Professors updating assignments after the fact may lead to missed updates.
- Future updates could include syncing and updating existing entries.

---

