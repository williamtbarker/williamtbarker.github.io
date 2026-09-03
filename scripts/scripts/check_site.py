#!/usr/bin/env python3
"""Dependency-free structural checks for the static portfolio."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = (ROOT / "index.html", ROOT / "404.html")


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[tuple[Path, str]] = []
        self.has_title = False
        self.has_description = False
        self.current_file = Path()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if element_id := values.get("id"):
            if element_id in self.ids:
                raise AssertionError(f"duplicate id #{element_id} in {self.current_file.name}")
            self.ids.add(element_id)
        if tag == "title":
            self.has_title = True
        if tag == "meta" and values.get("name") == "description":
            self.has_description = bool(values.get("content"))
        for attr in ("href", "src"):
            if target := values.get(attr):
                self.links.append((self.current_file, target))


def check() -> None:
    parser = SiteParser()
    for html_file in HTML_FILES:
        assert html_file.exists(), f"missing {html_file.name}"
        parser.current_file = html_file
        parser.feed(html_file.read_text(encoding="utf-8"))

    assert parser.has_title, "missing page title"
    assert parser.has_description, "index.html is missing a meta description"

    required_ids = {"main", "top", "work", "advisory", "fiction", "about", "contact"}
    missing_ids = required_ids - parser.ids
    assert not missing_ids, f"missing required section ids: {sorted(missing_ids)}"

    for source, target in parser.links:
        parsed = urlparse(target)
        if parsed.scheme in {"http", "https", "mailto"} or target.startswith("#"):
            continue
        local_target = target.split("#", 1)[0].split("?", 1)[0]
        if not local_target or local_target == "/":
            continue
        local_path = ROOT / local_target.lstrip("/")
        assert local_path.exists(), f"broken local link in {source.name}: {target}"

    checked_extensions = {".html", ".css", ".js", ".md", ".txt", ".xml"}
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix in checked_extensions:
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                assert line == line.rstrip(), f"trailing whitespace: {path.relative_to(ROOT)}:{line_number}"

    print(
        f"PASS: {len(HTML_FILES)} HTML pages parsed; "
        "local assets, required anchors, and whitespace verified"
    )


if __name__ == "__main__":
    check()
