# CLAUDE.md

Dahai Yu's personal academic homepage — al-folio v1.x, deployed to GitHub Pages.
53 tracked files: content (15 of them publication thumbnails), one build
workflow, seven local theme files. The theme runtime lives entirely in the
`al_folio_*` gems; upgrade with `bundle update`, never by merging an upstream
remote (there isn't one).

`_config.yml` and the `Gemfile` were trimmed to only what this site renders, and
the two `plugins`/gem lists must stay in sync — a plugin in only one list is
inert. Judge a change of that kind by what the build emits, not by reading
templates — and there is no local toolchain to build with (see
**Building and deploying**), so that means the `Deploy site` run and the live
page. To read a gem's actual templates without a Ruby install:

```bash
curl -sO https://rubygems.org/downloads/al_folio_core-1.0.15.gem   # version from Gemfile.lock
tar xf al_folio_core-1.0.15.gem && tar xzf data.tar.gz             # -> _sass/ _layouts/ _includes/
```

## Things that look removable but aren't

| Item | Why it stays |
| --- | --- |
| `jekyll-toc` | `post.liquid` calls its tag unconditionally |
| `al_citations` | same, from `selected_papers.liquid` |
| `al_folio.distill.source` key | `al_folio_core` warns without it |
| `jekyll-email-protect` | `al_search`'s `search-data.liquid.js` pipes the address through `encode_email`; Liquid drops an unknown filter silently, so removing the gem ships the email as plaintext in the search index with no error |
| `enable_publication_thumbnails: true` | despite the name it gates the whole left column of `bib.liquid` — both the venue badge coloured by `_data/venues.yml` and the `preview` thumbnail |

Badge colours in `_data/venues.yml` are a background with white text
(`_layouts/bib.liquid` + `_sass/_publications.scss`), so each one needs ~5:1
against white; they all sit there deliberately. `arXiv` is a badge but not a
venue — every entry without a DOI is a preprint, and its `note` carries the
status line.

`enable_math` is **off**: no `$`/`$$` in `_pages`, `_news`, or `papers.bib`, so
`al_math` is out of both lists and `mathjax` out of `third_party_libraries` —
that keeps a ~1 MB bundle off every page. To write math again, restore all three
plus `enable_math: true`.

`third_party_libraries` lists only the six CDN libraries this site can request
(fontawesome, academicons, google_fonts, tocbot, scholar-icons,
vanilla-back-to-top). Upstream's other ~20 are gated on page flags no page sets
(`page.map`, `page.code_diff`, `page.pretty_table`, `page.pseudocode`,
`page.tikzjax`, `enable_masonry`) or on gems not in `plugins` (`al_charts`,
`al_cookie`, `al_analytics`, `al_folio_distill`) — the `analytics:` block is gone
for the same reason. Re-enabling such a feature means restoring its entry too.

There is no RSS feed: `jekyll-feed` produced a `/feed.xml` nothing linked to,
because `rss_icon` is deliberately absent from `_data/socials.yml` (both gem
templates that would link the feed key off it). Re-adding means the gem, the
`plugins` entry, and uncommenting `rss_icon`.

## Local files that shadow or prune the theme

Each override carries a `Local change:` comment at the edit; keep the rest of the
file verbatim so a theme upgrade stays diffable. Prefer `_config.yml` and content
over adding an eighth.

- `_sass/_footer.scss` — flexes the body to full viewport height so the copyright
  line stays at the bottom on short pages (/news/, a single news item).
- `assets/css/main.scss` + `_sass/_local.scss` — our own CSS. The site accent, FSU
  garnet `#782f40` in light mode and `#c96a80` in dark: `_local.scss` is a
  partial of our own that redeclares `--global-theme-color` /
  `--global-hover-color` on the gem's own selectors (`:root` and
  `html[data-theme="dark"]`); the `main.scss` copy is the gem's 33 lines verbatim
  plus a trailing `@use "local"` so ours lands last and wins at equal
  specificity. That is what the accent feeds: links, venue badges, author
  underlines, the scroll progress bar, the back-to-top button, every hover state.
  The same file also repaints the `/publications/` filter box in dark mode: the
  gem styles it with the *newsletter* tokens, which are inverted on purpose
  (light card on a dark page), so on a site with no newsletter it was just a
  white rectangle.

  The same file also holds the site's **minimum reading size: 1rem**, the size
  of the home page subtitle (`<p class="desc">` in `_layouts/about.liquid`, a
  class the gem never styles, so it inherits the body: Roboto 300, 1rem). The
  theme puts a lot of prose at 0.7–0.9rem; the rules there raise the parts this
  site renders — the `/cv/` table of contents (0.8rem, the one that reads as
  broken), the `.post-description` line under each page title, a paper's
  abstract, the footer, and inside `/cv/` the location lines and the ten `<h6>`s
  the CV template sizes with an inline `style="font-size: 0.95rem"` (an inline
  declaration is why that one rule needs `!important`). Badges, icons and
  monospace stay small on purpose — the reasons are at each rule. Two things to
  know when adding to it: `al-folio-cv.css` is a *separate* stylesheet loaded
  after `main.css`, so a `/cv/` rule needs the `.cv` prefix to outrank the gem
  on specificity rather than on order; and `tools/check.py` warns about any new
  `font-size` below 1rem in `_sass/_local.scss` or `_pages/`, with
  `FONT_FLOOR_EXCEPTIONS` as the escape hatch.

  **Shadowing `_sass/_variables.scss` does not work** — it was tried first and
  the deployed CSS still came out magenta. Dart Sass resolves a `@use` relative
  to the importing file before it consults the load path, and the gem's
  `_themes.scss` (which is where every `--global-*` is assigned) says
  `@use "variables"`, so it always finds the gem's copy sitting next to it. The
  general rule: a gem partial can only be shadowed if `assets/css/main.scss`
  `@use`s it directly (that file is outside the gem's `_sass/`, so its lookups do
  fall through to the load path). That is why the `_footer.scss` shadow works and
  a `_variables.scss` one cannot. Whatever `main.scss` configures with
  `@use "variables" with (...)` is likewise a different module from the one every
  other partial sees.
