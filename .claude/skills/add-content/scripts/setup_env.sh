#!/usr/bin/env bash
# setup_env.sh: create (or reuse) the transcription venv OUTSIDE the repo and print its python path.
#
# Usage:   bash setup_env.sh
# Result:  the last line on stdout is the venv python, e.g. ~/.cache/kabbalah-add-content/venv/bin/python
#
# - The venv lives at ~/.cache/kabbalah-add-content/venv (override with KABBALAH_VENV).
# - It is made with `uv venv --python 3.12`, because the system python3 is 3.14 and the ML wheels lack it.
#   uv is taken from ~/.local/bin/uv, or from PATH.
# - It installs mlx-whisper only when `import mlx_whisper` fails, so a second run changes nothing. The check runs
#   with -I, so a coverage.py in the current folder (scripts/ has one) cannot shadow the package numba imports.
# - It also warns (stderr) when yt-dlp or ffmpeg is missing; transcribe.py needs both.
set -euo pipefail

VENV="${KABBALAH_VENV:-$HOME/.cache/kabbalah-add-content/venv}"
UV="$HOME/.local/bin/uv"
if [ ! -x "$UV" ]; then
  UV="$(command -v uv || true)"
fi
if [ -z "$UV" ]; then
  echo "error: uv not found (expected ~/.local/bin/uv). Install it: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 1
fi

if [ -x "$VENV/bin/python" ]; then
  echo "venv exists: $VENV" >&2
else
  mkdir -p "$(dirname "$VENV")"
  echo "creating venv: $VENV (python 3.12)" >&2
  "$UV" venv --python 3.12 "$VENV" >&2
fi

if "$VENV/bin/python" -I -c "import mlx_whisper" >/dev/null 2>&1; then
  echo "mlx-whisper already installed" >&2
else
  echo "installing mlx-whisper into $VENV" >&2
  VIRTUAL_ENV="$VENV" "$UV" pip install --python "$VENV/bin/python" mlx-whisper >&2
  "$VENV/bin/python" -I -c "import mlx_whisper" >/dev/null
fi

if ! command -v yt-dlp >/dev/null 2>&1 && [ ! -x "$HOME/.local/bin/yt-dlp" ]; then
  echo "warning: yt-dlp not found on PATH or in ~/.local/bin (needed by fetch_meta.py and transcribe.py)" >&2
fi
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "warning: ffmpeg not found on PATH (mlx-whisper needs it to decode audio)" >&2
fi

echo "$VENV/bin/python"
