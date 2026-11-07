from __future__ import annotations

import base64
import mimetypes
import time
from pathlib import Path

import requests


class Provider:
    name = "base"
    #: manual provider does not create files itself
    creates_files = True

    def generate(self, *, prompt: str, negative: str, image: Path | None, seconds: int, out: Path) -> dict:
        raise NotImplementedError


def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def download(url: str, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".part")
    with requests.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        with tmp.open("wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    tmp.rename(out)


def poll(fetch, *, done, failed, every: float = 5, timeout: float = 1800):
    """Call fetch() until done(result) or failed(result). Returns the final result."""
    start = time.time()
    while True:
        result = fetch()
        if done(result):
            return result
        if failed(result):
            raise RuntimeError(f"Generation failed: {result}")
        if time.time() - start > timeout:
            raise TimeoutError("Generation took too long; it may still finish on the provider's site.")
        time.sleep(every)