- `_includes/metadata.liquid` — the gem's whole Twitter-card block and the
  `x_username` case in the schema.org `sameAs` loop are deleted; this site has no
  X presence. OpenGraph covers the same consumers, and
  `og_image: /assets/img/prof_pic.jpg` gives a shared link its thumbnail.
- `_layouts/about.liquid` — reads `page.profile.image_alt` for the portrait's alt
  text; the gem passes the file name, so a screen reader read "prof_pic.jpg".
- `_plugins/social_link_labels.rb` — relabels the navbar's social icons.
  jekyll-socials derives each tooltip from the `_data/socials.yml` key with
  `key.gsub('_',' ').capitalize` and has no config for it, so the icons read
  "Github username", "Orcid id", "Scholar userid", "Cv pdf". The plugin prepends a
  module over `Jekyll::SocialLinksTag#render` and rewrites those labels, and adds
  an `aria-label` to every icon — they are icon-only links with no text, so the
  tooltip is their only accessible name and `title` alone is not reliably
  announced. Add a key to `LABELS` when you add a social with an ugly key name.
- `_plugins/prune_theme_assets.rb` — deletes theme assets no page can request
  (three `jupyter*.css`, `typograms.js`, `table-engine.js`, `tabs.js`,
  `masonry.js`, `calendar-setup.js`, ~350 KB). `exclude:` cannot do this: the
  theme-assets reader walks the gem's `assets/` without consulting it.
  `jupyter_new_tab.js` is **not** on the list — `scripts.liquid` loads it on
  every page. `sass.sourcemap: never` drops `main.css.map` for the same reason.

