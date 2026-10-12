#!/usr/bin/env python
"""Download audio and transcribe the new video units with mlx-whisper, one unit at a time.

Usage (with the venv python from setup_env.sh, NOT python3 -I):
    ~/.cache/kabbalah-add-content/venv/bin/python transcribe.py --config <ws>/project.json [--units 12,13] [--force]

For each unit with kind youtube/video and "new": true (or only the units given by --units):
  1. audio/<id>.<ext>: downloaded with yt-dlp (bestaudio, m4a preferred) unless it exists already;
     on HTTP 403 it retries with --extractor-args "youtube:player_client=default,android".
  2. mlx-whisper, sequentially. language "he" -> mlx-community/ivrit-ai-whisper-large-v3-turbo-mlx,
     anything else -> mlx-community/whisper-large-v3-turbo; models are loaded by HF id, so they cache in
     ~/.cache/huggingface. If the primary model fails, the fallback model (whisper-large-v3-turbo) is tried.
  3. transcripts/<id>.json and transcripts/<id>.md (same formats as the original batch script), then
     transcripts/<id>.done. Per-segment diagnostics go to logs/<id>.diag.json, verbose output to
     logs/<id>.segments.log, and progress lines to transcripts/progress.log.
Units with a .done marker are skipped unless --force. --model overrides the primary model (an HF id or a local
folder with MLX weights; a path containing "ivrit" is recorded under the ivrit.ai model name).
Exit 1 when any unit failed.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _common as C  # noqa: E402
# This script runs without -I, so Python put its own folder on sys.path. That folder also holds coverage.py,
# which would shadow the `coverage` package that numba (used by mlx-whisper) imports. Drop it now.
sys.path[:] = [p for p in sys.path if Path(p or ".").resolve() != HERE]

HE_MODEL = "mlx-community/ivrit-ai-whisper-large-v3-turbo-mlx"
HE_MODEL_NAME = ("mlx-community/ivrit-ai-whisper-large-v3-turbo-mlx "
                 "(ivrit.ai Hebrew fine-tune of whisper-large-v3-turbo, fp16, MLX)")
MULTI_MODEL = "mlx-community/whisper-large-v3-turbo"
MULTI_MODEL_NAME = "mlx-community/whisper-large-v3-turbo (OpenAI multilingual, MLX)"
RETRY_ARGS = ["--extractor-args", "youtube:player_client=default,android"]
AUDIO_EXTS = ("m4a", "webm", "opus", "mp3", "wav")

PROGRESS = None  # set in main()


def log(msg):
    line = f"{datetime.now().strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(PROGRESS, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def hms(sec):
    sec = int(sec)
    return f"{sec // 3600:02d}:{(sec % 3600) // 60:02d}:{sec % 60:02d}"


def ytdlp():
    exe = shutil.which("yt-dlp") or str(Path.home() / ".local/bin/yt-dlp")
    if not Path(exe).exists():
        raise SystemExit("yt-dlp not found on PATH or in ~/.local/bin")
    return exe


def find_audio(audio_dir, vid):
    for ext in AUDIO_EXTS:
        p = audio_dir / f"{vid}.{ext}"
        if p.exists() and p.stat().st_size > 0 and not Path(str(p) + ".part").exists():
            return p
    return None


def download(audio_dir, vid, url):
    have = find_audio(audio_dir, vid)
    if have:
        return have
    audio_dir.mkdir(parents=True, exist_ok=True)
    base = [ytdlp(), "-f", "bestaudio[ext=m4a]/bestaudio", "--no-playlist", "--no-progress",
            "-o", str(audio_dir / f"{vid}.%(ext)s")]
    for extra in ([], RETRY_ARGS):
        r = subprocess.run(base + extra + [url], capture_output=True, text=True)
        have = find_audio(audio_dir, vid)
        if r.returncode == 0 and have:
            return have
        if extra or "403" not in (r.stderr + r.stdout):
            break
        log(f"[{vid}] HTTP 403 while downloading; retrying with the android player client")
    tail = (r.stderr or r.stdout or "yt-dlp failed").strip().splitlines()[-1:]
    raise RuntimeError("download failed: %s" % (tail[0] if tail else "?"))


def load_meta(meta_dir, vid):
    p = meta_dir / f"{vid}.json"
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}


def clean_segments(raw):
    segs = []
    dropped_dupes = 0
    dropped_empty = 0
    prev = None
    for s in raw:
        text = s["text"].strip()
        if not text:
            dropped_empty += 1
            continue
        if text == prev:
            dropped_dupes += 1
            continue
        segs.append({
            "start": round(float(s["start"]), 2),
            "end": round(float(s["end"]), 2),
            "text": text,
            "avg_logprob": round(float(s.get("avg_logprob", 0)), 3),
            "compression_ratio": round(float(s.get("compression_ratio", 0)), 3),
            "no_speech_prob": round(float(s.get("no_speech_prob", 0)), 3),
        })
        prev = text
    return segs, dropped_dupes, dropped_empty


def run_one(audio, model_path, opts, logs_dir, vid):
    import mlx_whisper
    # per-segment verbose output goes to a per-file log
    seglog = open(logs_dir / f"{vid}.segments.log", "w", encoding="utf-8")
    old_stdout = sys.stdout
    sys.stdout = seglog
    try:
        t0 = time.time()
        result = mlx_whisper.transcribe(str(audio), path_or_hf_repo=model_path, verbose=True, **opts)
        wall = time.time() - t0
    finally:
        sys.stdout = old_stdout
        seglog.close()
    return result, wall


def write_outputs(out_dir, logs_dir, vid, title, meta, unit, result, wall, model_name, attempts, opts):
    segs, dupes, empties = clean_segments(result["segments"])
    duration = meta.get("duration") or unit.get("duration")
    duration_str = meta.get("duration_string") or unit.get("duration_string") or (hms(duration) if duration else "")
    url = meta.get("webpage_url") or C.unit_url(unit) or f"https://www.youtube.com/watch?v={vid}"
    words = sum(len(s["text"].split()) for s in segs)
    # heuristics for the quality note
    low_lp = sum(1 for s in segs if s["avg_logprob"] < -1.0)
    high_cr = sum(1 for s in segs if s["compression_ratio"] > 2.4)
    gaps = []
    for a, b in zip(segs, segs[1:]):
        g = b["start"] - a["end"]
        if g > 60:
            gaps.append((a["end"], b["start"], round(g, 1)))
    tail_gap = (duration - segs[-1]["end"]) if (duration and segs) else None
    stats = {
        "segments": len(segs), "words": words, "dropped_consecutive_duplicates": dupes,
        "dropped_empty": empties, "segments_low_logprob": low_lp,
        "segments_high_compression": high_cr, "gaps_over_60s": gaps,
        "tail_uncovered_seconds": round(tail_gap, 1) if tail_gap is not None else None,
        "wall_minutes": round(wall / 60, 1), "attempts": attempts,
        "realtime_factor": round(duration / wall, 1) if duration else None,
    }
    out = {
        "id": vid, "title": title, "url": url, "duration": duration,
        "duration_string": duration_str, "model": model_name,
        "transcription_options": opts, "stats": stats,
        "segments": [{"start": s["start"], "end": s["end"], "text": s["text"]} for s in segs],
    }
    with open(out_dir / f"{vid}.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    # keep diagnostics (per-segment probabilities) separately
    with open(logs_dir / f"{vid}.diag.json", "w", encoding="utf-8") as f:
        json.dump({"id": vid, "stats": stats, "segments": segs}, f, ensure_ascii=False, indent=1)
    with open(out_dir / f"{vid}.md", "w", encoding="utf-8") as f:
        f.write(f"# {title}\n")
        f.write(f"מקור: {url}\n")
        f.write(f"אורך: {duration_str}\n")
        f.write(f"מודל: {model_name}\n\n")
        for s in segs:
            f.write(f"[{hms(s['start'])}] {s['text']}\n")
    return stats


def main():
    global PROGRESS
    ap = argparse.ArgumentParser(description="Transcribe new video units with mlx-whisper.", epilog=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--units", default="", help="comma-separated unit numbers, e.g. 12,13")
    ap.add_argument("--force", action="store_true", help="redo units that already have a .done marker")
    ap.add_argument("--model", help="primary model: an HF id or a local folder with MLX weights (default by language)")
    args = ap.parse_args()
    cfg = C.Config(Path(args.config))
    for d in (cfg.audio, cfg.transcripts, cfg.logs):
        d.mkdir(parents=True, exist_ok=True)
    PROGRESS = cfg.transcripts / "progress.log"

    only = {int(x) for x in re.split(r"[,\s]+", args.units.strip()) if x} if args.units.strip() else set()
    units = [u for u in cfg.units if C.is_video(u) and (int(u["n"]) in only if only else u.get("new"))]
    missing = only - {int(u["n"]) for u in units}
    if missing:
        raise SystemExit("not video units in the config: %s" % ", ".join(map(str, sorted(missing))))
    if not args.force:
        for u in units:
            if (cfg.transcripts / f"{u['id']}.done").exists():
                print(f"[{u['id']}] unit {u['n']} already done, skipping")
        units = [u for u in units if not (cfg.transcripts / f"{u['id']}.done").exists()]
    if not units:
        print("nothing to transcribe")
        return 0
    try:
        import mlx_whisper  # noqa: F401
    except ImportError:
        raise SystemExit("mlx_whisper is not importable: run setup_env.sh and use the venv python it prints")
    if not shutil.which("ffmpeg"):
        print("warning: ffmpeg not on PATH; mlx-whisper needs it to decode audio", file=sys.stderr)

    if cfg.language == "he":
        models = [(HE_MODEL, HE_MODEL_NAME), (MULTI_MODEL, MULTI_MODEL_NAME)]
    else:
        models = [(MULTI_MODEL, MULTI_MODEL_NAME)]
    if args.model:
        name = HE_MODEL_NAME if "ivrit" in args.model.lower() else args.model
        models = [(args.model, name)] + [m for m in models if m[0] != args.model][1 if cfg.language == "he" else 0:]
    opts = dict(language=cfg.language, task="transcribe", word_timestamps=False,
                condition_on_previous_text=False,
                compression_ratio_threshold=2.4, logprob_threshold=-1.0,
                no_speech_threshold=0.6)

    log(f"=== batch start; {len(units)} unit(s); primary model {models[0][1]}")
    failed = 0
    for u in units:
        n, vid = int(u["n"]), u["id"]
        done = cfg.transcripts / f"{vid}.done"
        meta = load_meta(cfg.meta, vid)
        title = u.get("title") or meta.get("title") or vid
        try:
            audio = download(cfg.audio, vid, u.get("url") or C.unit_url(u))
        except Exception as e:  # noqa: BLE001
            log(f"[{vid}] unit {n} FAILED: {e}")
            failed += 1
            continue
        log(f"[{vid}] START  unit {n}  {title}  ({meta.get('duration_string') or u.get('duration_string')})  file={audio.name}")
        attempts = []
        ok = False
        for i, (model_path, model_name) in enumerate(models):
            try:
                result, wall = run_one(audio, model_path, opts, cfg.logs, vid)
                attempts.append({"model": model_name, "ok": True})
                stats = write_outputs(cfg.transcripts, cfg.logs, vid, title, meta, u, result, wall,
                                      model_name, attempts, opts)
                log(f"[{vid}] DONE   {stats['wall_minutes']} min, {stats['segments']} segs, {stats['words']} words, "
                    f"dupes={stats['dropped_consecutive_duplicates']}, lowlp={stats['segments_low_logprob']}, "
                    f"gaps>60s={len(stats['gaps_over_60s'])}, tail={stats['tail_uncovered_seconds']}s, "
                    f"model={model_name.split(' ')[0]}")
                with open(done, "w", encoding="utf-8") as f:
                    f.write("%s %s\n" % (datetime.now().isoformat(timespec="seconds"), model_name.split(" ")[0]))
                ok = True
                break
            except Exception as e:  # noqa: BLE001
                attempts.append({"model": model_name, "ok": False, "error": str(e)})
                last = i == len(models) - 1
                log(f"[{vid}] FAILED with {model_name.split(' ')[0]}: {e!r}" + ("" if last else "; retrying with fallback"))
                with open(cfg.logs / f"{vid}.error.log", "a", encoding="utf-8") as f:
                    f.write(traceback.format_exc() + "\n")
        if not ok:
            failed += 1
    log("=== batch finished%s" % (f"; {failed} failed" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
