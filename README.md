# Dahai Yu — Personal Homepage

<https://ufodestiny.github.io>

Academic homepage built on the [al-folio](https://github.com/alshedivat/al-folio)
Jekyll theme. The whole repo is 53 files: content, one build workflow, and seven
small local files that override or prune the theme. Everything else — layouts,
styles, Liquid tags — comes from the `al_folio_*` gems declared in `Gemfile`, so
there is no theme source to maintain here. `CLAUDE.md` explains what each of the
seven does and why.

Edit a file, push to `main`, and GitHub Actions rebuilds and publishes the site.
Nothing has to be built locally.

Before pushing, `python3 tools/check.py` (a few seconds, no Ruby needed) checks
the conventions that live in two files at once — a plugin named in `_config.yml`
but not the `Gemfile`, a `preview` pointing at a missing image, an
`/publications/#key` link in `about.md` that no longer names an entry, the email
drifting between `socials.yml`, `cv.yml` and `about.md`. Pushing to a branch or
opening a pull request runs the same checks plus a full production build, so a
mistake shows up as a red PR instead of a red deploy.

## What to edit

| I want to…                       | Edit                                                        |
| -------------------------------- | ----------------------------------------------------------- |
| Change the bio / photo / blurbs  | `_pages/about.md`                                           |
| Add a paper                      | `_bibliography/papers.bib` — add `selected = {true}` to feature it on the home page |
| Post news                        | new file `_news/YYYY-MM-DD-slug.md`                         |
| Update the CV                    | `_data/cv.yml` + `assets/pdf/dahai_yu_cv.pdf`               |
| Add/remove a social link         | `_data/socials.yml`                                         |
| Link a coauthor's homepage       | `_data/coauthors.yml`                                       |
| Recolor a venue badge            | `_data/venues.yml`                                          |
| Site title, nav, feature flags   | `_config.yml`                                               |
| Colours, font sizes, CSS tweaks  | `_sass/_local.scss`                                         |

Navigation comes from the `nav:` / `nav_order:` front matter in `_pages/`:
publications (1), news (2), CV (3). `about.md` sets neither — it is the site root
(`permalink: /`) and the theme links it as the home entry.

`plugins:` in `_config.yml` and the `Gemfile` are two lists that must agree — a
plugin named in only one of them silently does nothing. Both lists are cut down
to what this site actually renders, so read `CLAUDE.md` before touching either.

## Deploying

The site is a GitHub *user* site, so the repo has to be named
`UFOdestiny.github.io` and `baseurl` stays empty. Two settings make it work:

- The repo must be **public** — Pages is free only on public repos.
- Settings → Pages → Source: **GitHub Actions**, not "Deploy from a branch"
  (there is no `gh-pages` branch). On "Deploy from a branch" GitHub also runs its
  own builder, which cannot build this site: the site still deploys, but every
  push shows an extra failed "pages build and deployment".

`.github/workflows/deploy.yml` then builds on every push to `main` and hands
`_site/` to Pages' deployment API. GitHub Pages cannot build this site itself —
it whitelists only the `github-pages` gem's plugins, not `jekyll-scholar` or the
`al_folio_*` gems.

To move to a custom domain later, add a `CNAME` file with the domain, change
`url:`, and point DNS at GitHub Pages — nothing else changes.

Theme updates come from the gems, not from git: `bundle update`, then commit the
new `Gemfile.lock`. Dependabot (`.github/dependabot.yml`) opens those as monthly
pull requests instead — the `al_folio_*` gems are pinned to exact versions, so
nothing else would ever tell you a new one exists. Each PR is built by the Check
workflow before you merge it.

## Keeping the CV in sync

`assets/pdf/dahai_yu_cv.pdf` is the authority for CV content: `_data/cv.yml` and
`_pages/about.md` were reconciled against it, not the other way round. Whenever
the PDF is regenerated, re-check the email, the degree names, the awards, the
internship, and the publication list against it.

Publication metadata is verified against Crossref, [DBLP `31/2647-2`](https://dblp.org/pid/31/2647-2.html),
and the arXiv API. When a preprint gets published, edit the existing entry (add
`doi`/`html`, keep `arxiv`) rather than adding a second one. Dates in `_news/`
match arXiv submission / proceedings dates where known; acceptance announcements
use the 1st of the month.