Known gap: the PDF icon in the `/cv/` page header is an icon-only link with no
accessible name. It lives in `al_folio_cv`'s 389-line `templates/cv/render.liquid`
and shadowing all of that for one attribute is not worth the upgrade drift — the
navbar's own labelled `cv_pdf` link reaches the same file from every page.

Layout choices: `footer_fixed: false`, and `enable_navbar_social: true` with
`social: false` in `_pages/about.md`, so the social icons sit in the navbar.

al-folio's development scaffolding (`docs/`, `AGENTS.md`, `.agents/`, `bin/`,
Docker files, issue templates, the npm/purgecss step, 22 CI workflows) was
**removed on purpose**. Do not reintroduce it, and do not follow upstream
contributor docs found online — they describe the starter repo. In particular
`baseurl` is empty; upstream's `/al-folio` is about the template's demo site.

## Where content lives

| Change                       | File                                                  |
| ---------------------------- | ----------------------------------------------------- |
| Bio, profile photo, blurbs   | `_pages/about.md`                                     |
| Publications                 | `_bibliography/papers.bib` (`selected={true}` → home page) |
| News / announcements         | `_news/YYYY-MM-DD-slug.md`                            |
| CV                           | `_data/cv.yml` (rendercv format)                      |
| Social links                 | `_data/socials.yml`                                   |
| Coauthor homepages           | `_data/coauthors.yml`                                 |
| Venue badge colors           | `_data/venues.yml`                                    |
| Site metadata, feature flags | `_config.yml`                                         |

Page titles are Capitalised (`About`, `Publications`, `News`, `CV`) — al-folio
ships them lowercase, but `title` is both the navbar label and the page's `<h1>`,
and the two home page section headings in `_layouts/about.liquid` were capitalised
to match. Keep new pages consistent with that.

`_pages/publications.md`, `_pages/news.md` and `_pages/cv.md` are thin wrappers.
The navbar is built from `nav:` / `nav_order:` in `_pages/`; `about.md` has
neither, because it is the site root (`permalink: /`).

`/publications/` builds its year jump nav out of the bibliography itself:
jekyll-scholar renders each year group as a bare `<h2 class="bibliography">2026</h2>`
with no id and offers no config for one, so `_pages/publications.md` captures the
`{% bibliography %}` output, adds ids with `regex_replace`, then splits the same
string on the id marker to recover the year list. Nothing to maintain when a year
is added, and `/publications/#2025` works without JavaScript. Per-entry anchors
(`#yu2026trustenergy`) come from the gem and are what `_pages/about.md` links each
project name to.

## Publication thumbnails

Every entry except `yan2026fusiontransnet` (no public PDF) carries
`preview = {<shortname>.png}` → `assets/img/publication_preview/`. Each one is a
crop of that paper's own framework figure, taken from the camera-ready PDF where
one is reachable (AAAI OJS, ijcai.org, CEUR) and from arXiv otherwise — ACM DL
returns 403, so EnergyMamba, SynHAT and UQGNN come from arXiv. `hu2026ensf` is
the exception on content: that paper has no architecture figure at all, so its
thumbnail is one panel of its forecast-vs-truth plot.

All are 800 px wide PNGs, cropped to the figure's own bounding box with no
caption, and cropped to keep a landscape aspect: `yu2023citation`'s model figure
is a tall portrait diagram that made its row three times the height of every
other one, so that entry uses the paper's method flow chart instead.
`filtered_bibtex_keywords` must keep `preview` in it or the field shows up in the
BibTeX popup. To redo one: pull the PDF, find the caption block for the
figure, and crop the union of the image/drawing rects sitting above it — the
figure always ends immediately above its caption, so snapping the crop's bottom
to `caption.y0 - 2` is what keeps faded sub-panels from being clipped. Note that
`bib.liquid` passes the file name as the `alt` text, so the short project name is
the accessible name a screen reader reads.

## Publication metadata

`_bibliography/papers.bib` is verified against Crossref (DOIs, volume/issue,
pages), DBLP, and the arXiv API — abstracts are the authors' own, from arXiv.

