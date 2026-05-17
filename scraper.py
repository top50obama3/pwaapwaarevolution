import requests
from bs4 import BeautifulSoup
import re

# ── 1. FETCH THE PAGE ──────────────────────────────────────────
url = "https://scholarscup.org/calendar/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# ── 2. FIND ALL EVENTS ─────────────────────────────────────────
# Each event is an <h3> tag with a link, followed by an <h4> (location) and a date
events = []

headings = soup.find_all("h3")

for h3 in headings:
    name = h3.get_text(strip=True)

    # Location is in the next <h4>
    h4 = h3.find_next_sibling("h4")
    location = h4.get_text(strip=True) if h4 else "TBA"

    # Date is a text node after the h4, usually just plain text like "May 16-17, 2026"
    # We'll grab all text after h4 until the next tag
    date_text = ""
    if h4:
        next_node = h4.next_sibling
        while next_node:
            if hasattr(next_node, 'name') and next_node.name in ['h3', 'h2', 'h1']:
                break
            if isinstance(next_node, str):
                cleaned = next_node.strip()
                if cleaned:
                    date_text = cleaned
                    break
            next_node = next_node.next_sibling

    if name and "Round" in name or "Tournament" in name or "Global" in name:
        events.append({
            "name": name,
            "location": location,
            "date": date_text if date_text else "Date TBA"
        })

# ── 3. BUILD THE HTML FOR THE CALENDAR SECTION ─────────────────
calendar_rows = ""
for event in events:
    calendar_rows += f"""
    <div class="calendar-row">
      <div class="calendar-date">{event['date']}</div>
      <div class="calendar-info">
        <strong>{event['name']}</strong>
        <span>{event['location']}</span>
      </div>
    </div>"""

new_calendar_html = f"""<!-- CALENDAR-START -->
  <div style="padding: 48px; max-width: 700px;">
    {calendar_rows}
    <div style="display: flex; gap: 12px; margin-top: 32px; flex-wrap: wrap;">
      <a href="https://scholarscup.org/calendar/" class="btn" target="_blank">All Dates & Full Calendar →</a>
      <a href="https://scholarscup.org/results/" class="btn btn-outline" target="_blank">Results</a>
    </div>
  </div>
<!-- CALENDAR-END -->"""

# ── 4. INJECT INTO index.html ───────────────────────────────────
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace everything between the markers
updated_html = re.sub(
    r'<!-- CALENDAR-START -->.*?<!-- CALENDAR-END -->',
    new_calendar_html,
    html,
    flags=re.DOTALL
)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(updated_html)

print(f"✅ Calendar updated with {len(events)} events!")
