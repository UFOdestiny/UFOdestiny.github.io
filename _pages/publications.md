---
layout: page
permalink: /publications/
title: Publications
description: In reverse chronological order. Also on <a href='https://dblp.org/pid/31/2647-2.html'>DBLP</a>.
nav: true
nav_order: 1
---

{% include bib_search.liquid %}

{% comment %}
  jekyll-scholar renders each year group as a bare `<h2 class="bibliography">2026</h2>`
  with no id, and offers no config for one. So capture the bibliography, give the
  headings ids with the `regex_replace` filter (jekyll-regex-replace), then read the
  year list back out of the same string — splitting on the id marker leaves each year
  at the start of a chunk. That keeps the nav below in sync with the .bib for free,
  and the anchors are real HTML, so /publications/#2025 works without JavaScript.
{% endcomment %}
{% capture bibliography %}{% bibliography %}{% endcapture %}
{% assign bibliography = bibliography | regex_replace: '<h2 class="bibliography">(\d+)</h2>', '<h2 class="bibliography" id="\1">\1</h2>' %}
{% assign year_chunks = bibliography | split: '<h2 class="bibliography" id="' %}

<style>
  /* Local to this page: the year nav and the scroll offset its anchors need, so
     `navbar_fixed: true` does not park a heading underneath the navbar. */
  .publication-years {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
  }
  .publication-years a {
    border: 1px solid var(--global-divider-color);
    border-radius: 4px;
    padding: 0.1rem 0.55rem;
    font-size: 0.9rem;
    color: var(--global-text-color-light);
  }
  .publication-years a:hover {
    border-color: var(--global-theme-color);
    color: var(--global-theme-color);
  }
  .publications h2.bibliography,
  .publications li .row > div[id] {
    scroll-margin-top: 5rem;
  }
</style>

<nav class="publication-years" aria-label="Jump to year">
  {% for chunk in year_chunks offset: 1 %}
    {% assign year = chunk | split: '"' | first %}
    <a href="#{{ year }}">{{ year }}</a>
  {% endfor %}
</nav>

<div class="publications">

{{ bibliography }}

</div>