- A published paper carries `doi` + `html` (prefer the publisher's page: AAAI OJS,
  ACM DL, ijcai.org) and keeps its preprint only as an `arxiv` field. **Never add
  a second entry for the preprint.**
- `note` holds a track/workshop/status line ("AI and Social Good Track",
  "To appear.", "Under minor revision.", "Submitted to AAAI 2027."); it renders
  under the venue.
- Only claim page numbers, volumes, and author lists you can source. GeoGen
  (`10.1609/aaai.v40i2.37111`) is deliberately absent: the published AAAI author
  list and arXiv v3 do not include Dahai Yu, even though DBLP and Scholar do.
- An entry under review has no DOI, publisher page or preprint, so its only source
  is the CV PDF. `yan2026fusiontransnet` is the one such entry; its `year` is the
  revision round, not a publication year.

## The CV PDF is the authority

`assets/pdf/dahai_yu_cv.pdf` is a real CV. Where it and the site disagreed, the
PDF won — that fixed the email (`dahai.yu@fsu.edu`, not `dy23a@`), the Peking
University degree ("B.S. in Big Data Management and Application"), the awards and
internship in `_data/cv.yml`, the LLM post-training skills row, and the missing
FusionTransNet entry in `papers.bib`. Re-check all of those whenever the PDF is
regenerated. One thing in the PDF is deliberately **not** on the site: the phone
number — adding it is Dahai's call, not a consistency fix.

## Being findable as "Dahai Yu"

The domain carries no name, so everything that ties this site to the person is in
the markup, and all of it is config-driven:

- `tagline` in `_config.yml` is appended to the home page's `<title>`, which the
  gem otherwise leaves as the bare name — a search for "dahai yu fsu" had nothing
  to match. `_includes/metadata.liquid` does that (local change); other pages keep
  the gem's "Page | Name".
- `description` leads with the full name, because it is both the meta description
  and the `og:description`, i.e. the snippet a search result shows.
- `person:` in `_config.yml` feeds a schema.org `ProfilePage` → `Person` block that
  `metadata.liquid` emits **on the site root only**: job title, affiliation with
  its URL, `alumniOf`, image, email, `knowsAbout`, and the same `sameAs` list as
  the gem's `WebSite` block. The gem's own block names the person only as a bare
  `author` string, which is too thin to associate this site with the Dahai Yu on
  Scholar / ORCID / DBLP. That `sameAs` list also used to start with a literal
  `null` (the gem pushes `social[1].url` unguarded, and `cv_pdf` is a plain
  string) — fixed in the same file.

What is left is off-site and cannot be done from this repo: the homepage URL has
to be on the Google Scholar profile, ORCID, GitHub profile, LinkedIn, the FSU CS
people page and the advisor's lab page, and the site has to be verified in Google
Search Console with `/sitemap.xml` submitted (`jekyll-sitemap` already generates
it). Inbound links from pages Google already trusts are what actually moves a
name query; the markup above only makes sure the right page wins once it is
crawled.

Search Console verification is `google_site_verification` in `_config.yml`, which
`_includes/metadata.liquid` renders as a `<meta>` in every page's head. **Do not
remove it** — Google re-checks the tag, and losing it un-verifies the property and
with it the `/sitemap.xml` submission. The token is per property *and* per method:
it has to come from a **URL prefix** property (`https://ufodestiny.github.io/`)
verified with "HTML tag". A "Domain" property is not usable here at all — it can
only be verified by a DNS TXT record on github.io, which is GitHub's domain, not
ours — and a token issued for DNS or for the HTML-file method will not verify in
the meta tag.

## Checks

