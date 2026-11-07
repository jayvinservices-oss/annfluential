"""Manual mode: you generate clips in a web app and drop the files into clips/<slug>/."""
from __future__ import annotations

from .base import Provider


class ManualProvider(Provider):
    name = "manual"
    creates_files = False

    def __init__(self, cfg: dict):
        self.cfg = cfg

    def generate(self, *, prompt, negative, image, seconds, out):
        return {"provider": self.name, "expected_file": str(out)}
