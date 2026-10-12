#!/usr/bin/env python3
"""Fetch video metadata with yt-dlp and fill project.json.

Usage:  python3 -I fetch_meta.py --config <ws>/project.json [--force]

For every unit with kind youtube/video and "new": true:
  - runs `yt-dlp -J` into meta/<id>.json (reused when it exists, unless --force)
  - sets title, duration, duration_string, url and date (d.m.yyyy from upload_date, the page's own format)
    in project.json, and prints any value it changed; a "topic" set by hand is never touched
  - appends a "## <display>: title" block (display = the unit's "label", else "<unit_label> N") with the description to meta/descriptions.md
    (skipped when that id already has a block)
yt-dlp comes from PATH or ~/.local/bin/yt-dlp. On HTTP 403 it retries with the android player client.
Exit 1 when any unit failed.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C  # noqa: E402

RETRY_ARGS = ["--extractor-args", "youtube:player_client=default,android"]


def ytdlp() -> str:
    exe = shutil.which("yt-dlp") or str(Path.home() / ".local/bin/yt-dlp")
    if not Path(exe).exists():
        raise SystemExit("yt-dlp not found on PATH or in ~/.local/bin")
    return exe


def fetch(url: str) -> dict:
    base = [ytdlp(), "-J", "--no-warnings", "--skip-download", "--no-playlist"]
    for extra in ([], RETRY_ARGS):
        r = subprocess.run(base + extra + [url], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout)
        if not extra and "403" not in r.stderr:
            break
        if not extra:
            print("  HTTP 403, retrying with the android player client", file=sys.stderr)
    raise RuntimeError((r.stderr or "yt-dlp failed").strip().splitlines()[-1])


def main() -> int:
    ap = C.arg_parser(__doc__)
    ap.add_argument("--force", action="store_true", help="re-fetch meta/<id>.json even when it exists")
    args = ap.parse_args()
    cfg = C.Config(Path(args.config))
    units = [u for u in cfg.data.get("units", []) if u.get("new") and C.is_video(u)]
    if not units:
        print("no new video units in %s" % cfg.path)
        return 0
    cfg.meta.mkdir(parents=True, exist_ok=True)
    desc_file = cfg.meta / "descriptions.md"
    desc = C.read_text(desc_file) if desc_file.exists() else "# תיאורי הסרטונים (כפי שפורסמו במקור)\n"
    failed = 0
    for u in sorted(units, key=lambda x: int(x["n"])):
        n, vid = int(u["n"]), u.get("id")
        if not vid:
            print("%s: no id, skipped" % C.unit_display(cfg, u))
            failed += 1
            continue
        mf = cfg.meta / ("%s.json" % vid)
        try:
            if mf.exists() and not args.force:
                d = json.loads(C.read_text(mf))
                src = "cached"
            else:
                d = fetch(u.get("url") or C.unit_url(u))
                C.write_text(mf, json.dumps(d, ensure_ascii=False, indent=1) + "\n")
                src = "fetched"
        except Exception as e:  # noqa: BLE001
            print("%s (%s): FAILED: %s" % (C.unit_display(cfg, u), vid, e))
            failed += 1
            continue
        new = {
            "title": (d.get("title") or "").strip(),
            "duration": int(d["duration"]) if d.get("duration") else None,
            "duration_string": d.get("duration_string") or (C.hms(d["duration"]) if d.get("duration") else ""),
            "date": C.date_from_upload(d.get("upload_date") or ""),
        }
        if not u.get("url"):
            new["url"] = d.get("webpage_url") or C.unit_url(u)
        changes = []
        for k, v in new.items():
            if v in (None, ""):
                continue
            if u.get(k) not in (None, "") and u.get(k) != v:
                changes.append("%s: %r -> %r" % (k, u.get(k), v))
            u[k] = v
        print("%s (%s): %s · %s · %s · %s%s" % (
            C.unit_display(cfg, u), vid, src, new["title"], new["duration_string"], new["date"],
            "" if u.get("topic") else " · no topic yet"))
        for c in changes:
            print("   changed " + c)
        if ("- מזהה: %s\n" % vid) not in desc:
            views = d.get("view_count")
            block = ["", "## %s: %s" % (C.unit_display(cfg, u), new["title"]),
                     "- מזהה: %s" % vid,
                     "- קישור: %s" % (d.get("webpage_url") or C.unit_url(u)),
                     "- אורך: %s · פורסם: %s%s" % (new["duration_string"], d.get("upload_date") or "?",
                                                    " · צפיות: %s" % views if views is not None else ""),
                     "", "### התיאור", "", (d.get("description") or "(אין תיאור)").strip(), ""]
            desc = desc.rstrip("\n") + "\n" + "\n".join(block)
    C.write_text(desc_file, desc.rstrip("\n") + "\n")
    cfg.save()
    print("updated %s and %s" % (cfg.path, desc_file))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
