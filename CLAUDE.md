# CLAUDE.md
Do not list Claude as a co-author when pushing code to GitHub.
Dahai Yu's academic homepage: al-folio v1.x, deployed to GitHub Pages by GitHub Actions only. **No local build, no Ruby installed** — a change is verified by the `Check` run (any branch / PR) or `Deploy site` (push to `main`) and the live page. The theme lives entirely in the `al_folio_*` gems (exact-pinned; Dependabot bumps them). There is no upstream remote. al-folio's dev scaffolding (docs, Docker, npm/purgecss, `bin/`, 22 CI workflows, `serve.sh`) was removed on purpose — don't bring it back, and ignore upstream contributor docs; they describe the starter repo.

To read a gem's real templates without Ruby:

```bash
curl -sO https://rubygems.org/downloads/al_folio_core-1.0.15.gem   # version from Gemfile.lock
tar xf al_folio_core-1.0.15.gem && tar xzf data.tar.gz             # -> _sass/ _layouts/ _includes/
```

## Config is trimmed to what renders

`plugins:` in `_config.yml` and the `Gemfile` must list the same gems (one in only one list is inert; `tools/check.py` enforces it). Transitive deps (`css_parser`, `observer`) are not listed. When editing the `Gemfile`, keep `Gemfile.lock`'s `DEPENDENCIES` in step — CI installs in frozen mode.

Looks removable, isn't:

