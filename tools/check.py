#!/usr/bin/env python3
"""Consistency checks for this site, runnable without a Ruby toolchain.

There is no local Jekyll build (see CLAUDE.md), so a mistake in the content or in
one of the paired config lists is otherwise only caught by the `Deploy site` run.
This catches the classes of mistake that a build would *not* catch anyway --
a plugin listed in only one of the two lists, a `preview` pointing at a missing
file, an anchor in about.md that no longer names a bib entry -- plus the YAML
syntax errors that a build catches slowly.

    python3 tools/check.py            # errors and warnings
    python3 tools/check.py --strict   # treat warnings as errors too

Exit status is non-zero when there is anything to fix. Add a check here whenever
you add a convention that lives in two places.
"""

from __future__ import annotations

import argparse
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ERRORS: list[str] = []
WARNINGS: list[str] = []


def error(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# YAML
# --------------------------------------------------------------------------- #

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - depends on the environment
    yaml = None


def load_yaml(text: str, label: str):
    """Parse YAML, reporting the failure against `label`.

    Returns None when the content could not be parsed (or PyYAML is missing).
    Every caller treats None as "unknown" and skips the checks that read it --
    one syntax error should report itself once, not as a cascade of everything
    that file was supposed to contain.
    """
    if yaml is None:
        return None
    try:
        return yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        error(f"{label}: invalid YAML -- {str(exc).splitlines()[0]}")
        return None


FRONT_MATTER = re.compile(r"\A---\n(.*?)\n?---\s*\n?", re.DOTALL)


def front_matter(path: Path):
    """The front matter of a content file, parsed. None when there is none."""
    match = FRONT_MATTER.match(read(path))
    if not match:
        error(f"{rel(path)}: no front matter (a `---` fenced block at the top)")
        return None
    return load_yaml(match.group(1), rel(path))


def unknown(value) -> bool:
    """True when a file could not be parsed, so checks over it must be skipped."""
    return value is None


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


# --------------------------------------------------------------------------- #
# BibTeX
# --------------------------------------------------------------------------- #

# Fields that are bibliography data. Anything else in an entry is an al-folio
# field and has to be in `filtered_bibtex_keywords` or it shows up in the BibTeX
# popup on /publications/.
STANDARD_BIBTEX_FIELDS = {
    "address", "annote", "author", "booktitle", "chapter", "crossref", "doi",
    "edition", "editor", "howpublished", "institution", "journal", "key",
    "month", "note", "number", "organization", "pages", "publisher", "school",
    "series", "title", "type", "url", "volume", "year",
}


class Entry:
    def __init__(self, kind: str, key: str, body: str, line: int):
        self.kind = kind
        self.key = key
        self.line = line
        self.fields = parse_fields(body)


def parse_fields(body: str) -> dict[str, str]:
    """Split an entry body into field -> value, brace-aware."""
    fields: dict[str, str] = {}
    for match in re.finditer(r"(?m)^\s*([A-Za-z_-]+)\s*=\s*", body):
        name = match.group(1).lower()
        rest = body[match.end():]
        if rest.startswith("{"):
            depth, end = 0, None
            for i, ch in enumerate(rest):
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        end = i
                        break
            value = rest[1:end] if end is not None else rest
        else:  # a @string reference or a bare number
            value = rest.split(",", 1)[0]
        fields[name] = " ".join(value.split())
    return fields


def parse_bib(path: Path) -> list[Entry]:
    text = read(path)
    entries: list[Entry] = []
    for match in re.finditer(r"(?m)^@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        kind = match.group(1).lower()
        if kind in ("string", "preamble", "comment"):
            continue
        depth, end = 0, None
        for i in range(match.start(), len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i
                    break
        if end is None:
            error(f"{rel(path)}: entry `{match.group(2)}` has unbalanced braces")
            continue
        line = text.count("\n", 0, match.start()) + 1
        entries.append(Entry(kind, match.group(2), text[match.end():end], line))
    return entries


# --------------------------------------------------------------------------- #
# PNG
# --------------------------------------------------------------------------- #

def png_size(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", header[16:24])


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #

def check_yaml_files() -> dict:
    """Parse every YAML file and front matter. Returns the parsed data files."""
    if yaml is None:
        warn("PyYAML is not installed, so YAML syntax is unchecked "
             "(`python3 -m pip install --user pyyaml`)")
    data = {}
    for path in sorted((ROOT / "_data").glob("*.yml")):
        data[path.stem] = load_yaml(read(path), rel(path))
    config = load_yaml(read(ROOT / "_config.yml"), "_config.yml")
    for path in sorted((ROOT / "_pages").glob("*.md")):
        front_matter(path)
    for path in sorted((ROOT / "_news").glob("*.md")):
        front_matter(path)
    # The workflows are the only thing that ever builds this site, so a typo in
    # one of them is not something to discover from a run that never started.
    for path in sorted((ROOT / ".github").rglob("*.yml")):
        load_yaml(read(path), rel(path))
    return {"data": data, "config": config}


def check_plugin_lists(config: dict) -> None:
    """`plugins:` in _config.yml and the Gemfile must name the same set.

    A plugin in only one of the two is inert, and nothing in the build says so.
    """
    if unknown(config) or not config:
        return
    # `jekyll/scholar` is how the gem `jekyll-scholar` is required.
    configured = {str(p).replace("/", "-") for p in config.get("plugins") or []}

    gemfile = read(ROOT / "Gemfile")
    declared: set[str] = set()
    group = None
    for raw in gemfile.splitlines():
        line = raw.split("#", 1)[0].strip()
        if line.startswith("group "):
            group = line
        elif line == "end":
            group = None
        elif line.startswith("gem ") and group and "other_plugins" not in group:
            declared.add(re.sub(r"^gem\s+['\"]([^'\"]+)['\"].*", r"\1", line))

    for name in sorted(configured - declared):
        error(f"_config.yml lists plugin `{name}` but the Gemfile has no such gem "
              f"-- the build will fail to load it")
    for name in sorted(declared - configured):
        error(f"Gemfile has gem `{name}` but `plugins:` in _config.yml does not "
              f"list it -- it is installed but inert")

    # Jekyll copies any top-level directory it does not recognise straight into
    # _site, so a dev directory has to be excluded or it is published.
    excluded = {str(x) for x in (config.get("exclude") or [])}
    for name in ("tools",):
        if (ROOT / name).is_dir() and name not in excluded:
            error(f"_config.yml: `{name}/` is not in `exclude:`, so the build "
                  f"publishes it at /{name}/")

    theme = config.get("theme")
    if theme and theme not in declared:
        error(f"_config.yml `theme: {theme}` is not a gem in the Gemfile")


def check_bibliography(config: dict, data: dict) -> None:
    entries = parse_bib(ROOT / "_bibliography" / "papers.bib")
    if not entries:
        error("_bibliography/papers.bib: no entries parsed")
        return

    seen: dict[str, int] = {}
    for entry in entries:
        if entry.key in seen:
            error(f"papers.bib:{entry.line}: duplicate citekey `{entry.key}` "
                  f"(also at line {seen[entry.key]})")
        seen[entry.key] = entry.line

    venues = data.get("venues")
    filtered = None
    if not unknown(config):
        filtered = {str(k) for k in (config.get("filtered_bibtex_keywords") or [])}
    preview_dir = ROOT / "assets" / "img" / "publication_preview"
    referenced_previews: set[str] = set()
    used_abbrs: set[str] = set()
    used_custom: set[str] = set()

    for entry in entries:
        where = f"papers.bib:{entry.line} ({entry.key})"

        for name in entry.fields:
            if name not in STANDARD_BIBTEX_FIELDS:
                used_custom.add(name)
                if filtered is not None and name not in filtered:
                    error(f"{where}: field `{name}` is not in "
                          f"`filtered_bibtex_keywords` -- it will show up in the "
                          f"BibTeX popup")

        abbr = entry.fields.get("abbr")
        if not abbr:
            warn(f"{where}: no `abbr`, so the entry renders without a venue badge")
        else:
            used_abbrs.add(abbr)
            if not unknown(venues) and abbr not in venues:
                error(f"{where}: `abbr = {{{abbr}}}` has no entry in "
                      f"_data/venues.yml, so the badge renders uncoloured")

        preview = entry.fields.get("preview")
        if preview:
            referenced_previews.add(preview)
            path = preview_dir / preview
            if not path.exists():
                error(f"{where}: `preview = {{{preview}}}` does not exist in "
                      f"assets/img/publication_preview/")
            else:
                size = png_size(path)
                if size is None:
                    warn(f"{where}: {preview} is not a PNG")
                else:
                    width, height = size
                    if width != 800:
                        warn(f"{where}: {preview} is {width}px wide; the others "
                             f"are 800px, so this row's image resolves differently")
                    if height > width:
                        warn(f"{where}: {preview} is portrait ({width}x{height}), "
                             f"which makes its row much taller than the rest -- "
                             f"crop a landscape figure instead (see CLAUDE.md)")

        # A published entry has doi/html, a preprint has arxiv (and says so in
        # `journal`). An entry with neither is under review, and `note` is the
        # only thing that can say so on the page.
        if not any(entry.fields.get(f) for f in ("doi", "html", "arxiv", "note")):
            error(f"{where}: no `doi`, `html`, `arxiv` or `note` -- the entry "
                  f"renders with nothing saying where it is or what its status is")

    if filtered is not None:
        for name in sorted(filtered - used_custom):
            warn(f"_config.yml: `filtered_bibtex_keywords` lists `{name}`, which "
                 f"no entry in papers.bib uses")

    if not unknown(venues):
        for name in sorted(set(venues) - used_abbrs):
            warn(f"_data/venues.yml: `{name}` matches no `abbr` in papers.bib")

    on_disk = {p.name for p in preview_dir.iterdir() if p.is_file()}
    for name in sorted(on_disk - referenced_previews):
        warn(f"assets/img/publication_preview/{name} is referenced by no entry "
             f"in papers.bib")

    check_about_anchors({e.key for e in entries})
    check_coauthors(entries, data)


def check_about_anchors(keys: set[str]) -> None:
    """Every /publications/#key link in about.md must name a real entry."""
    about = read(ROOT / "_pages" / "about.md")
    for anchor in sorted(set(re.findall(r"/publications/#([A-Za-z0-9_:-]+)", about))):
        if anchor.isdigit():  # a year jump nav target, not an entry
            continue
        if anchor not in keys:
            error(f"_pages/about.md: links to /publications/#{anchor}, which is "
                  f"not a citekey in papers.bib")


def check_coauthors(entries: list[Entry], data: dict) -> None:
    """Flag coauthors.yml keys that no longer appear in the bibliography."""
    coauthors = data.get("coauthors")
    if unknown(coauthors):
        return
    surnames: set[str] = set()
    for entry in entries:
        for author in entry.fields.get("author", "").split(" and "):
            if "," in author:
                surnames.add(author.split(",", 1)[0].strip().lower())
            elif author.strip():
                surnames.add(author.split()[-1].strip().lower())
    for key in sorted(coauthors):
        if key.lower() not in surnames:
            warn(f"_data/coauthors.yml: `{key}` is not an author surname in "
                 f"papers.bib")


def check_identity(data: dict) -> None:
    """The email and the CV PDF path each live in several files; keep them equal."""
    sources = {
        "_data/socials.yml": read(ROOT / "_data" / "socials.yml"),
        "_data/cv.yml": read(ROOT / "_data" / "cv.yml"),
        "_pages/about.md": read(ROOT / "_pages" / "about.md"),
    }
    found: dict[str, set[str]] = {}
    for label, text in sources.items():
        emails = set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", text))
        if emails:
            found[label] = emails
    everything = set().union(*found.values()) if found else set()
    if len(everything) > 1:
        listing = "; ".join(f"{k}: {', '.join(sorted(v))}" for k, v in found.items())
        error(f"the email address differs between files ({listing}) -- "
              f"assets/pdf/dahai_yu_cv.pdf is the authority")

    socials = data.get("socials")
    pdf = None if unknown(socials) else socials.get("cv_pdf")
    if pdf:
        if not (ROOT / pdf.lstrip("/")).exists():
            error(f"_data/socials.yml: `cv_pdf: {pdf}` does not exist")
        cv_page = front_matter(ROOT / "_pages" / "cv.md")
        if cv_page and cv_page.get("cv_pdf") and cv_page["cv_pdf"] != pdf:
            error(f"_pages/cv.md `cv_pdf: {cv_page['cv_pdf']}` and "
                  f"_data/socials.yml `cv_pdf: {pdf}` point at different files")


def check_pages() -> None:
    """Navbar order comes from front matter; two pages sharing a slot is ambiguous."""
    orders: dict[int, str] = {}
    for path in sorted((ROOT / "_pages").glob("*.md")):
        matter = front_matter(path)
        if matter is None or not matter.get("nav"):
            continue
        order = matter.get("nav_order")
        if order is None:
            warn(f"{rel(path)}: `nav: true` without `nav_order`, so its place in "
                 f"the navbar is arbitrary")
        elif order in orders:
            error(f"{rel(path)}: `nav_order: {order}` is also used by "
                  f"{orders[order]}")
        else:
            orders[order] = rel(path)


def check_news() -> None:
    """The filename date is what orders /news/; the front matter date is displayed."""
    for path in sorted((ROOT / "_news").glob("*.md")):
        match = re.match(r"(\d{4}-\d{2}-\d{2})-", path.name)
        if not match:
            error(f"{rel(path)}: filename must start with YYYY-MM-DD- or the "
                  f"collection will not pick it up")
            continue
        matter = front_matter(path)
        if matter is None:
            continue
        date = matter.get("date")
        if date is None:
            error(f"{rel(path)}: no `date` in the front matter")
            continue
        if not str(date).startswith(match.group(1)):
            error(f"{rel(path)}: front matter date {date} disagrees with the "
                  f"filename date {match.group(1)}")


# Our own CSS holds a floor: nothing a reader reads as prose goes below 1rem,
# the size of the home page subtitle (`<p class="desc">`, unstyled, so it
# inherits the body). See the section at the end of _sass/_local.scss.
READING_FONT_FLOOR_REM = 1.0

# Sizes below the floor that are deliberate. Keyed by the source line itself
# rather than a line number, so it survives the file being reordered:
#   "_sass/_local.scss|font-size: 0.75rem;": "the venue badge is a label"
FONT_FLOOR_EXCEPTIONS: dict[str, str] = {}


def check_font_sizes() -> None:
    """Flag a font-size below the floor in a file we wrote.

    The gem is full of 0.7-0.9rem text and _sass/_local.scss raises the parts of
    it this site actually renders. This is what keeps a later addition of ours
    from quietly reintroducing the thing we just fixed.
    """
    # Only files whose CSS is ours to choose. `_sass/_footer.scss` and
    # `assets/css/main.scss` are gem content kept verbatim (the point of those
    # two shadows is that a theme upgrade stays diffable), so their 0.75rem and
    # 0.9rem are not ours to raise -- `_local.scss` overrides the one that
    # renders instead.
    files = [
        ROOT / "_sass" / "_local.scss",
        *sorted((ROOT / "_pages").glob("*.md")),
    ]
    for path in files:
        if not path.exists():
            continue
        for number, line in enumerate(read(path).splitlines(), start=1):
            code = line.split("//", 1)[0]
            if "*" in code:  # inside a /* */ comment block
                continue
            match = re.search(r"font-size:\s*([\d.]+)(rem|px)", code)
            if not match:
                continue
            value = float(match.group(1))
            rem = value if match.group(2) == "rem" else value / 16
            if rem >= READING_FONT_FLOOR_REM:
                continue
            if f"{rel(path)}|{code.strip()}" in FONT_FLOOR_EXCEPTIONS:
                continue
            warn(f"{rel(path)}:{number}: font-size {match.group(1)}{match.group(2)} is below the "
                 f"{READING_FONT_FLOOR_REM}rem reading floor -- if it is a label "
                 f"rather than prose, add it to FONT_FLOOR_EXCEPTIONS with the "
                 f"reason")


def check_workflows() -> None:
    """The two workflows build the same site, so they must build it the same way.

    deploy.yml and ci.yml each set up Ruby and ImageMagick themselves (a
    reusable workflow for four lines would be worse), which makes the Ruby pin a
    second list to keep in sync -- exactly the kind of thing this script exists
    to watch. The pin matters: an older RubyGems cannot read the libc-qualified
    platform names in Gemfile.lock.
    """
    workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    pins: dict[str, str] = {}
    runs_check: list[str] = []
    for path in workflows:
        text = read(path)
        found = re.findall(r'ruby-version:\s*"?([\d.]+)"?', text)
        if found:
            pins[rel(path)] = found[0]
        if "tools/check.py" in text:
            runs_check.append(rel(path))

    if len(set(pins.values())) > 1:
        listing = "; ".join(f"{k}: {v}" for k, v in sorted(pins.items()))
        error(f"the workflows pin different Ruby versions ({listing}) -- CI would "
              f"then build the site differently from the deploy")

    for path in workflows:
        text = read(path)
        if "bundle exec jekyll build" in text and rel(path) not in runs_check:
            warn(f"{rel(path)} builds the site but never runs tools/check.py, so "
                 f"whatever it builds is unchecked")


def check_local_overrides() -> None:
    """The seven local files exist and each says what is local about it.

    That marker is the whole upgrade story: without it, a later reader cannot
    tell our edit from the gem's own lines.
    """
    marker = re.compile(r"local (change|override|addition|partial)", re.IGNORECASE)
    overrides = [
        "_includes/metadata.liquid",
        "_layouts/about.liquid",
        "_sass/_footer.scss",
        "_sass/_local.scss",
        "assets/css/main.scss",
    ]
    # Wholly ours, so there is nothing local to mark -- only their presence is
    # checked, because CLAUDE.md documents each one.
    own_files = [
        "_plugins/social_link_labels.rb",
        "_plugins/prune_theme_assets.rb",
    ]
    for name in own_files:
        if not (ROOT / name).exists():
            warn(f"{name} is listed in CLAUDE.md as a local file but is gone -- "
                 f"remove it from CLAUDE.md too")
    for name in overrides:
        path = ROOT / name
        if not path.exists():
            warn(f"{name} is listed in CLAUDE.md as a local file but is gone -- "
                 f"remove it from CLAUDE.md too")
        elif not marker.search(read(path)):
            warn(f"{name} overrides or prunes the theme but says nowhere what is "
                 f"local about it -- keep a `Local change:` style marker at the edit")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true",
                        help="exit non-zero on warnings as well as errors")
    args = parser.parse_args()

    parsed = check_yaml_files()
    config, data = parsed["config"], parsed["data"]
    check_plugin_lists(config)
    check_bibliography(config, data)
    check_identity(data)
    check_pages()
    check_news()
    check_font_sizes()
    check_workflows()
    check_local_overrides()

    for msg in WARNINGS:
        print(f"warning: {msg}")
    for msg in ERRORS:
        print(f"error: {msg}")

    if ERRORS:
        print(f"\n{len(ERRORS)} error(s), {len(WARNINGS)} warning(s)")
        return 1
    if WARNINGS and args.strict:
        print(f"\n{len(WARNINGS)} warning(s), treated as errors by --strict")
        return 1
    print(f"all checks passed ({len(WARNINGS)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
