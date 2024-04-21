from __future__ import annotations

import os
import time


class source_file:
    __slots__ = ("filename", "modified", "last_size")

    def __init__(self, filename: str) -> None:
        self.filename = os.path.abspath(filename)
        self.modified = self.get_last_modified()
        self.last_size = os.path.getsize(filename)

    def get_last_modified(self) -> str:
        return time.ctime(os.path.getmtime(self.filename))

    def was_updated(self) -> bool:
        t = self.get_last_modified()
        if t > self.modified:
            self.modified = t
            return True
        return False

    def get_base_name(self) -> str:
        return os.path.basename(self.filename)

    def get_directory(self) -> str:
        return os.path.dirname(self.filename)

    def get_text(self, only_new_text: bool = False) -> str:
        text = ""
        while not text:
            with open(self.filename, encoding="utf-8") as content_file:
                if only_new_text:
                    content_file.seek(self.last_size)
                text = content_file.read()

            time.sleep(0.1)

        self.last_size = os.path.getsize(self.filename)
        return text
