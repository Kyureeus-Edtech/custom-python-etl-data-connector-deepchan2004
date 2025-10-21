from datetime import datetime
from typing import Dict, List, Any
from extract import extract_wayback

def transform_wayback(data: Dict[str, Any]) -> Dict[str, Any]:

    transformed = {
        "source": "wayback",
        "url": data.get("url"),
        "status": data.get("status", "unknown"),
        "fetched_at": datetime.utcnow(),
    }

    latest = data.get("latest_snapshot")
    if latest:
        transformed["latest_snapshot_url"] = latest.get("snapshot_url")
        transformed["latest_snapshot_timestamp"] = latest.get("timestamp")
        try:
            transformed["latest_snapshot_datetime"] = datetime.strptime(
                latest.get("timestamp"), "%Y%m%d%H%M%S"
            )
        except Exception:
            transformed["latest_snapshot_datetime"] = None


    history = data.get("history", [])
    parsed_history = []
    image_entries = []

    for row in history:
        if len(row) < 5:
            continue

        entry = {
            "timestamp": row[0],
            "original": row[1],
            "status_code": row[2],
            "mime_type": row[3],
            "length": int(row[4]) if row[4].isdigit() else None,
            "archived_url": f"https://web.archive.org/web/{row[0]}/{row[1]}"
        }
        try:
            entry["datetime"] = datetime.strptime(row[0], "%Y%m%d%H%M%S")
        except Exception:
            entry["datetime"] = None

        parsed_history.append(entry)
        if entry["mime_type"].startswith("image/"):
            image_entries.append(entry)

    transformed["total_snapshots"] = len(parsed_history)
    transformed["image_snapshots"] = len(image_entries)
    transformed["history"] = parsed_history[:50]  

    transformed["has_images"] = transformed["image_snapshots"] > 0
    transformed["content_types"] = list(
        {entry["mime_type"] for entry in parsed_history if entry["mime_type"]}
    )

    return transformed

