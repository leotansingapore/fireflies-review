#!/usr/bin/env python3
"""Fireflies helper for the fireflies-review skill.

  ff.py find [KEYWORD] [--limit N] [--days D]   list recent meetings (newest first)
  ff.py fetch ID --out DIR                       transcript.md + meta.json (+ the video URL)
  ff.py frames ID MM:SS [MM:SS ...] --out DIR    one 1280px frame per timestamp, via ffmpeg

Reads FIREFLIES_API_KEY from the environment. frames needs ffmpeg on PATH.
Standard library only, and no syntax newer than Python 3.8, so the system python works.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from urllib.request import Request, urlopen

API = "https://api.fireflies.ai/graphql"


def api_key():
    key = os.environ.get("FIREFLIES_API_KEY", "").strip()
    if not key:
        sys.exit("FIREFLIES_API_KEY is not set. Copy the API key from your Fireflies settings and run: export FIREFLIES_API_KEY=...")
    return key


def gql(query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = Request(API, data=body, headers={"Authorization": "Bearer " + api_key(), "Content-Type": "application/json"})
    with urlopen(req, timeout=60) as r:
        data = json.load(r)
    if data.get("errors"):
        sys.exit("Fireflies error: " + json.dumps(data["errors"])[:500])
    return data["data"]


def mmss(seconds):
    s = int(seconds or 0)
    return "%02d:%02d:%02d" % (s // 3600, (s % 3600) // 60, s % 60) if s >= 3600 else "%02d:%02d" % (s // 60, s % 60)


def cmd_find(a):
    since = time.time() * 1000 - a.days * 86400000
    q = """query($kw: String, $limit: Int, $skip: Int) {
      transcripts(keyword: $kw, limit: $limit, skip: $skip) { id title date duration participants organizer_email }
    }"""
    rows, skip = [], 0
    # The API returns at most 50 meetings a page, so keep paging until the --days window is covered (capped at 500).
    while True:
        page = gql(q, {"kw": a.keyword or None, "limit": 50, "skip": skip})["transcripts"] or []
        rows += page
        if len(page) < 50 or (page and page[-1]["date"] < since) or len(rows) >= 500:
            break
        skip += 50
    rows = [r for r in rows if r["date"] >= since][: a.limit]
    for r in rows:
        when = time.strftime("%Y-%m-%d %H:%M", time.localtime(r["date"] / 1000))
        print("%s  %s  %3d min  %s  [%d people]" % (r["id"], when, round(r["duration"] or 0), r["title"], len(r["participants"] or [])))
    if not rows:
        print("no meetings found")


def transcript(tid):
    q = """query($id: String!) { transcript(id: $id) {
      id title date duration participants organizer_email video_url transcript_url
      summary { overview action_items }
      sentences { speaker_name text start_time }
    } }"""
    t = gql(q, {"id": tid})["transcript"]
    if not t:
        sys.exit("no transcript with id " + tid)
    return t


def cmd_fetch(a):
    t = transcript(a.id)
    os.makedirs(a.out, exist_ok=True)
    lines, last = [], None
    for s in t.get("sentences") or []:
        name = s.get("speaker_name") or "Unknown"
        if name != last:
            lines.append("\n**%s** (%s)" % (name, mmss(s.get("start_time"))))
            last = name
        lines.append(s.get("text") or "")
    speakers = sorted({(s.get("speaker_name") or "Unknown") for s in t.get("sentences") or []})
    when = time.strftime("%Y-%m-%d %H:%M", time.localtime((t.get("date") or 0) / 1000))
    head = [
        "# " + (t.get("title") or ""),
        "",
        "- When: %s, %s min" % (when, round(t.get("duration") or 0)),
        "- Fireflies: https://app.fireflies.ai/view/" + t["id"],
        "- Invite emails: " + ", ".join(t.get("participants") or []),
        "- Speaker names (as Fireflies heard them, map to emails yourself): " + ", ".join(speakers),
        "- Video: " + ("yes, run `ff.py frames`" if t.get("video_url") else "none"),
        "",
        "## Fireflies' own summary (owners are often wrong, rebuild them from the transcript)",
        "",
        str((t.get("summary") or {}).get("overview") or "(none)"),
        "",
        str((t.get("summary") or {}).get("action_items") or "(none)"),
        "",
        "## Transcript",
    ]
    open(os.path.join(a.out, "transcript.md"), "w").write("\n".join(head + lines) + "\n")
    meta = {k: t.get(k) for k in ("id", "title", "date", "duration", "participants", "organizer_email", "video_url")}
    meta["speakers"] = speakers
    meta["sentence_count"] = len(t.get("sentences") or [])
    json.dump(meta, open(os.path.join(a.out, "meta.json"), "w"), indent=1)
    print("%s: %d sentences, %d speakers -> %s/transcript.md" % (t.get("title"), meta["sentence_count"], len(speakers), a.out))
    if meta["sentence_count"] < 20:
        print("WARNING: under 20 sentences. Fireflies may still be processing; wait and fetch again.")


def cmd_frames(a):
    url = None
    meta_path = os.path.join(a.out, "meta.json")
    if os.path.exists(meta_path):
        meta = json.load(open(meta_path))
        if meta.get("id") == a.id:
            url = meta.get("video_url")
    url = url or transcript(a.id).get("video_url")
    if not url:
        sys.exit("this meeting has no recording")
    os.makedirs(a.out, exist_ok=True)
    procs = []
    for ts in a.times:
        if not re.match(r"^\d{1,2}(:\d{2}){1,2}$", ts):
            sys.exit("bad timestamp %r, use MM:SS or H:MM:SS" % ts)
        path = os.path.join(a.out, "frame_%s.jpg" % ts.replace(":", "-"))
        cmd = ["ffmpeg", "-nostdin", "-loglevel", "error", "-ss", ts, "-i", url, "-frames:v", "1", "-vf", "scale=1280:-2", "-y", path]
        procs.append((path, subprocess.Popen(cmd)))
    for path, p in procs:
        p.wait()
        print(path if p.returncode == 0 and os.path.exists(path) else "FAILED " + path)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("find")
    f.add_argument("keyword", nargs="?")
    f.add_argument("--limit", type=int, default=10)
    f.add_argument("--days", type=int, default=14)
    g = sub.add_parser("fetch")
    g.add_argument("id")
    g.add_argument("--out", required=True)
    h = sub.add_parser("frames")
    h.add_argument("id")
    h.add_argument("times", nargs="+")
    h.add_argument("--out", required=True)
    a = ap.parse_args()
    {"find": cmd_find, "fetch": cmd_fetch, "frames": cmd_frames}[a.cmd](a)


if __name__ == "__main__":
    main()
