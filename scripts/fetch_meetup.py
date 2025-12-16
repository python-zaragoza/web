#!/usr/bin/env python3
"""
Fetch upcoming and past Meetup events for a group and write assets/events.json.

Priority order:
1) Use Meetup API (requires MEETUP_TOKEN via OAuth, and MEETUP_GROUP urlname).
2) Fallback: parse the group's public iCal feed for upcoming events only.

Env vars:
- MEETUP_GROUP (e.g. "python_zgz")
- MEETUP_TOKEN (OAuth token) [optional but recommended]

Writes:
- assets/events.json (list of events with fields: name, link, time(ms), venue{name}, description)
"""

from __future__ import annotations
import os
import json
from typing import Any, Dict, List

import httpx

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
OUTPUT_PATH = os.path.join(ASSETS_DIR, "events.json")


def _ensure_assets_dir() -> None:
    os.makedirs(ASSETS_DIR, exist_ok=True)


def fetch_api(group: str, token: str) -> List[Dict[str, Any]]:
    url = f"https://api.meetup.com/{group}/events"
    # Request both upcoming and past (descending), large page size
    params = {"status": "upcoming,past", "desc": "true", "page": 200}
    headers = {"Authorization": f"Bearer {token}"}
    with httpx.Client(timeout=20.0) as client:
        r = client.get(url, params=params, headers=headers)
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, list):
            return []
        events: List[Dict[str, Any]] = []
        for ev in data:
            # Normalize minimal fields
            name = ev.get("name")
            link = ev.get("link") or ev.get("event_url")
            time_ms = ev.get("time")  # epoch ms
            venue = None
            if isinstance(ev.get("venue"), dict):
                vname = ev["venue"].get("name")
                if vname:
                    venue = {"name": vname}
            # Per request: use SUMMARY as description; in API 'name' is the closest
            desc = name
            events.append(
                {
                    "name": name,
                    "link": link,
                    "time": time_ms,
                    "venue": venue,
                    "description": desc,
                }
            )
        return events


def fetch_ical(group: str) -> List[Dict[str, Any]]:
    # Fallback: parse iCal feed (usually upcoming events only)
    ical_url = f"https://www.meetup.com/{group}/events/ical/"
    with httpx.Client(timeout=20.0) as client:
        r = client.get(ical_url)
        if r.status_code != 200:
            return []
        raw_lines = r.text.splitlines()

    # Unfold folded lines per RFC 5545 (lines starting with space continue previous)
    lines: List[str] = []
    for raw in raw_lines:
        if raw.startswith(" ") and lines:
            lines[-1] += raw[1:]
        else:
            lines.append(raw)

    events: List[Dict[str, Any]] = []
    cur: Dict[str, Any] | None = None

    for raw in lines:
        line = raw.strip()
        if line == "BEGIN:VEVENT":
            cur = {}
            continue
        if line == "END:VEVENT":
            if cur:
                # DTSTART may appear as DTSTART or DTSTART;TZID=...
                dt = cur.get("DTSTART")
                tzid = cur.get("DTSTART_TZID")
                time_ms = None
                if isinstance(dt, str) and dt:
                    from datetime import datetime, timezone
                    from zoneinfo import ZoneInfo

                    # Try several common formats
                    fmts = [
                        "%Y%m%dT%H%M%SZ",  # UTC with Z
                        "%Y%m%dT%H%M%S",  # no Z
                        "%Y%m%dT%H%M",  # minutes precision
                    ]
                    for fmt in fmts:
                        try:
                            dt_obj = datetime.strptime(dt, fmt)
                            # If the string ends with Z, it's already UTC.
                            # If no Z and TZID provided, localize with that tz.
                            if dt.endswith("Z"):
                                dt_obj = dt_obj.replace(tzinfo=timezone.utc)
                            elif tzid:
                                try:
                                    dt_obj = dt_obj.replace(tzinfo=ZoneInfo(tzid))
                                except Exception:
                                    # Fallback to Europe/Madrid if TZID unknown
                                    dt_obj = dt_obj.replace(
                                        tzinfo=ZoneInfo("Europe/Madrid")
                                    )
                            else:
                                # No tz info; assume Europe/Madrid as Meetup feed usually emits local time
                                dt_obj = dt_obj.replace(
                                    tzinfo=ZoneInfo("Europe/Madrid")
                                )
                            # Convert to UTC for storage
                            dt_obj = dt_obj.astimezone(timezone.utc)
                            time_ms = int(dt_obj.timestamp() * 1000)
                            break
                        except Exception:
                            continue

                events.append(
                    {
                        "name": cur.get("SUMMARY"),
                        "link": cur.get("URL"),
                        "time": time_ms,
                        "venue": (
                            {"name": cur.get("LOCATION")}
                            if cur.get("LOCATION")
                            else None
                        ),
                        # Per request: use SUMMARY as description in iCal too
                        # "description": cur.get("SUMMARY"),
                    }
                )
            cur = None
            continue

        if cur is None:
            continue

        # KEY:VALUE or KEY;PARAM=...:VALUE
        if ":" in line:
            left, value = line.split(":", 1)
            value = value.strip()
            # Extract base key and params
            if ";" in left:
                base, param_str = left.split(";", 1)
                base_key = base.strip().upper()
                # Very light param parsing (e.g., TZID=Europe/Madrid)
                params = {}
                for part in param_str.split(";"):
                    if "=" in part:
                        k, v = part.split("=", 1)
                        params[k.strip().upper()] = v.strip()
            else:
                base_key = left.strip().upper()
                params = {}

            cur[base_key] = value
            # Capture TZID for DTSTART if present
            if base_key == "DTSTART" and "TZID" in params:
                cur["DTSTART_TZID"] = params["TZID"]
        else:
            # No colon; ignore
            pass

    return events


def main() -> int:
    group = os.getenv("MEETUP_GROUP") or "python_zgz"
    token = os.getenv("MEETUP_TOKEN")
    _ensure_assets_dir()

    events: List[Dict[str, Any]] = []
    if token:
        try:
            events = fetch_api(group, token)
        except Exception as e:
            print(f"[fetch_meetup] API fetch failed: {e}")
    if not events:
        try:
            events = fetch_ical(group)
        except Exception as e:
            print(f"[fetch_meetup] iCal fetch failed: {e}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(events)} events to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
