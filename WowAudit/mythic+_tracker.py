import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import os
import json

# --- CONFIG ---
GOOGLE_SHEET_KEY = os.environ["GOOGLE_SHEET_KEY"]
SHEET_GID = "0"  # GID for "Overview" tab
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL_DEV_TESTING"]
DISCORD_ROLE_ID = os.environ["DISCORD_ROLE_ID_OFFICER"]
CREDS_FILE = os.environ["GOOGLE_CREDS_JSON"]

# --- AUTHENTICATE ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
client = gspread.authorize(creds)

# Open the sheet by key and go to the "Mythic+ Done" tab
sheet = client.open_by_key(GOOGLE_SHEET_KEY).worksheet("Mythic+ Done")

# --- FETCH DATA (RAW VALUES) ---
raw_data = sheet.get_all_values()

# Column mapping: A=0, I=8, J=9
rows = raw_data[1:]  # skip header row

report_lines = []
for row in rows:
    if len(row) < 10:  # skip empty / incomplete rows
        continue

    character = row[0].strip()              # Column A = Character
    try:
        dungeons_done = int(row[8])         # Column I = This Week
    except ValueError:
        dungeons_done = 0
    highest_key = row[9]                    # Column J = Highest This Week

    if not character or character.lower().startswith("refreshed"):
        continue

    warning = " ⚠️ **Less than 8 runs this week!**" if dungeons_done < 8 else ""
    line = f"**{character}** → {dungeons_done} runs | Highest key: {highest_key}{warning}"
    report_lines.append(line)

# --- HEADER MESSAGE ---
role_tag = f"<@&{DISCORD_ROLE_ID}>" if DISCORD_ROLE_ID else ""
header_message = (
    f"{role_tag}\n"
    "Good evening and happy Sunday all! Here are the current Mythic+ standings for this week. "
    "You still have one day left to complete your runs and fill your Mythic+ vault slots before the weekly reset. "
    "For core raiders, this is a required task. Please make sure it’s completed, "
    "and don’t hesitate to reach out if you need assistance."
)

# --- EMBED ---
embed = {
    "title": "Mythic+ Weekly Report",
    "description": "\n".join(report_lines),
    "color": 3447003  # blue (you can change this)
}

# --- SEND TO DISCORD ---
if DISCORD_WEBHOOK_URL:
    # send header message
    requests.post(DISCORD_WEBHOOK_URL, json={"content": header_message})

    # send embed
    payload = {"embeds": [embed]}
    r = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if r.status_code != 204:
        print(f"Discord webhook error: {r.status_code} {r.text}")
    else:
        print("Embed sent ✅")
else:
    print("No Discord webhook URL configured. Here’s the report:\n")
    print(header_message)
    print("\n--- EMBED ---")
    print(embed["title"])
    print(embed["description"])