| Item | Why it stays |
| --- | --- |
| `jekyll-toc` | `post.liquid` calls `{% toc %}` unconditionally |
| `al_citations` | same, from `selected_papers.liquid` |
| `jemoji` | `news.liquid` pipes through `emojify` |
| `jekyll-email-protect` | `al_search` pipes the email through `encode_email`; without the gem Liquid drops the filter silently and the email ships as plaintext in the search index |
| `al_folio.distill.source` | `al_folio_core` warns without it |
| `enable_publication_thumbnails: true` | gates the whole left column of `bib.liquid`: venue badge *and* thumbnail |
| `google_site_verification` | Search Console re-checks it; removing it un-verifies the property and drops the sitemap submission. Token must come from a **URL-prefix** property verified by **HTML tag** (a Domain property needs DNS on github.io, which we don't control) |

Deliberately off — to re-enable, restore every piece listed:

- **Math**: `enable_math: true`, `al_math` in both lists, `mathjax` in `third_party_libraries`.
- **Other CDN libraries**: `third_party_libraries` lists only the six this site can request. The rest are gated on page flags no page sets or on gems not loaded (`al_charts`, `al_cookie`, `al_analytics`, `al_folio_distill`).
- **RSS**: `jekyll-feed` in both lists + uncomment `rss_icon` in `_data/socials.yml`.
- **X/Twitter**: removed from `metadata.liquid` and `socials.yml`; no X presence.

## The seven local theme files

Each gem copy keeps the gem's text verbatim apart from edits marked `Local change:`, so a theme upgrade stays diffable. Prefer `_config.yml` or content over adding an eighth.

- `_includes/metadata.liquid` — appends `tagline` to the home `<title>`; renders `google_site_verification`; drops the Twitter card and `x_username` sameAs case; guards the gem's `null` in `sameAs`; fixes invalid JSON-LD `description`; emits a schema.org `ProfilePage`/`Person` (from `person:` in `_config.yml`) on `/` only.
- `_layouts/about.liquid` — portrait alt from `page.profile.image_alt`; capitalised section headings.
- `_sass/_footer.scss` — flex body to full viewport height so the footer sits at the bottom of short pages.
- `assets/css/main.scss` — the gem's entry file, minus the `tabs`/`teachings`/`typograms` partials, plus a trailing `@use "local"`.
- `_sass/_local.scss` — our CSS: FSU garnet accent (`#782f40` light, `#c96a80` dark) on `--global-theme-color`/`--global-hover-color`; dark-mode fix for the `/publications/` filter box; bold own name in author lists; the **1rem reading floor**.
- `_plugins/social_link_labels.rb` — real labels + `aria-label` for navbar social icons (jekyll-socials derives "Github username" etc. from the key). Add to `LABELS` when adding a social with an ugly key.
- `_plugins/prune_theme_assets.rb` — deletes ~350 KB of theme assets no page requests (`exclude:` can't; the theme-assets reader ignores it). Not `jupyter_new_tab.js`: `scripts.liquid` loads it on every page.

Sass gotchas:

- **Shadowing `_sass/_variables.scss` does not work.** Dart Sass resolves `@use` relative to the importing file first, so the gem's `_themes.scss` always gets the gem's copy. Only partials `@use`d directly by `assets/css/main.scss` can be shadowed.
- `al-folio-cv.css` loads *after* `main.css`, so a `/cv/` rule needs a `.cv` prefix to win on specificity. The CV `<h6>`s have an inline font-size, hence one `!important`.
- The 1rem floor exempts badges, icons, monospace and the footer. The footer is a hard constraint: the copyright line is 912px at 1rem vs 900px available, so it only fits at the gem's 0.9rem — re-measure before editing `footer_text`.

Compile the CSS locally (output is byte-identical to the deploy's apart from `$max-content-width`):

```bash
cd "$(mktemp -d)" && curl -sO https://rubygems.org/downloads/al_folio_core-1.0.15.gem
tar xf al_folio_core-1.0.15.gem && tar xzf data.tar.gz
python3 -c "s=open('REPO/assets/css/main.scss').read().split('---',2)[2]; open('entry.scss','w').write(s.replace('{{ site.max_width | default:  \"930px\" }}','930px'))"
npx --yes sass@1 --style=compressed --no-source-map --load-path=REPO/_sass --load-path=_sass entry.scss out.css
```

Measure whether text fits on one line: fetch Roboto 300's TTF from `https://fonts.googleapis.com/css?family=Roboto:300`, then `PIL.ImageFont.truetype(ttf, 14.4*64).getlength(text)/64` vs 900px (PIL skips kerning, so it errs wide — the safe direction).

Known gap: the `/cv/` header PDF icon has no accessible name; it lives in `al_folio_cv`'s 389-line `render.liquid`, not worth shadowing. The navbar's labelled `cv_pdf` link reaches the same file.

## Content

| Change | File |
| --- | --- |
| Bio, photo, blurbs | `_pages/about.md` |
| Publications | `_bibliography/papers.bib` (`selected={true}` → home page) |
| News | `_news/YYYY-MM-DD-slug.md` |
| CV | `_data/cv.yml` (rendercv) + `assets/pdf/dahai_yu_cv.pdf` |
| Socials / coauthors / badge colours | `_data/socials.yml` / `coauthors.yml` / `venues.yml` |
| Site metadata, flags | `_config.yml` |

- Page titles are Capitalised (`About`, `Publications`, `News`, `CV`): `title` is both navbar label and `<h1>`. Navbar order is `nav_order` in `_pages/`.
- `/publications/` builds its year jump nav by capturing `{% bibliography %}` and adding ids with `regex_replace` — nothing to maintain per year. Per-entry anchors (`#yu2026trustenergy`) come from the gem; `about.md` links to them.
- Venue badges are white text on the colour, so each colour needs ~5:1 against white. `arXiv` is a badge, not a venue: every entry without a DOI is a preprint, and its `note` carries the status.
- `assets/tex/cv.tex` is the PDF's LaTeX source and is published as-is, by choice.

### Publication metadata

Verified against Crossref, DBLP and the arXiv API; abstracts are the authors' own.

- Published paper: `doi` + `html` (publisher page: AAAI OJS, ACM DL, ijcai.org), preprint kept only as `arxiv`. **Never add a second entry for the preprint.**
- `note` = track / status line ("To appear.", "Submitted to AAAI 2027.").
- Only claim pages, volumes and author lists you can source. GeoGen (`10.1609/aaai.v40i2.37111`) is deliberately absent: the published author list doesn't include Dahai Yu, even though DBLP and Scholar do.
- `yan2026fusiontransnet` is under review, sourced only from the CV PDF; its `year` is the revision round.
- New custom bib fields must go in `filtered_bibtex_keywords` or they show in the BibTeX popup.

### Thumbnails

`preview = {<name>.png}` → `assets/img/publication_preview/`, on every entry but `yan2026fusiontransnet` (no public PDF). 800px wide, landscape, cropped to the figure's bounding box without caption. Source is the paper's framework figure from the camera-ready PDF (arXiv where ACM DL 403s). To redo one: crop the union of image/drawing rects above the caption, with the bottom at `caption.y0 - 2`. Exceptions: `hu2026ensf` uses a forecast plot (no architecture figure); `yu2023citation` uses the method flow chart (its model figure is portrait). `bib.liquid` uses the file name as `alt`, so name files by project.

### The CV PDF is the authority

Where `assets/pdf/dahai_yu_cv.pdf` and the site disagree, the PDF wins (email `dahai.yu@fsu.edu`, PKU degree "B.S. in Big Data Management and Application", awards, internship, skills, publication list). Re-check these whenever it is regenerated. The phone number is in the PDF and `cv.tex` but not in any page — Dahai's call.

## Findability

`description` leads with the full name (it is the search snippet); `tagline` is appended to the home `<title>`; `person:` feeds the `ProfilePage` JSON-LD. The rest is off-site: the homepage URL on Scholar, ORCID, GitHub, LinkedIn, the FSU people page and the lab page, and `/sitemap.xml` submitted in Search Console.

## Checks

`python3 tools/check.py` (needs PyYAML; skips YAML parsing without it) checks conventions that live in two places at once: plugin lists, `abbr` vs `venues.yml`, `preview` files and their size/aspect, custom bib fields vs `filtered_bibtex_keywords`, `about.md` anchors vs citekeys, the email and `cv_pdf` across files, `nav_order` collisions, `_news` filename vs date, `tools/` in `exclude:`, font sizes below 1rem in our CSS (`FONT_FLOOR_EXCEPTIONS` is the escape hatch), the Ruby pin shared by both workflows, and the local overrides' `Local change:` markers.

**When you add a convention that must hold in two files, add a check for it.** Errors render wrong or fail; warnings will rot. CI (`ci.yml`) runs `--strict`; the deploy doesn't, so a warning never blocks publishing.

## Deploying

- Repo must be public, named `UFOdestiny.github.io` (`baseurl` empty), with Pages source = **GitHub Actions**. GitHub's own builder can't build this site (non-whitelisted gems); if the source reverts to a branch, fix the setting — **not** with `.nojekyll`, which would publish raw source.
- Both workflows pin Ruby `4.0` (older RubyGems can't parse the libc-qualified `PLATFORMS` in `Gemfile.lock`) and install ImageMagick for responsive images. `check.py` asserts the pins match.
