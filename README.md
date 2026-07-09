# ✍️ Scribe: Google Calendar MCP Server

Scribe is a **Model Context Protocol (MCP)** server that allows CLI AI assistants (such as the Google Antigravity `agy` CLI or custom agents) to securely manage your Google Calendar schedule, events, and focus time using natural language.

---

## 🔌 Exposed MCP Tools

Once loaded by an AI client, Scribe registers the following tools:

- **`list_events`:** View upcoming meetings and appointments.
- **`create_event`:** Schedule new events (supports summaries, descriptions, date-times, and locations).
- **`reschedule_event`:** Change the time range of an existing event ID.
- **`delete_event`:** Remove/cancel an event.
- **`search_events`:** Find appointments matching a free-text search query.

---

## 🛠️ Step-by-Step Setup

### Step 1: Install Python Dependencies
Set up your python environment and install the required modules:
```bash
pip install -r requirements.txt
```

### Step 2: Configure Google Cloud OAuth Client
Because Google Calendar requires secure authentication, you must configure a private Desktop OAuth Client in the Google Cloud Console:

1. Open the **[Google Cloud Console](https://console.cloud.google.com/)**.
2. Create a new project (e.g. `Scribe-Calendar`).
3. Search for **Google Calendar API** in the library search bar and click **Enable**.
4. Go to the **OAuth Consent Screen** panel on the left sidebar:
   - Select **External** user type and click Create.
   - Enter your email under support and developer contacts.
   - Under **Test Users**, click **Add Users** and add your own Google email address (so your private app can authenticate).
5. Go to the **Credentials** panel on the left sidebar:
   - Click **Create Credentials** -> **OAuth Client ID**.
   - Select **Desktop App** as the Application Type.
   - Name it (e.g. `Scribe-CLI`) and click Create.
6. Under the created Client ID row, click the **Download icon** on the far right to download the client secrets JSON.
7. Save the downloaded JSON file directly into this `scribe` directory under the exact name:
   `credentials.json`

---

### Step 3: Run the Authentication Script
Execute the authentication script to login and generate your offline access token:
```bash
./auth.py
```
*A browser window will open asking you to authorize the application. Log in with the Google Account you added as a test user in Step 2. Once authorized, Scribe will save your session details locally in `token.json`.*

---

### Step 4: Link Scribe to Google Antigravity CLI
To enable your Antigravity agent to read and write to your calendar, add Scribe to your CLI settings file:

1. Open the configuration file:
   `~/.gemini/antigravity-cli/settings.json`
2. Add Scribe under the `mcpServers` settings block:
   ```json
   {
     "mcpServers": {
       "scribe": {
         "command": "python3",
         "args": ["/home/keen/Desktop/Projects and Codes/scribe/scribe_server.py"]
       }
     }
   }
   ```

---

## 🚀 Usage Examples

Start the Antigravity TUI or prompt `agy` directly:
- *"Do I have any meetings tomorrow?"*
- *"Add a meeting with Sarah tomorrow at 10am for 1 hour about project launch"*
- *"Reschedule my focus time tomorrow afternoon to 3pm"*
- *"Cancel the lunch appointment on Friday"*

---

## 📅 Timetable Importer (`add_schedule.py`)

Scribe includes a utility script to bulk import recurring university classes or recurring weekly schedules:
- **Usage:** Run the script locally once you are authenticated:
  ```bash
  ./add_schedule.py
  ```
- **Configuration:** You can edit the classes list in `add_schedule.py` to change titles, days of the week, times, rooms, or instructors.
- **Semester Boundaries:** Currently pre-configured to populate your 3rd Year 1st Semester from **June 29th, 2026** to **November 7th, 2026** with weekly recurrence rules.

