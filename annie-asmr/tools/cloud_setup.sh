#!/usr/bin/env bash
# Rebuild the free voice engine in a fresh cloud session (about 10 minutes, ~11 GB of disk).
# Needs network access to pypi.org, huggingface.co and *.hf.co.
set -euo pipefail
ENV=${VOXCPM_ENV:-/home/user/voice-env}
if [ ! -x "$ENV/bin/python" ]; then
  uv venv -q "$ENV" --python 3.12
  VIRTUAL_ENV="$ENV" uv pip install -q voxcpm soundfile
fi
"$ENV/bin/python" - <<'PY'
from huggingface_hub import snapshot_download
print("model at", snapshot_download("openbmb/VoxCPM2"))
PY
pip install -q --break-system-packages -r "$(dirname "$0")/../requirements.txt" || true
echo "Voice engine ready: $ENV/bin/python"