`python3 tools/check.py` is the only thing here that can validate a change
without a Ruby toolchain, and it deliberately checks what a *build* would not:
conventions that live in two places at once. Today that is the
`plugins:`/`Gemfile` pair, `abbr` vs `_data/venues.yml`, `preview` vs the files
in `assets/img/publication_preview/` (including the 800px-wide/landscape rule),
custom bib fields vs `filtered_bibtex_keywords`, `about.md`'s
`/publications/#key` anchors vs the citekeys, the email across `socials.yml` /
`cv.yml` / `about.md`, `cv_pdf` across `socials.yml` / `cv.md`, `nav_order`
collisions, `_news` filename vs front-matter dates, the Ruby pin shared by the
two workflows, and the presence of the local overrides with their
`Local change:` markers. It also parses every YAML file and front matter, which
a build does catch — just slowly.

**When you add a convention that has to hold in two files, add a check for it.**
That is the whole point of the file; a comment in one of the two places is what
this repo already tried. Errors are things that render wrong or fail; warnings
are things that will rot. `--strict` fails on warnings and is what CI uses on a
branch or PR (`ci.yml`); the deploy runs it without `--strict`, because a
warning is not a reason to block publishing a correct site.

PyYAML is the one dependency (`python3 -m pip install --user pyyaml`); without
it the script still runs, skips YAML parsing, and says so.

## Building and deploying

Deployment is GitHub Actions only (`.github/workflows/deploy.yml`, push to
`main` → `upload-pages-artifact` + `deploy-pages`). Requirements: the repo is
public, named `UFOdestiny.github.io`, and Pages source is set to **GitHub
Actions**, not a branch — GitHub's own builder cannot build this site
(`jekyll-scholar` and the `al_folio_*` gems are not whitelisted). If the source
is ever set back to a branch, that built-in job fails on every push while
`Deploy site` still succeeds; the fix is the Pages setting, **not** a `.nojekyll`
file, which would publish raw source over the good deployment. CI Ruby is pinned
to `4.0` to match whatever wrote `Gemfile.lock`; older RubyGems cannot parse the
libc-qualified platform names (`x86_64-linux-gnu`) in `PLATFORMS`.

`ci.yml` is that same build without the deploy, on pull requests and on pushes
to any branch but `main`, so a change can be verified before it is live. Both
workflows set up Ruby and ImageMagick themselves rather than sharing a reusable
workflow for four lines, and `tools/check.py` asserts they pin the same Ruby.
Gem and action updates arrive as monthly Dependabot PRs
(`.github/dependabot.yml`) that `ci.yml` builds — the `al_folio_*` gems are
pinned to exact versions, so `bundle update` alone never moves them and nothing
else announces that a new one exists.

The stylesheet, at least, *can* be compiled locally without Ruby — dart-sass
via `npx` plus the gem tarball, which is how the 1rem floor above was verified
(each rule has to win the cascade, and two of them only win on specificity):

```bash
cd "$(mktemp -d)" && curl -sO https://rubygems.org/downloads/al_folio_core-1.0.15.gem
tar xf al_folio_core-1.0.15.gem && tar xzf data.tar.gz          # -> the gem's _sass/
python3 - <<'EOF'                                               # strip front matter + Liquid
s = open('/path/to/repo/assets/css/main.scss').read().split('---', 2)[2]
open('entry.scss', 'w').write(s.replace('{{ site.max_width | default:  "930px" }}', '930px'))
EOF
npx --yes sass@1 --style=compressed --no-source-map \
  --load-path=/path/to/repo/_sass --load-path=_sass entry.scss out.css
```

`out.css` is byte-for-byte what the deploy produces, apart from `$max-content-width`
being hardcoded. Diffing it against the live `/assets/css/main.css` is the fastest
way to see what a Sass change actually did.

There is no local build: `serve.sh` and its conda Ruby env were removed once the
env stopped existing, and no Ruby is installed. Every change is verified by the
Actions run. A local loop can be rebuilt if it is ever worth it — Ruby >= 3.2
(system Ruby 3.0.7 is too old for `Gemfile.lock`), `bundle config set --local
path vendor/bundle`, `bundle install`, `bundle exec jekyll serve`, plus
ImageMagick for the responsive-image pipeline.
