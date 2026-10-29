import json
from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

FEED_URL = "https://letterboxd.com/0bl1vious/rss/"
LETTERBOXD_NAMESPACE = "{https://letterboxd.com}"
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "letterboxd-feed.json"

request = Request(FEED_URL, headers={"User-Agent": "HB-pencil media feed updater"})
with urlopen(request, timeout=30) as response:
    rss = ET.fromstring(response.read())

entries = []
for item in rss.findall("./channel/item"):
    def field(name):
        return (item.findtext(f"{LETTERBOXD_NAMESPACE}{name}") or "").strip()

    try:
        score = float(field("memberRating") or 0)
    except ValueError:
        score = 0

    entries.append({
        "title": field("filmTitle"),
        "year": field("filmYear"),
        "watchedDate": field("watchedDate"),
        "score": score,
        "filmUrl": (item.findtext("link") or FEED_URL).strip(),
        "descriptionHtml": item.findtext("description") or ""
    })

if not entries:
    raise SystemExit("Letterboxd RSS feed contained no diary entries")

OUTPUT_PATH.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {len(entries)} Letterboxd entries to {OUTPUT_PATH}")
