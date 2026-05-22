import requests
from bs4 import BeautifulSoup
import re

url = "https://scholarscup.org/calendar/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

date_pattern = re.compile(
    r'(January|February|March|April|May|June|July|August|September|October|November|December)'
    r'\s+\d{1,2}(?:[–\-]\d{1,2})?,?\s+\d{4}'
)

upcoming_section = soup.find("h2", string=lambda t: t and "Upcoming Regional" in t)
section = soup.find(string=lambda t: t and "Upcoming Regional" in t)
print("Found section tag:", section.parent.name if section else "NOT FOUND")

if not upcoming_section:
    print("Could not find Upcoming Regional Events section!")
    exit()

headings = []
node = upcoming_section.find_next_sibling()
while node:
    if node.name == "h2":
        break  
    if node.name == "h3":
        headings.append(node)
    node = node.find_next_sibling()

events = []

for h3 in headings:
    name = h3.get_text(strip=True)
    if not any(word in name for word in ["Round", "Tournament", "Global", "Champions"]):
        continue

    h4 = h3.find_next_sibling("h4")
    location = h4.get_text(strip=True) if h4 else "TBA"

    date_text = "Date TBA"
    if h4:
        raw = ""
        node = h4.next_sibling
        count = 0
        while node and count < 10:
            if hasattr(node, 'name') and node.name == 'h3':
                break
            raw += str(node)
            node = node.next_sibling
            count += 1
        match = date_pattern.search(raw)
        if match:
            date_text = match.group(0).strip()

    events.append({"name": name, "location": location, "date": date_text})

print(f"Found {len(events)} events")

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

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

updated_html = re.sub(
    r'<!-- CALENDAR-START -->.*?<!-- CALENDAR-END -->',
    new_calendar_html,
    html,
    flags=re.DOTALL
)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(updated_html)

print("Calendar updated successfully!")
